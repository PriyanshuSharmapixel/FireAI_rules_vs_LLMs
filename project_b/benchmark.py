"""Isolated corruptions, disjoint train/validation/test, honest proxy-clean FPR."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import random
import time
from .detectors import Baseline, PROBLEMS, normalize, rule_detect, statistical_detect, date, numeric, canonical
from .inject import inject
from .profile import profile
from .hybrid import run as hybrid_run


def partition(rows):
    groups=[[],[],[]]
    for row in rows:
        bucket=int(hashlib.sha256(str(row.get('unique_key')).encode()).hexdigest()[:8],16)%10
        groups[0 if bucket<6 else 1 if bucket<8 else 2].append(row)
    return groups


def structurally_valid(rows):
    # Explicit selection contract, not a semantic ground-truth label.
    good=[]
    seen=set()
    for r in rows:
        a,b=date(r.get('created_date')),date(r.get('closed_date'))
        if not a or b and b<a: continue
        if r.get('closed_date') and not b: continue
        lat,lon=r.get('latitude'),r.get('longitude')
        if not numeric(lat) or not numeric(lon) or not (40<=lat<=41.5 and -75<=lon<=-73): continue
        if not r.get('descriptor') or not r.get('incident_zip') or not r.get('borough'): continue
        key=canonical(r)
        if key in seen: continue
        seen.add(key);good.append(r)
    return good


def metrics(ids,truth,n):
    tp=len(ids & truth)
    return {'tp':tp,'fn':len(truth-ids),'fp':len(ids-truth),'tn':n-len(truth|ids)}


def evaluate(pool,baseline,rows_per_batch=240,seeds=(17,28,43),rates=(.01,.05,.15),choices=None):
    records=[]
    funcs={'rule':rule_detect,'statistical':statistical_detect}
    if choices:
        funcs={'hybrid':lambda rows,base,only:hybrid_run(rows,base,choices)['alerts']}
    for seed in seeds:
        rng=random.Random(seed)
        clean=rng.sample(pool,min(len(pool),rows_per_batch))
        for problem in PROBLEMS:
            for family,detector in funcs.items():
                start=time.perf_counter()
                clean_alerts=detector(clean,baseline,only=[problem])
                clean_seconds=time.perf_counter()-start
                clean_ids={i for a in clean_alerts if a['problem']==problem for i in a['rows']}
                for rate in rates:
                    corrupt,truth,meta=inject(clean,problem,rate,seed)
                    if not truth: raise RuntimeError('No eligible corruption for '+problem)
                    start=time.perf_counter()
                    found=detector(corrupt,baseline,only=[problem])
                    seconds=time.perf_counter()-start
                    ids={i for a in found if a['problem']==problem for i in a['rows']}
                    records.append({'problem':problem,'family':family,'seed':seed,'rate':rate,'metadata':meta,
                                    **metrics(ids,truth,len(corrupt)),'clean_proxy_flagged':len(clean_ids),'clean_proxy_n':len(clean),
                                    'clean_proxy_batch_alert':bool(clean_ids),'corrupt_batch_detected':bool(ids & truth),
                                    'rows':len(corrupt),'seconds':seconds,'clean_seconds':clean_seconds,
                                    'llm_calls':0,'cost_usd_per_million':0,
                                    'alerts_with_reason':sum(bool(a.get('reason')) for a in found),'alerts':len(found)})
    return records


def aggregate(records):
    groups=defaultdict(list)
    for r in records: groups[(r['problem'],r['family'])].append(r)
    output=[]
    for (problem,family),items in sorted(groups.items()):
        tp,fn,fp,tn=[sum(x[k] for x in items) for k in ['tp','fn','fp','tn']]
        # Unmodified batches repeat across rates: deduplicate those FPR denominators.
        clean={x['seed']:x for x in items}.values()
        clean_n=sum(x['clean_proxy_n'] for x in clean)
        clean_fp=sum(x['clean_proxy_flagged'] for x in clean)
        seconds=sum(x['seconds'] for x in items)
        total_rows=sum(x['rows'] for x in items)
        output.append({'problem':problem,'family':family,'tp':tp,'fn':fn,'fp':fp,'tn':tn,
                       'detection_rate':tp/max(1,tp+fn),'clean_proxy_row_flag_rate':clean_fp/max(1,clean_n),
                       'clean_proxy_batch_flag_rate':sum(x['clean_proxy_batch_alert'] for x in clean)/max(1,len(clean)),
                       'corrupt_batch_detection_rate':sum(x['corrupt_batch_detected'] for x in items)/len(items),
                       'rows_per_second':total_rows/max(seconds,1e-9),'seconds':seconds,'trials':len(items),
                       'paid_api_usd_per_million':0,'compute_cost':'not monetized; throughput measured on execution host',
                       'explained_alert_fraction':sum(x['alerts_with_reason'] for x in items)/max(1,sum(x['alerts'] for x in items))})
    return output


def choose(validation):
    choices={}
    for problem in PROBLEMS:
        items=[x for x in validation if x['problem']==problem]
        # Fixed score chosen before held-out evaluation. Prefer rule on a tie.
        best=max(items,key=lambda x:(x['detection_rate']-x['clean_proxy_row_flag_rate'],x['family']=='rule'))
        choices[problem]=best['family']
    return choices


def benchmark():
    raw=json.loads(Path('data/nyc311_2023.json').read_text())
    rows=normalize(raw)
    train,validation,test=partition(rows)
    baseline=Baseline(train)
    valid=structurally_valid(validation)
    heldout=structurally_valid(test)
    if min(len(valid),len(heldout))<100: raise RuntimeError('Too few structurally valid held-out rows')
    val_records=evaluate(valid,baseline,rows_per_batch=240,seeds=(3,8),rates=(.05,.15))
    val_summary=aggregate(val_records)
    choices=choose(val_summary)
    records=evaluate(heldout,baseline)
    hybrid_records=evaluate(heldout,baseline,choices=choices)
    # Actual end-to-end full pipeline throughput and joint corruption, not a sum of isolated checks.
    batch=random.Random(811).sample(heldout,min(1000,len(heldout)))
    mixed=batch
    for i,p in enumerate(PROBLEMS[1:]):
        mixed,_,_=inject(mixed,p,.02,seed=900+i)
    hybrid=hybrid_run(mixed,baseline,choices)
    joint_counts={p:len({i for a in hybrid['alerts'] if a['problem']==p for i in a['rows']}) for p in PROBLEMS}
    end_to_end={'rows':len(mixed),'seconds':hybrid['seconds'],'rows_per_second':len(mixed)/hybrid['seconds'],
                'llm_calls':0,'paid_api_usd':0,'alerted_rows_by_problem':joint_counts,
                'note':'Joint-corruption stress run: counts only, no combined-label accuracy claim because corruptions can overwrite each other.'}
    results={'sample_rows':len(rows),'split':{'train':len(train),'validation':len(validation),'test':len(test),'validation_structurally_valid':len(valid),'test_structurally_valid':len(heldout)},
             'validation':val_summary,'choices':choices,'measurements':aggregate(records),'hybrid_measurements':aggregate(hybrid_records),'end_to_end':end_to_end,
             'llm_status':'NOT_RUN: no configured Gemini credentials; no LLM comparison winner can be claimed',
             'caveats':['Reference-clean means structurally screened, uncorrupted holdout; semantic labels are not independently adjudicated. Flag rates are proxy FPR, not certified FPR.',
                        'Rule/statistical schema/type/date support checks share contract; they are deliberately weak statistical baselines.',
                        'Corruption templates are narrow; high recall on them does not establish real-world recall.',
                        'Execution host is not the applicants laptop. Rerun on laptop before claiming laptop throughput.',
                        'Offline USD API cost excludes CPU, storage, monitoring, operations and tenant onboarding.']}
    out=Path('results');out.mkdir(exist_ok=True)
    (out/'profile_b.json').write_text(json.dumps(profile(raw),indent=2)+'\n')
    (out/'benchmark_b.json').write_text(json.dumps(results,indent=2)+'\n')
    (out/'trials_b.json').write_text(json.dumps({'validation':val_records,'test':records,'hybrid':hybrid_records},indent=2)+'\n')
    print('B: benchmark complete;',len(records),'isolated held-out trials; choices',choices)
    return results


if __name__=='__main__': benchmark()
