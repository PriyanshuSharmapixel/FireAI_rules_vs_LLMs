"""A: handwritten rules. Decimal arithmetic; trace every calculation stage.

Authority and scope are recorded in SOURCES.md. The calculator is not a tax
filing product; the independent official-calculator validation remains a gate.
"""
from decimal import Decimal
from .model import TaxInput, money, statutory_round

D = Decimal


def slabs_for(person, regime):
    if regime == 'old':
        exemption = 500000 if person.resident and person.age >= 80 else 300000 if person.resident and person.age >= 60 else 250000
        return [(exemption, '0'), (500000, '.05'), (1000000, '.20'), (None, '.30')]
    if person.fy == '2024-25':
        return [(300000, '0'), (700000, '.05'), (1000000, '.10'), (1200000, '.15'), (1500000, '.20'), (None, '.30')]
    return [(400000, '0'), (800000, '.05'), (1200000, '.10'), (1600000, '.15'), (2000000, '.20'), (2400000, '.25'), (None, '.30')]


def progressive(income, slabs):
    result, lower = D(0), D(0)
    for upper, rate in slabs:
        end = income if upper is None else min(income, D(upper))
        result += max(D(0), end - lower) * D(rate)
        if upper is None or income <= upper:
            break
        lower = D(upper)
    return result


def deductions(person, regime):
    salary = money(person.gross_salary)
    std = min(salary, D(50000 if regime == 'old' else 75000))
    result = [('standard_deduction', std, '16(ia)')]
    if regime == 'new':
        return result
    hra = max(D(0), min(money(person.hra_received), money(person.rent_paid) - money(person.hra_salary) / 10,
                         money(person.hra_salary) * D('.5' if person.metro else '.4')))
    result += [('hra_exemption', hra, '10(13A), Rule 2A'),
               ('80c', min(money(person.deduction_80c), D(150000)), '80C, 80CCE'),
               ('nps', min(money(person.nps_80ccd1b), D(50000)), '80CCD(1B)')]
    # Combined preventive check-up sublimit is 5,000 across both groups.
    remaining = D(5000)
    for name, premium, checkup, expense, senior in (
        ('80d_self', person.health_self, person.checkup_self, person.medical_self_uninsured, person.self_group_senior or (person.resident and person.age >= 60)),
        ('80d_parents', person.health_parents, person.checkup_parents, person.medical_parents_uninsured, person.parents_senior)):
        cap = D(50000 if senior else 25000)
        allowed_checkup = min(money(checkup), remaining)
        remaining -= allowed_checkup
        result.append((name, min(cap, money(premium) + money(expense) + allowed_checkup), '80D'))
    result.append(('home_interest', min(money(person.home_interest), D(200000 if person.home_eligible_2l else 30000)), '24(b), 71(3A)'))
    return result


def calculate(person: TaxInput, regime='new'):
    if regime not in ('old', 'new'):
        raise ValueError('regime must be old or new')
    trace = []
    salary = money(person.gross_salary)
    items = deductions(person, regime)
    # HRA and salary deduction cannot make salary income negative; Chapter VIA
    # deductions cannot exceed remaining positive gross total income.
    salary_deductions = sum((v for k, v, _ in items if k in ('standard_deduction', 'hra_exemption')), D(0))
    rest = sum((v for k, v, _ in items if k not in ('standard_deduction', 'hra_exemption')), D(0))
    unrounded = max(D(0), max(D(0), salary - salary_deductions) - rest)
    income = D(statutory_round(unrounded))
    for name, amount, clause in items:
        trace.append({'step': name, 'amount': str(amount), 'clause': clause})
    trace.append({'step': 'taxable_income', 'amount': str(income), 'clause': '288A', 'before_rounding': str(unrounded)})
    slabs = slabs_for(person, regime)
    base = progressive(income, slabs)
    trace.append({'step': 'slab_tax', 'amount': str(base), 'clause': '115BAC(1A)' if regime == 'new' else 'Finance Act First Schedule Part III, Paragraph A', 'slabs': slabs})
    rebate = marginal_rebate = D(0)
    limit = D(500000 if regime == 'old' else 700000 if person.fy == '2024-25' else 1200000)
    if person.resident:
        if income <= limit:
            rebate = min(base, D(12500 if regime == 'old' else 25000 if person.fy == '2024-25' else 60000))
        elif regime == 'new':
            marginal_rebate = max(D(0), base - (income - limit))
    net = base - rebate - marginal_rebate
    trace += [{'step': 'rebate', 'amount': str(rebate), 'clause': '87A'},
              {'step': 'rebate_marginal_relief', 'amount': str(marginal_rebate), 'clause': '87A proviso (b)'}]
    schedule = [(5000000, D('.10')), (10000000, D('.15')), (20000000, D('.25'))]
    if regime == 'old':
        schedule.append((50000000, D('.37')))
    surcharge = relief = D(0)
    prior_rate = D(0)
    for threshold, rate in schedule:
        if income > threshold:
            surcharge = net * rate
            threshold_total = progressive(D(threshold), slabs) * (1 + prior_rate)
            relief = max(D(0), net + surcharge - threshold_total - (income - threshold))
        prior_rate = rate
    pretax_cess = net + surcharge - relief
    cess = pretax_cess * D('.04')
    total = pretax_cess + cess
    trace += [{'step': 'surcharge', 'amount': str(surcharge), 'clause': 'Finance Act First Schedule surcharge'},
              {'step': 'surcharge_marginal_relief', 'amount': str(relief), 'clause': 'Finance Act First Schedule marginal relief'},
              {'step': 'cess', 'amount': str(cess), 'clause': 'Finance Act health and education cess 4%'},
              {'step': 'payable', 'amount': str(statutory_round(total)), 'clause': '288B', 'before_rounding': str(total)}]
    return {'fy': person.fy, 'regime': regime, 'taxable_income': int(income), 'tax': statutory_round(total),
            'tax_before_final_rounding': str(total), 'trace': trace}


def compare(person):
    old, new = calculate(person, 'old'), calculate(person, 'new')
    return {'old': old, 'new': new, 'recommended': 'tie' if old['tax'] == new['tax'] else 'old' if old['tax'] < new['tax'] else 'new',
            'saving': abs(old['tax'] - new['tax'])}
