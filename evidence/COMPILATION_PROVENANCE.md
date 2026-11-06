# Compiled-rule provenance

Generator: ChatGPT Codex, during this task on 6 November 2026. No separate
Gemini call produced the checked-in configuration. This distinction is visible
in the benchmark labels (`compiled_codex`) and must remain in the submission.

Generation task: convert the reviewed salary-only operational extracts in
`project_a/rules/2024-25.md` and `2025-26.md` into declarative JSON containing
ordered slab boundaries/rates, age-specific old slabs, deduction caps, standard
deductions, rebate limits, surcharge tiers and cess. Execute JSON through a
fixed interpreter; do not execute generated Python.

Outputs: the corresponding year-named JSON files. Review performed in this
session: compared constants against the official-source extracts; compared all
2,296 frozen cases, both regimes, against the independently coded closed-form
oracle and handwritten engine; tested FY mismatch rejection and slab ordering.
This is AI-assisted self-review, not independent human legal review. The
applicant must review the configuration before submission.

`compile_candidate(fy, client)` repeats the compilation experiment using Gemini,
records the candidate path/hash and requires explicit review before promotion.
Candidates are ignored by the production loader. Candidate generation latency
is measured when live experiments run; no historical compilation-time claim is
made for the checked-in Codex output.

Design limitation: the LLM-generated configuration covers legal constants and
slab/rebate tables; HRA/deduction operations and settlement algorithm are fixed
interpreter code, not a complete compiler for arbitrary tax legislation. A new
kind of deduction requires interpreter changes, not merely a configuration edit.
