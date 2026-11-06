"""Seeded, labelled, isolated corruptions. Labels are never passed to detectors."""
from collections import defaultdict
from copy import deepcopy
from datetime import timedelta
import random
from .detectors import PROBLEMS,date,COLUMNS


def inject(clean,problem,rate=.05,seed=42):
    if problem not in PROBLEMS: raise ValueError('Unknown problem')
    if not 0<rate<=1: raise ValueError('Rate must be in (0,1]')
    if not clean: raise ValueError('Empty batch')
    rng=random.Random(seed)
    rows=deepcopy(clean)
    n=max(1,round(len(rows)*rate))
    eligible=list(range(len(rows)))
    if problem in ['swapped_coordinates','type_change']:
        eligible=[i for i,r in enumerate(rows) if r.get('latitude') is not None and r.get('longitude') is not None]
    elif problem in ['reversed_dates','date_format']:
        eligible=[i for i,r in enumerate(rows) if date(r.get('created_date'))]
    elif problem in ['zip_borough','complaint_descriptor']:
        eligible=[i for i,r in enumerate(rows) if r.get('incident_zip') and r.get('borough') and r.get('descriptor')]
    elif problem=='agency_null_spike':
        groups=defaultdict(list)
        for i,r in enumerate(rows):
            if r.get('descriptor'): groups[r.get('agency')].append(i)
        if not groups: return rows,set(),{'requested_rate':rate,'affected':0}
        agency,eligible=max(groups.items(),key=lambda pair:len(pair[1]))
    chosen=rng.sample(eligible,min(n,len(eligible)))
    truth=set()
    if problem=='schema':
        # Schema corruption is a batch event; controlled row rate does not apply.
        for i,r in enumerate(rows):
            if seed%2:
                r['agency_renamed']=r.pop('agency',None)
            else:
                r.pop('agency',None)
            truth.add(i)
    elif problem in ['exact_duplicates','near_duplicates']:
        for index in chosen:
            clone=deepcopy(rows[index])
            if problem=='near_duplicates':
                clone['unique_key']=str(clone.get('unique_key'))+'-copy'
                old=date(clone.get('created_date'))
                if old: clone['created_date']=(old+timedelta(seconds=rng.randint(1,90))).isoformat(timespec='milliseconds')
                clone['descriptor']=str(clone.get('descriptor') or '')+' '
            truth.add(len(rows));rows.append(clone)
    else:
        for i in chosen:
            r=rows[i]
            if problem=='type_change': r['latitude']=str(r['latitude'])
            elif problem=='date_format': r['created_date']=date(r['created_date']).strftime('%m/%d/%Y %H:%M:%S')
            elif problem=='swapped_coordinates': r['latitude'],r['longitude']=r['longitude'],r['latitude']
            elif problem=='agency_null_spike': r['descriptor']=None
            elif problem=='reversed_dates': r['closed_date']=(date(r['created_date'])-timedelta(days=1)).isoformat(timespec='milliseconds')
            elif problem=='zip_borough':
                options=[b for b in ['MANHATTAN','BROOKLYN','QUEENS','BRONX','STATEN ISLAND'] if b!=r.get('borough')]
                r['borough']=rng.choice(options)
            elif problem=='complaint_descriptor':
                # Pull a real descriptor from another complaint type, not a magic marker.
                alternatives=[x['descriptor'] for x in clean if x.get('descriptor') and x.get('complaint_type')!=r.get('complaint_type') and x['descriptor']!=r.get('descriptor')]
                if not alternatives: continue
                r['descriptor']=rng.choice(alternatives)
            elif problem=='resolution_status':
                r['status']='Closed'
                r['resolution_description']='This request is still open and awaiting inspection; it is not yet resolved.'
            elif problem=='personal_data':
                # Entirely fictional test entities; reserved example domain/555 numbers.
                options=[' Contact Jane Example at jane@example.com.',' Contact Alex Sample at 212-555-0123.',' My name is Morgan Example.']
                r['resolution_description']=str(r.get('resolution_description') or '')+rng.choice(options)
            truth.add(i)
    return rows,truth,{'requested_rate':rate,'realized_rate':len(truth)/len(rows),'affected':len(truth),
                       'rows':len(rows),'seed':seed,'scope':'batch' if problem=='schema' else 'group' if problem=='agency_null_spike' else 'row',
                       'note':'Duplicate rate is relative to original batch before appended copies; schema affects entire batch.'}
