"""Examples: python -m project_a.cli --input examples/tax.json
python -m project_a.cli --text 'Meri salary 12 lakh hai' --llm-parser
"""
import argparse
import json
from pathlib import Path
from .model import TaxInput
from .handwritten import compare
from .parser import parse


def main():
    p=argparse.ArgumentParser()
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--input',help='Structured JSON file; documented defaults apply')
    group.add_argument('--text')
    p.add_argument('--llm-parser',action='store_true')
    a=p.parse_args()
    if a.input:
        result=compare(TaxInput(**json.loads(Path(a.input).read_text())))
    else:
        client=None
        if a.llm_parser:
            from common import Gemini
            client=Gemini(max_calls=1)
        result=parse(a.text,client)
        if result['status']=='ready': result['calculation']=compare(TaxInput(**result['values']))
    print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__=='__main__':main()
