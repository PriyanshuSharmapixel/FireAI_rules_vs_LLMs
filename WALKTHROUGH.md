# Explain and modify the submission

This is an interview study guide, not a script to memorize.

1. **Describe the experiment.** Same problem, different tools. Choose based on
   correctness, repeatability, cost, latency, source trace and change safety.
2. **Read model.py.** Distinguish CTC, annual gross salary, tax residency, age,
   eligible deductions and annual/rental-period amounts. Explain why the parser
   cannot fill missing financial facts with guesses.
3. **Trace handwritten.py using examples/tax.json.** Follow standard deduction,
   HRA, Chapter VIA, home interest, income rounding, slabs, rebate, surcharge,
   both marginal relief mechanisms, cess and final rounding. Rebate relief and
   surcharge relief are different discontinuities.
4. **Explain the oracle.** Production uses progressive bands; tests use separate
   piecewise formulas. Agreement can still share a wrong legal interpretation,
   which is why official-calculator verification is mandatory.
5. **Read compiled_rules.py.** LLM-produced JSON supplies constants, fixed Python
   executes them. No arbitrary generated code runs. A novel legal operation can
   require interpreter changes; do not call it an unrestricted law compiler.
6. **Read parser.py and llm_runtime.py.** The former extracts facts; the latter
   actually asks Gemini to calculate. They are separate experiments.
7. **Read the NYC manifest.** Know why the 12,000-row sample is not representative
   of the entire city/year. Explain input normalization and stable API fields.
8. **Read inject.py.** Show where labels are produced and why detectors never
   receive them. Explain batch-level schema events and append-based duplicates.
9. **Read Baseline and both detector functions.** Explain MAD robust ranges,
   conditional frequencies, binomial null-rate deviations, similarity blocking
   and why semantic/PII proxies can generate false alarms.
10. **Read benchmark.py and hybrid.py.** Train on one split, choose on validation,
    report on held-out test. Know the clean-label limitation and why optional
    sampling checks otherwise unflagged rows.

Practise these live changes:

- Change a slab boundary in a candidate config and show regression failures.
- Set gross salary just above a rebate threshold; explain marginal relief.
- Change the taxpayer from resident to non-resident at age 80.
- Add a legitimate new complaint/descriptor pair and reduce novelty alerts.
- Change a null-spike threshold and observe recall/false-flag trade-offs.
- Make the LLM unavailable and demonstrate clarification instead of guessing.
- Explain what happens to duplicates spanning batch boundaries at production scale.

Be candid about pending experiments and process limitations. Never quote the
independent-oracle score as official-calculator accuracy, execution-host speed
as laptop throughput, or zero paid API charges as zero total operating cost.
