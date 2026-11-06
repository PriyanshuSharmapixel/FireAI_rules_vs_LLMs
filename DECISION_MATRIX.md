# Decision matrix

Offline choices are provisional. Every number is generated from retained JSON evidence; proxy FPR and missing live measurements remain explicit.

| Component / check | Classification | Choice and measured justification |
|---|---|---|
| Tax arithmetic | rule | Handwritten exact agreement 100.00% with independent oracle; 0 varying repeated inputs; official checks pending |
| Tax configuration authoring | hybrid | Codex-generated reviewed constants execute as rules; Gemini compilation candidate path unrun; arbitrary legal logic still requires code changes |
| Free-text extraction | hybrid | Conservative rule readiness checks pass 50/50 curated examples; Gemini extraction implemented but unmeasured; explicit clarification required |
| Regime recommendation | rule | Compare computed rounded liabilities; report tie; deterministic in regression checks |
| Legal release | hybrid | Human clause review plus deterministic regression/calculator gate; no automatically promoted generated rules |
| Runtime LLM tax calculation | LLM | Implemented experimental comparator; no offline evidence justifies production use |
| schema | rule | Validation recall 100.00%, clean-proxy flags 0.00%; chosen before held-out test; see RESULTS_B for test results |
| type_change | rule | Validation recall 100.00%, clean-proxy flags 0.00%; chosen before held-out test; see RESULTS_B for test results |
| date_format | rule | Validation recall 100.00%, clean-proxy flags 0.00%; chosen before held-out test; see RESULTS_B for test results |
| swapped_coordinates | rule | Validation recall 100.00%, clean-proxy flags 0.00%; chosen before held-out test; see RESULTS_B for test results |
| exact_duplicates | rule | Validation recall 100.00%, clean-proxy flags 0.00%; chosen before held-out test; see RESULTS_B for test results |
| near_duplicates | rule | Validation recall 100.00%, clean-proxy flags 0.00%; chosen before held-out test; see RESULTS_B for test results |
| agency_null_spike | statistical | Validation recall 100.00%, clean-proxy flags 0.00%; chosen before held-out test; see RESULTS_B for test results |
| reversed_dates | rule | Validation recall 100.00%, clean-proxy flags 0.00%; chosen before held-out test; see RESULTS_B for test results |
| zip_borough | rule | Validation recall 97.92%, clean-proxy flags 0.00%; chosen before held-out test; see RESULTS_B for test results |
| complaint_descriptor | rule | Validation recall 96.88%, clean-proxy flags 1.46%; chosen before held-out test; see RESULTS_B for test results |
| resolution_status | statistical | Validation recall 100.00%, clean-proxy flags 0.00%; chosen before held-out test; see RESULTS_B for test results |
| personal_data | rule | Validation recall 100.00%, clean-proxy flags 5.83%; chosen before held-out test; see RESULTS_B for test results |
| Semantic escalation | hybrid | Capped candidate review plus unflagged sample implemented; LLM evidence pending, cannot claim a measured improvement |
| Every-problem LLM comparator | LLM | All 12 checks implemented in shared reviewer; NOT RUN without Gemini; no invented cost/detection values |
