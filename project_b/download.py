"""Download a deterministic 2023 sample from the named NYC source only."""
import argparse
import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

COLUMNS = ['unique_key', 'created_date', 'closed_date', 'agency', 'complaint_type', 'descriptor',
           'status', 'resolution_description', 'incident_zip', 'borough', 'latitude', 'longitude']
ENDPOINT = 'https://data.cityofnewyork.us/resource/erm2-nwe9.json'


def download(output='data/nyc311_2023.json', limit=12000):
    # Monthly quota avoids a sample consisting only of New Year's Eve.
    # This is NOT a representative probability sample.
    rows, queries = [], []
    for month in range(1, 13):
        following = f'2023-{month+1:02d}-01' if month < 12 else '2024-01-01'
        count = limit // 12 + (month <= limit % 12)
        if not count:
            continue
        params = {'$select': ','.join(COLUMNS), '$where': f"created_date >= '2023-{month:02d}-01T00:00:00' AND created_date < '{following}T00:00:00'",
                  '$order': 'created_date ASC,unique_key ASC', '$limit': count}
        url = ENDPOINT + '?' + urllib.parse.urlencode(params)
        for attempt in range(3):
            try:
                with urllib.request.urlopen(url, timeout=60) as response:
                    batch = json.load(response)
                if not isinstance(batch, list) or not all(isinstance(x, dict) for x in batch):
                    raise ValueError('Unexpected Socrata response')
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(1 + attempt)
        rows.extend(batch)
        queries.append({'url': url, 'rows': len(batch)})
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(rows, ensure_ascii=False, separators=(',', ':')).encode()
    out.write_bytes(content)
    manifest = {'endpoint': ENDPOINT, 'year': 2023, 'sampling': 'First ordered quota from each calendar month; not random',
                'requested': limit, 'downloaded': len(rows), 'sha256': hashlib.sha256(content).hexdigest(), 'queries': queries,
                'retrieved_utc': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}
    out.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2))
    print(json.dumps({'rows': len(rows), 'sha256': manifest['sha256']}))
    return rows


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--limit', type=int, default=12000)
    p.add_argument('--output', default='data/nyc311_2023.json')
    a = p.parse_args()
    if a.limit < 12:
        p.error('Use at least 12 rows')
    download(a.output, a.limit)
