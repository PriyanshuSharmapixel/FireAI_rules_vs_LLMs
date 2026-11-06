"""Opt-in Gemini experiments. Missing/failed calls are failures, never mocks.

python live_experiments.py --max-calls 300 --tax-limit 30 --b-rows 120
Full tax-suite evaluation requires --tax-limit 2296 and an adequate call quota.
Free-tier availability and model names must be checked in the applicant account.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import random
import statistics
import time
from common import Gemini,token_cost
from project_a.model import TaxInput
from project_a import llm_runtime,compiled_rules
from project_a.parser import parse
from project_b.detectors import Baseline,PROBLEMS,llm_detect,normalize
from project_b.benchmark import partition,structurally_valid,metrics
from project_b.inject import inject
from project_b.hybrid import run as hybrid_run


def run(max_calls=300,tax_limit=30,b_rows=120):
    out=Path('results/live');out.mkdir(parents=True,exist_ok=True)
    run_id=str(time.time_ns())
    client=Gemini(max_calls=max_calls,log_path=str(out/('usage-'+run_id+'.jsonl')))
    cases=json.loads(Path('project_a/fixtures/tax_cases.json').read_text())
    selected=random.Random(503).sample(cases,min(tax_limit,len(cases)))
    required=len(selected)*2+20+50+2+(1+len(PROBLEMS))*((b_rows+39)//40)+2*((max(1,round(b_rows*.05))+b_rows+39)//40-(b_rows+39)//40)+1
    if max_calls<required: raise ValueError(f'Budget needs at least {required} calls for this plan; lower limits or explicitly raise --max-calls')
    result={'run_id':run_id,'model':client.model,'max_calls':max_calls,'tax':[],'repeat':[],'parser':[],'compilation':[],
            'b':[],'b_scope':'One seed, 5% corruption, bounded subsample; provisional, not full offline benchmark coverage.'}
    def checkpoint():
        if client.log_path.exists():
            usage=[json.loads(line) for line in client.log_path.read_text().splitlines() if line]
            costs=[token_cost(item.get('usage',{})) for item in usage if item.get('ok')]
            result['usage']={'log':str(client.log_path),'attempted':len(usage),'successful':sum(item.get('ok',False) for item in usage),
                             'prompt_tokens':sum(item.get('usage',{}).get('promptTokenCount',0) for item in usage),
                             'output_tokens':sum(item.get('usage',{}).get('candidatesTokenCount',0) for item in usage),
                             'thinking_tokens':sum(item.get('usage',{}).get('thoughtsTokenCount',0) for item in usage),
                             'estimated_successful_paid_equivalent_usd':sum(costs) if costs and all(c is not None for c in costs) else None,
                             'note':'Rates must be explicitly configured; failed-call usage is unknown; this is not an observed bill.'}
        (out/'summary.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    for c in selected:
        for regime in ['old','new']:
            entry={'case_id':c['id'],'regime':regime,'expected':c['expected'][regime]['tax']}
            tick=time.perf_counter()
            try:
                answer=llm_runtime.calculate(TaxInput(**c['input']),regime,client)
                entry.update(answer=answer,correct=answer['tax']==entry['expected'],ok=True)
            except Exception as e: entry.update(ok=False,error_type=type(e).__name__,correct=False)
            entry['seconds']=time.perf_counter()-tick
            result['tax'].append(entry);checkpoint()
    person=TaxInput(1500000,fy='2024-25')
    for regime in ['old','new']:
        outputs=[];failures=[]
        for repeat in range(10):
            try: outputs.append(llm_runtime.calculate(person,regime,client))
            except Exception as e: failures.append(type(e).__name__)
        result['repeat'].append({'input':person.to_dict(),'regime':regime,'requested_repetitions':10,'successful_repetitions':len(outputs),
                                 'distinct_taxes':len({x['tax'] for x in outputs}),'distinct_full_outputs':len({json.dumps(x,sort_keys=True) for x in outputs}),
                                 'failures':failures,'outputs':outputs});checkpoint()
    for item in json.loads(Path('project_a/fixtures/descriptions.json').read_text()):
        entry={'id':item['id'],'expected_status':item['expected_status']}
        try:
            extracted=parse(item['text'],client)
            entry.update(result=extracted,correct_status=extracted['status']==item['expected_status'])
            if item.get('expected_values'):
                entry['correct_values']=all(str(extracted.get('values',{}).get(k))==str(v) for k,v in item['expected_values'].items())
        except Exception as e: entry.update(error_type=type(e).__name__,correct_status=False)
        result['parser'].append(entry);checkpoint()
    for fy in ['2024-25','2025-26']:
        tick=time.perf_counter()
        try: entry=compiled_rules.compile_candidate(fy,client)
        except Exception as e: entry={'error_type':type(e).__name__}
        entry.update(fy=fy,seconds=time.perf_counter()-tick)
        result['compilation'].append(entry);checkpoint()
    raw=json.loads(Path('data/nyc311_2023.json').read_text())
    training,_,heldout=partition(normalize(raw));baseline=Baseline(training)
    clean=random.Random(301).sample(structurally_valid(heldout),b_rows)
    clean_alerts=None
    try: clean_alerts=llm_detect(clean,baseline,client)
    except Exception as e: result['b_clean_error']=type(e).__name__
    for problem in PROBLEMS:
        batch,truth,metadata=inject(clean,problem,.05,301)
        tick=time.perf_counter();entry={'problem':problem,'metadata':metadata,'clean_n':len(clean)}
        try:
            alerts=llm_detect(batch,baseline,client)
            predicted={i for a in alerts if a['problem']==problem for i in a['rows']}
            clean_ids=None if clean_alerts is None else {i for a in clean_alerts if a['problem']==problem for i in a['rows']}
            entry.update(metrics(predicted,truth,len(batch)))
            entry.update(alerts=alerts,clean_proxy_flagged=None if clean_ids is None else len(clean_ids),ok=True)
        except Exception as e: entry.update(error_type=type(e).__name__,ok=False)
        entry['seconds']=time.perf_counter()-tick
        result['b'].append(entry);checkpoint()
    try:
        choices=json.loads(Path('results/benchmark_b.json').read_text())['choices']
        result['hybrid']=hybrid_run(clean,baseline,choices,client,review_cap=40)
    except Exception as e: result['hybrid']={'error_type':type(e).__name__}
    result['calls_attempted']=client.calls
    result['full_tax_suite_evaluated']=len(selected)==len(cases)
    result['note']='Compilation candidates are NOT promoted automatically. Live outputs contain LLM claims, not verified legal answers.'
    checkpoint()
    print('Live evidence saved; run python reproduce.py --replay to refresh reports.')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--max-calls',type=int,default=300)
    p.add_argument('--tax-limit',type=int,default=30)
    p.add_argument('--b-rows',type=int,default=120)
    a=p.parse_args()
    if a.b_rows<40 or a.tax_limit<1: p.error('b-rows must be >=40 and tax-limit positive')
    run(a.max_calls,a.tax_limit,a.b_rows)
