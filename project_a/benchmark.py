"""Measured accuracy, traces, repetitions, latency and a labelled change simulation."""
import csv
from dataclasses import replace
import json
from pathlib import Path
import statistics
import time
from .model import TaxInput
from . import handwritten,compiled_rules
from .parser import parse

FIXTURES=Path(__file__).parent/'fixtures'


def official_validation(cases):
    by_id={c['id']:c for c in cases}
    checks=list(csv.DictReader((FIXTURES/'official_checks.csv').open()))
    verified=[]; mismatches=[];invalid=[]
    for row in checks:
        if row['status']!='VERIFIED': continue
        try:
            tax=int(row['official_tax'])
            if not row['checked_utc'] or not row['evidence_path'] or not Path(row['evidence_path']).is_file():
                raise ValueError('Missing date or evidence file')
            expected=by_id[row['case_id']]['expected'][row['regime']]['tax']
            verified.append(row)
            if tax!=expected: mismatches.append({'case_id':row['case_id'],'regime':row['regime'],'official':tax,'oracle':expected})
        except (KeyError,ValueError): invalid.append(row['case_id'])
    pairs={(r['case_id'],r['regime']) for r in verified}
    dual={c for c,r in pairs if (c,'old') in pairs and (c,'new') in pairs}
    return {'verified_regime_checks':len(verified),'distinct_cases_both_regimes':len(dual),'required_cases_both_regimes':30,
            'mismatches':mismatches,'invalid_evidence':invalid,'passes_gate':len(dual)>=30 and not mismatches and not invalid}


def law_change(cases):
    changed=[c for c in cases if c['input']['fy']=='2025-26']
    records=[]
    for name,module in [('handwritten',handwritten),('compiled_codex',compiled_rules)]:
        start=time.perf_counter();stale_wrong=0;updated_wrong=0
        for case in changed:
            person=TaxInput(**case['input'])
            stale=replace(person,fy='2024-25')
            for regime in ['old','new']:
                stale_wrong+=module.calculate(stale,regime)['tax']!=case['expected'][regime]['tax']
                updated_wrong+=module.calculate(person,regime)['tax']!=case['expected'][regime]['tax']
        records.append({'implementation':name,'evaluated_outputs':len(changed)*2,'stale_year_silent_wrong_answers':stale_wrong,
                        'updated_wrong_answers':updated_wrong,'regression_seconds':time.perf_counter()-start,
                        'human_update_time_seconds':None,'note':'Simulated stale-year routing, not a contemporaneously timed human implementation migration.'})
    return records


def benchmark():
    cases=json.loads((FIXTURES/'tax_cases.json').read_text())
    measurements=[]
    for name,module in [('handwritten',handwritten),('compiled_codex',compiled_rules)]:
        errors=[];latencies=[];trace_complete=0
        start=time.perf_counter()
        for case in cases:
            person=TaxInput(**case['input'])
            for regime in ['old','new']:
                tick=time.perf_counter();answer=module.calculate(person,regime);latencies.append(time.perf_counter()-tick)
                if answer['tax']!=case['expected'][regime]['tax']: errors.append({'case':case['id'],'regime':regime,'got':answer['tax'],'expected':case['expected'][regime]['tax']})
                trace_complete+=all(x.get('clause') for x in answer['trace'])
        elapsed=time.perf_counter()-start
        # Repeated ACTUAL executions, not repeated reads from a cached answer.
        selected=[cases[i] for i in range(0,len(cases),max(1,len(cases)//30))][:30]
        differing=0
        for c in selected:
            person=TaxInput(**c['input'])
            for regime in ['old','new']:
                outputs=[json.dumps(module.calculate(person,regime),sort_keys=True) for _ in range(10)]
                differing+=len(set(outputs))>1
        measurements.append({'implementation':name,'taxpayer_cases':len(cases),'evaluated_outputs':len(cases)*2,
                             'correct_outputs':len(cases)*2-len(errors),'accuracy':1-len(errors)/(len(cases)*2),
                             'errors':errors,'median_ms':statistics.median(latencies)*1000,'p95_ms':sorted(latencies)[int(.95*(len(latencies)-1))]*1000,
                             'total_seconds':elapsed,'trace_nonempty_clause_outputs':trace_complete,
                             'trace_legal_review':'Clause labels and arithmetic trace present; source correctness not independently audited',
                             'repetition_inputs':len(selected)*2,'repetitions_per_input':10,'differing_inputs':differing,
                             'paid_api_usd_per_1000_requests':0,'compute_cost':'Not monetized; execution-host timings, not laptop timings'})
    descriptions=json.loads((FIXTURES/'descriptions.json').read_text())
    parser_results=[{'id':x['id'],'expected':x['expected_status'],'actual':parse(x['text'])['status']} for x in descriptions]
    result={'measurements':measurements,'parser':{'cases':len(descriptions),'correct_status':sum(x['actual']==x['expected'] for x in parser_results),
              'details':parser_results,'note':'Conservative rule-parser readiness/clarification check; not Gemini extraction accuracy.'},
            'official_validation':official_validation(cases),'law_change_simulation':law_change(cases),
            'llm_runtime_status':'NOT_RUN: missing Gemini credentials/model',
            'compiled_origin':'Codex generated the reviewed JSON configuration; Gemini compilation path is implemented but has not run.',
            'fixture_provenance':'Frozen independently coded piecewise-formula oracle. Not official-calculator ground truth.'}
    out=Path('results');out.mkdir(exist_ok=True)
    (out/'benchmark_a.json').write_text(json.dumps(result,indent=2)+'\n')
    print('A:',len(cases),'cases, two regimes, two deterministic implementations')
    return result


if __name__=='__main__': benchmark()
