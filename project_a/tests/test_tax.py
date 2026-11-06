import json
import unittest
from pathlib import Path
from project_a.model import TaxInput, statutory_round
from project_a import handwritten, compiled_rules
from project_a.parser import parse

FIXTURES=Path(__file__).parents[1]/'fixtures'


class TaxTests(unittest.TestCase):
    def test_independent_frozen_expectations(self):
        cases=json.loads((FIXTURES/'tax_cases.json').read_text())
        self.assertGreaterEqual(len(cases),200)
        for case in cases:
            person=TaxInput(**case['input'])
            for regime in ('old','new'):
                for engine in (handwritten,compiled_rules):
                    with self.subTest(case=case['id'],regime=regime,engine=engine.__name__):
                        result=engine.calculate(person,regime)
                        self.assertEqual(result['tax'],case['expected'][regime]['tax'])
                        self.assertEqual(result['taxable_income'],case['expected'][regime]['taxable_income'])
                        self.assertTrue(all(x['clause'] for x in result['trace']))

    def test_known_examples(self):
        self.assertEqual(handwritten.calculate(TaxInput(775000),'new')['tax'],0)
        self.assertEqual(handwritten.calculate(TaxInput(1275000,fy='2025-26'),'new')['tax'],0)
        self.assertEqual(handwritten.calculate(TaxInput(1500000),'new')['tax'],130000)
        self.assertEqual(handwritten.calculate(TaxInput(1500000,fy='2025-26'),'new')['tax'],97500)
        self.assertEqual(handwritten.calculate(TaxInput(550000),'old')['tax'],0)
        self.assertGreater(handwritten.calculate(TaxInput(550010),'old')['tax'],12500)

    def test_rounding_discards_paise(self):
        for v,want in [('14.99',10),('15.00',20),('24.99',20),('25',30)]:
            self.assertEqual(statutory_round(v),want)

    def test_rebate_marginal_relief(self):
        for fy,limit in [('2024-25',700000),('2025-26',1200000)]:
            p=TaxInput(limit+75010,fy=fy)
            result=handwritten.calculate(p,'new')
            self.assertEqual(result['tax'],10)
            self.assertGreater(float(next(x['amount'] for x in result['trace'] if x['step']=='rebate_marginal_relief')),0)

    def test_surcharge_marginal_relief(self):
        for fy in ['2024-25','2025-26']:
            for regime,sd in [('old',50000),('new',75000)]:
                for boundary in [5000000,10000000,20000000]+([50000000] if regime=='old' else []):
                    at=handwritten.calculate(TaxInput(boundary+sd,fy=fy),regime)['tax']
                    above=handwritten.calculate(TaxInput(boundary+sd+10,fy=fy),regime)['tax']
                    self.assertLessEqual(above-at,20)

    def test_parser_fixtures(self):
        fixtures=json.loads((FIXTURES/'descriptions.json').read_text())
        self.assertEqual(len(fixtures),50)
        for item in fixtures:
            with self.subTest(description=item['id']):
                result=parse(item['text'])
                self.assertEqual(result['status'],item['expected_status'])
                for k,v in item.get('expected_values',{}).items():
                    self.assertEqual(str(result['values'][k]),str(v))

    def test_senior_self_insurance_uses_taxpayer_age(self):
        for engine in (handwritten,compiled_rules):
            result=engine.calculate(TaxInput(1500000,age=65,health_self=50000),'old')
            item=next(x for x in result['trace'] if x['step'] in ('80d_self','health_self'))
            self.assertEqual(float(item['amount']),50000)

    def test_reject_invalid(self):
        for opts in [{'gross_salary':-1},{'gross_salary':'NaN'},{'gross_salary':True},{'gross_salary':1,'resident':'yes'},
                     {'gross_salary':100,'hra_received':200},{'gross_salary':100,'age':60.5},
                     {'gross_salary':100,'medical_self_uninsured':100,'self_group_senior':False}]:
            with self.subTest(opts=opts),self.assertRaises(ValueError):
                TaxInput(**opts)

    def test_mismatched_rule_version(self):
        with self.assertRaises(ValueError):
            compiled_rules.load('2024-25',Path(__file__).parents[1]/'rules'/'2025-26.json')
