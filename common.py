"""Small Gemini REST client with explicit limits and auditable usage.

No dependencies, no implicit mock fallback, no secret-bearing URLs or logs.
"""
import json
import os
import time
import urllib.request
from pathlib import Path


class Gemini:
    def __init__(self, max_calls=100, log_path='results/live/usage.jsonl'):
        self.key = os.getenv('GEMINI_API_KEY')
        self.model = os.getenv('GEMINI_MODEL')
        if not self.key or not self.model:
            raise RuntimeError('Set GEMINI_API_KEY and GEMINI_MODEL to enable live experiments')
        if not all(c.isalnum() or c in '-_.' for c in self.model):
            raise ValueError('Invalid model identifier')
        self.max_calls, self.calls, self.log_path = max_calls, 0, Path(log_path)

    def ask(self, instruction, data, temperature=0):
        if self.calls >= self.max_calls:
            raise RuntimeError('Configured LLM call budget exhausted')
        self.calls += 1
        payload = {'systemInstruction': {'parts': [{'text': instruction}]},
                   'contents': [{'role': 'user', 'parts': [{'text': json.dumps(data, ensure_ascii=False)}]}],
                   'generationConfig': {'temperature': temperature, 'responseMimeType': 'application/json'}}
        req = urllib.request.Request(
            'https://generativelanguage.googleapis.com/v1beta/models/' + self.model + ':generateContent',
            data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': self.key})
        start = time.perf_counter()
        record = {'model': self.model, 'call': self.calls, 'temperature': temperature, 'ok': False}
        try:
            # No automatic retry: failures remain in denominators and token usage is
            # unknown for failed responses. Reruns are explicit and separately logged.
            with urllib.request.urlopen(req, timeout=90) as response:
                raw = json.load(response)
            record['usage'] = raw.get('usageMetadata', {})
            result = json.loads(''.join(part.get('text', '') for part in raw['candidates'][0]['content']['parts']))
            record['ok'] = True
            return result
        finally:
            record['seconds'] = time.perf_counter() - start
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open('a') as out:
                out.write(json.dumps(record) + '\n')


def token_cost(usage):
    input_rate = os.getenv('GEMINI_INPUT_USD_PER_MILLION')
    output_rate = os.getenv('GEMINI_OUTPUT_USD_PER_MILLION')
    if input_rate is None or output_rate is None:
        return None
    # Include thinking tokens when reported. Pricing assumptions must match model.
    return (usage.get('promptTokenCount', 0) * float(input_rate) +
            (usage.get('candidatesTokenCount', 0) + usage.get('thoughtsTokenCount', 0)) * float(output_rate)) / 1e6
