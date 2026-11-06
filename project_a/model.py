"""Validated structured inputs. All currency fields are annual INR.

Direct Python callers opt into documented zero defaults. The language parser must
obtain an explicit no-other-claims confirmation before it can apply those defaults.
No PAN, bank account or real taxpayer identity is required.
"""
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_DOWN


def money(value):
    if isinstance(value, bool):
        raise ValueError('Boolean is not a money amount')
    result = Decimal(str(value))
    if not result.is_finite() or result < 0:
        raise ValueError('Amounts must be finite and nonnegative')
    return result


def statutory_round(value):
    # 288A/288B: ignore paise first, then nearest ten, ties upward.
    integer = int(Decimal(str(value)).quantize(Decimal('1'), rounding=ROUND_DOWN))
    return ((integer + 5) // 10) * 10


@dataclass(frozen=True)
class TaxInput:
    gross_salary: int | float | str
    fy: str = '2024-25'
    age: int = 30
    resident: bool = True
    hra_salary: int | float | str = 0  # basic + eligible DA + eligible commission
    hra_received: int | float | str = 0
    rent_paid: int | float | str = 0
    metro: bool = False  # Only Delhi, Mumbai, Kolkata, Chennai for HRA
    deduction_80c: int | float | str = 0
    nps_80ccd1b: int | float | str = 0  # exclude amounts already claimed in 80C
    health_self: int | float | str = 0  # eligible non-cash insurance premium
    health_parents: int | float | str = 0
    self_group_senior: bool = False  # eligible resident senior in insured group
    parents_senior: bool = False
    checkup_self: int | float | str = 0
    checkup_parents: int | float | str = 0
    medical_self_uninsured: int | float | str = 0
    medical_parents_uninsured: int | float | str = 0
    home_interest: int | float | str = 0
    home_eligible_2l: bool = False  # confirmed acquisition/construction conditions

    def __post_init__(self):
        if self.fy not in ('2024-25', '2025-26'):
            raise ValueError('Supported FY: 2024-25 or 2025-26')
        if type(self.age) is not int or not 0 <= self.age <= 120:
            raise ValueError('Age must be an integer from 0 to 120')
        booleans = ('resident', 'metro', 'self_group_senior', 'parents_senior', 'home_eligible_2l')
        for key in booleans:
            if type(getattr(self, key)) is not bool:
                raise ValueError(key + ' must be a boolean')
        for key in asdict(self):
            if key not in booleans + ('fy', 'age'):
                money(getattr(self, key))
        if money(self.hra_salary) + money(self.hra_received) > money(self.gross_salary):
            raise ValueError('HRA salary plus HRA received exceeds gross salary')
        for premium, expense, senior in ((self.health_self, self.medical_self_uninsured, self.self_group_senior),
                                          (self.health_parents, self.medical_parents_uninsured, self.parents_senior)):
            if money(expense) and (money(premium) or not senior):
                raise ValueError('Medical expenditure input requires an uninsured eligible senior group')

    def to_dict(self):
        return asdict(self)
