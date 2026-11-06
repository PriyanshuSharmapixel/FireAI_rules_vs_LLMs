# Submission status and remaining work

## Implemented and measured

- [x] Python 3.10+ project with standard-library offline execution.
- [x] Both FYs, old/new salary-only tax engines and clause-labelled breakdown.
- [x] Handwritten rules and reviewed Codex-generated declarative rules.
- [x] 2,296 frozen independent-formula cases, both regimes; boundary coverage.
- [x] Fifty descriptions with readiness/clarification expectations, including Hinglish.
- [x] Conservative parser and runnable Gemini extraction path.
- [x] Ten-repeat deterministic experiments, latency and API-cost distinction.
- [x] Stale-year silent-error simulation, labelled as simulation.
- [x] Real 2023 NYC 311 snapshot with 12-month sampling and hash manifest.
- [x] Raw quality profile with counts/redacted examples.
- [x] All 12 corruption injectors with controlled rates, seeds and separate labels.
- [x] Rules and fitted-statistical baselines for all 12 categories.
- [x] All-category Gemini review implementation with validation/bounded calls.
- [x] Disjoint training/validation/test, 216 isolated held-out offline trials.
- [x] Offline hybrid selected on validation; held-out and end-to-end measurements.
- [x] Required results, decision matrix, AI note, architecture/scale discussions.
- [x] One-command reproduction and CI definition.

## Required evidence still pending

- [ ] Actually verify at least 30 distinct tax cases, BOTH regimes, with the
      official calculator; keep evidence and complete the CSV register.
- [ ] Review complete historical legislation; primary full-Act PDF retrieval
      failed here. Review operational extracts and self-occupied/HRA limitations.
- [ ] Configure free-tier Gemini locally. Run and retain real query-time tax,
      parser, repetition, compiler, all-category quality and hybrid experiments.
- [ ] Expand live tax coverage to the entire test suite and match the offline
      quality experiment's seeds/rates/row denominators for fair comparisons.
- [ ] Evaluate Gemini compilation candidates; review before promoting them.
- [ ] Record matched old-rule/new-rule LLM outcomes and genuine update timing.
- [ ] Adjudicate a genuine clean/error quality set; replace proxy FPR claims with
      verified false-alarm measurements and check injection label validity.
- [ ] Run throughput measurements on the applicant laptop, not this host.
- [ ] Calculate measured LLM token costs/1,000 requests and /million rows with
      explicit rates, free-tier charges, failures and quota assumptions.
- [ ] Review and explicitly commit sanitized live evidence; ignored files are
      not automatically part of the private repo.
- [ ] Create/upload the private GitHub repository, verify access and give the
      actual hiring-team accounts access after their identities are supplied.
- [ ] Read/change every submitted function; complete registration only when ready.

## Process limitations that must remain disclosed

The assignment asks for tests first and a timed law-change exercise. This
implementation was built iteratively, with both years supported in the first
completed version. It does not have historical proof of either requested
process. A retrospective simulation must never be represented as that history.
If this process requirement is strict, explain the limitation to the reviewer.

HRA currently needs a consistent period. Mixed insurance/medical-expense groups
are conservatively rejected. Broader period/person-level modelling may be
needed for fully general coverage of the scoped deductions.
