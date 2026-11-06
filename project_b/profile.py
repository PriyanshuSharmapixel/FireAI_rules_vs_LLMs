"""Raw-data profile: counts and redacted examples, not invented corruption labels."""
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
from .detectors import COLUMNS, NUMERIC, Baseline, normalize, rule_detect


def profile(raw):
    rows=normalize(raw)
    baseline=Baseline(rows)
    alerts=rule_detect(rows,baseline)
    by_problem={}
    for a in alerts:
        record=by_problem.setdefault(a['problem'],{'row_ids':set(),'reasons':[]})
        record['row_ids'].update(a['rows'])
        record['reasons'].append(a['reason'])
    issues={}
    for key,value in by_problem.items():
        indices=sorted(value['row_ids'])
        issues[key]={'count':len(indices),'reasons':value['reasons'][:3],
                     'examples':[{'row_index':i,'unique_key':rows[i].get('unique_key'),
                                  'created_date':rows[i].get('created_date'),'closed_date':rows[i].get('closed_date'),
                                  'agency':rows[i].get('agency'),'borough':rows[i].get('borough'),
                                  'text_sha256':hashlib.sha256(str(rows[i].get('resolution_description')).encode()).hexdigest()} for i in indices[:3]]}
    return {'rows':len(rows),'missing_counts':{key:sum(r.get(key) in (None,'') for r in rows) for key in COLUMNS},
            'year_counts':dict(Counter(str(r.get('created_date',''))[:4] for r in rows)),
            'agencies':dict(Counter(r.get('agency') for r in rows)), 'rule_flags':issues,
            'caveats':['Missing optional descriptor, coordinates and closure date may be valid.',
                       'Reversed dates and duplicates are structural findings; semantic flags require adjudication.',
                       'ZIP/category profiles derived from this sample cannot independently validate their own associations.',
                       'Near-duplicate similarity can flag legitimate repeated complaints. Text examples are redacted.']}


if __name__=='__main__':
    raw=json.loads(Path('data/nyc311_2023.json').read_text())
    Path('results/profile_b.json').write_text(json.dumps(profile(raw),indent=2)+'\n')
