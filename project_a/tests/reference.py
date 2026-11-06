"""Independent test oracle: piecewise closed-form tax, integer paise arithmetic.

Does not import either production engine or production rule configuration.
Not an official-calculator oracle. Correlated legal interpretation remains a risk.
"""
from decimal import Decimal


def rounded(x):
    return ((int(x)+5)//10)*10


def expected(person, regime):
    p=person.to_dict()
    amount=lambda key: Decimal(str(p[key]))
    gross=amount('gross_salary')
    standard=min(gross,50000 if regime=='old' else 75000)
    exempt=other=Decimal(0)
    if regime=='old':
        exempt=max(Decimal(0),min(amount('hra_received'),amount('rent_paid')-amount('hra_salary')/10,amount('hra_salary')*(Decimal('0.5') if p['metro'] else Decimal('0.4'))))
        other=min(amount('deduction_80c'),150000)+min(amount('nps_80ccd1b'),50000)
        preventive=min(amount('checkup_self'),5000)
        other+=min(amount('health_self')+amount('medical_self_uninsured')+preventive,50000 if p['self_group_senior'] or (p['resident'] and p['age']>=60) else 25000)
        other+=min(amount('health_parents')+amount('medical_parents_uninsured')+min(amount('checkup_parents'),5000-preventive),50000 if p['parents_senior'] else 25000)
        other+=min(amount('home_interest'),200000 if p['home_eligible_2l'] else 30000)
    x=rounded(max(0,max(0,gross-standard-exempt)-other))
    def base(y):
        # Return tax in paise, avoiding production's progressive-band loop.
        if regime=='old':
            exemption=500000 if p['resident'] and p['age']>=80 else 300000 if p['resident'] and p['age']>=60 else 250000
            if y<=exemption: return 0
            if y<=500000: return (y-exemption)*5
            at_five=(500000-exemption)*5
            if y<=1000000: return at_five+(y-500000)*20
            return at_five+10000000+(y-1000000)*30
        if p['fy']=='2024-25':
            if y<=300000: return 0
            if y<=700000: return (y-300000)*5
            if y<=1000000: return 2000000+(y-700000)*10
            if y<=1200000: return 5000000+(y-1000000)*15
            if y<=1500000: return 8000000+(y-1200000)*20
            return 14000000+(y-1500000)*30
        if y<=400000: return 0
        if y<=800000: return (y-400000)*5
        if y<=1200000: return 2000000+(y-800000)*10
        if y<=1600000: return 6000000+(y-1200000)*15
        if y<=2000000: return 12000000+(y-1600000)*20
        if y<=2400000: return 20000000+(y-2000000)*25
        return 30000000+(y-2400000)*30
    tax=base(x)
    boundary=500000 if regime=='old' else 700000 if p['fy']=='2024-25' else 1200000
    if p['resident']:
        if x<=boundary:
            tax=max(0,tax-(1250000 if regime=='old' else 2500000 if p['fy']=='2024-25' else 6000000))
        elif regime=='new':
            tax=min(tax,(x-boundary)*100)
    tiers=[(5000000,10),(10000000,15),(20000000,25)] + ([(50000000,37)] if regime=='old' else [])
    chosen=[(t,r) for t,r in tiers if x>t]
    combined=Decimal(tax)
    if chosen:
        threshold,rate=chosen[-1]
        prior=chosen[-2][1] if len(chosen)>1 else 0
        combined=min(Decimal(tax)*(100+rate)/100,Decimal(base(threshold))*(100+prior)/100+(x-threshold)*100)
    payable_paise=combined*104/100
    return {'tax':rounded(payable_paise/100),'taxable_income':x}
