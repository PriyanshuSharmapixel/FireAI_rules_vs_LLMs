"""One command: validate inputs, run tests, reproduce evidence and reports."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--replay',action='store_true',help='Regenerate exact report tables from retained measurements; still run tests')
    p.add_argument('--download',action='store_true',help='Refresh the 12,000-row source snapshot before benchmarking')
    p.add_argument('--strict',action='store_true',help='Fail when submission evidence gates remain open')
    a=p.parse_args()
    if a.replay and a.download: p.error('--replay and --download cannot be combined')
    os.chdir(ROOT)
    if a.download:
        from project_b.download import download
        download()
    data=Path('data/nyc311_2023.json')
    manifest=json.loads(data.with_suffix('.manifest.json').read_text())
    if hashlib.sha256(data.read_bytes()).hexdigest()!=manifest['sha256']:
        raise RuntimeError('NYC data hash mismatch; do not compare a modified snapshot silently')
    fixtures=json.loads(Path('project_a/fixtures/manifest.json').read_text())
    for name,digest in fixtures.items():
        if hashlib.sha256((Path('project_a/fixtures')/name).read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Frozen fixture changed: '+name+'; review and explicitly update manifest')
    subprocess.run([sys.executable,'-m','unittest','discover','-q'],check=True)
    if not a.replay:
        from project_a.benchmark import benchmark as a_benchmark
        from project_b.benchmark import benchmark as b_benchmark
        a_benchmark();b_benchmark()
        Path('results/environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),
                'machine':platform.machine(),'processor':platform.processor(),'cpu_count':os.cpu_count(),
                'timing_scope':'Execution host, not applicants laptop; perf_counter; no network in offline benchmark'},indent=2)+'\n')
    else:
        # Official evidence is mutable; refresh its gate even in measurement replay.
        from project_a.benchmark import official_validation
        aa=Path('results/benchmark_a.json');obj=json.loads(aa.read_text())
        obj['official_validation']=official_validation(json.loads(Path('project_a/fixtures/tax_cases.json').read_text()))
        aa.write_text(json.dumps(obj,indent=2)+'\n')
    from reports import generate
    generate()
    status=json.loads(Path('results/submission_status.json').read_text())
    print('Submission gates:',json.dumps(status))
    if a.strict and not status['ready_to_claim_assignment_complete']:
        print('INCOMPLETE: inspect results/submission_status.json; do not submit as fully complete.',file=sys.stderr)
        return 2
    return 0


if __name__=='__main__':sys.exit(main())
