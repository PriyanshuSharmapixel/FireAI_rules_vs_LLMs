"""Measured offline winners, with optional bounded semantic LLM review.

LLM escalation preserves the original alerts: an LLM cannot erase hard errors.
An unflagged sample is included to measure blind spots, not silently ignored.
"""
import random
import time
from .detectors import PROBLEMS,rule_detect,statistical_detect,llm_detect


def run(rows, baseline, choices, client=None, review_cap=40, seed=42):
    start=time.perf_counter()
    alerts=[]
    for family,detector in [('rule',rule_detect),('statistical',statistical_detect)]:
        selected=[p for p in PROBLEMS if choices.get(p)==family]
        if selected: alerts.extend(detector(rows,baseline,only=selected))
    review={'enabled':client is not None,'reviewed_rows':0,'candidate_rows':0,'unreviewed_due_to_cap':0,'alerts':[]}
    if client:
        suspicious={i for a in alerts if a['problem'] in ['complaint_descriptor','resolution_status','personal_data','zip_borough'] for i in a['rows']}
        review['candidate_rows']=len(suspicious)
        candidates=sorted(suspicious)
        rng=random.Random(seed)
        # Reserve 20% for a uniform sample of otherwise unflagged rows.
        flagged=rng.sample(candidates,min(len(candidates),max(0,int(review_cap*.8))))
        others=[i for i in range(len(rows)) if i not in suspicious]
        selected=flagged+rng.sample(others,min(len(others),review_cap-len(flagged)))
        review['unreviewed_due_to_cap']=len(candidates)-len(flagged)
        review['reviewed_rows']=len(selected)
        if selected:
            extra=llm_detect([rows[i] for i in selected],baseline,client,only=['complaint_descriptor','resolution_status','personal_data','zip_borough'])
            for a in extra:
                a['rows']=[selected[j] for j in a['rows']]
            review['alerts']=extra
            alerts.extend(extra)
    return {'alerts':alerts,'review':review,'seconds':time.perf_counter()-start,'rows':len(rows)}
