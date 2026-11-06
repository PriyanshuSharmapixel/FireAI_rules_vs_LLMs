# AI usage

ChatGPT Codex assisted with interpreting the assignment, finding official
sources, authoring Python code, producing declarative tax configuration,
independent-formula test fixtures, corruption experiments and this documentation.
No other person collaborated on the implementation.

Gemini is supported through a small REST adapter. No Gemini calls ran in the
initial offline evidence because no API key/model was configured. The runtime
calculator and LLM data-quality evaluator are implemented, but unmeasured LLM
outputs are never represented as observed results.

A concrete AI error: the initial insurance-cap implementation relied only on an
explicit self-group senior flag. Review identified that a resident taxpayer's
own age >=60 already establishes senior eligibility for their self coverage.
The handwritten engine, compiled interpreter and independent oracle were
corrected, and `test_senior_self_insurance_uses_taxpayer_age` now guards this.

A second review correction: current official webpages can include later
amendments. The source register records this, and the two requested FYs are
pinned rather than adopting the latest page indiscriminately.

Development-order disclosure: the current implementation was developed
iteratively; it does not provide a contemporaneous test-first history or a
human-timed legal migration. The frozen independent oracle, regression suite,
and explicitly labelled stale-law simulation are evidence actually available.
Do not claim these satisfy an historical process that was not recorded.

Applicant review is still required: explain every line, inspect the official
legal provisions and calculator evidence, understand the statistical baselines
and proxy false-positive labels, configure Gemini, and run the missing live
experiments. Do not claim the AI's work as independently validated human work.
