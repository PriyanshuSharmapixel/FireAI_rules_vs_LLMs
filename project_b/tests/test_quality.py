import unittest
from copy import deepcopy
from project_b.detectors import Baseline,PROBLEMS,rule_detect,statistical_detect
from project_b.inject import inject
from project_b.hybrid import run


def rows():
    return [{'unique_key':str(i),'created_date':f'2023-01-{i%28+1:02d}T12:00:00.000','closed_date':f'2023-01-{i%28+1:02d}T13:00:00.000',
             'agency':'DEP' if i%2 else 'NYPD','complaint_type':'Water' if i%2 else 'Noise','descriptor':'Leak' if i%2 else 'Loud music',
             'status':'Closed','resolution_description':'The agency completed its response.',
             'incident_zip':'10001' if i%2 else '11201','borough':'MANHATTAN' if i%2 else 'BROOKLYN',
             'latitude':40.75 if i%2 else 40.69,'longitude':-73.99 if i%2 else -73.98} for i in range(120)]


class QualityTests(unittest.TestCase):
    def test_injector_reproducible_and_nonmutating(self):
        original=rows();copy=deepcopy(original)
        for p in PROBLEMS:
            with self.subTest(problem=p):
                first=inject(original,p,.15,7)
                self.assertEqual(first,inject(original,p,.15,7))
                self.assertTrue(first[1])
                self.assertTrue(all(0<=i<len(first[0]) for i in first[1]))
        self.assertEqual(original,copy)

    def test_structural_corruptions_caught(self):
        clean=rows();base=Baseline(clean)
        for p in ['schema','type_change','date_format','swapped_coordinates','exact_duplicates','reversed_dates']:
            corrupt,truth,_=inject(clean,p,.15,42)
            for detector in [rule_detect,statistical_detect]:
                with self.subTest(problem=p,detector=detector.__name__):
                    predicted={i for a in detector(corrupt,base,only=[p]) for i in a['rows']}
                    self.assertTrue(truth<=predicted)

    def test_semantic_corruptions_and_false_alarms(self):
        clean=rows();base=Baseline(clean)
        for p in ['zip_borough','complaint_descriptor','resolution_status','personal_data']:
            corrupt,truth,_=inject(clean,p,.15,42)
            predicted={i for a in rule_detect(corrupt,base,only=[p]) for i in a['rows']}
            self.assertTrue(truth<=predicted,p)
            self.assertEqual(rule_detect(clean,base,only=[p]),[],p)

    def test_optional_nulls_are_not_schema_failures(self):
        clean=rows();base=Baseline(clean)
        clean[0]['closed_date']=None
        clean[0]['descriptor']=None
        self.assertEqual(rule_detect(clean,base,only=['schema','date_format','reversed_dates']),[])

    def test_zero_corruption_invalid(self):
        with self.assertRaises(ValueError): inject(rows(),'schema',0)

    def test_hybrid_never_needs_llm_without_client(self):
        clean=rows();base=Baseline(clean)
        corrupt,truth,_=inject(clean,'reversed_dates',.1,42)
        result=run(corrupt,base,{p:'rule' for p in PROBLEMS})
        self.assertFalse(result['review']['enabled'])
        self.assertTrue(truth<={i for a in result['alerts'] if a['problem']=='reversed_dates' for i in a['rows']})
