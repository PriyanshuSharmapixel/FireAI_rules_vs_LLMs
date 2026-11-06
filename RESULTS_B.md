# Project B results

**Status: real-data profile, injector, rule/statistical detectors and offline hybrid measured. Gemini family remains unmeasured unless live evidence is present.**

Source sample: 12,000 NYC 311 requests created in 2023, first ordered monthly quotas. This is not a probability sample or a full-year census. Source queries and SHA-256 are in data/nyc311_2023.manifest.json.
Train/validation/test: 7,178 / 2,393 / 2,429, split by stable hash of unique request key. Structurally screened validation/test pools: 2,328 / 2,352. Training frequencies are never fitted on injected evaluation data.

## Existing raw-data findings

| Finding | Count | Interpretation |
|---|---:|---|
| reversed_dates | 11 | Closure precedes creation; inspect agency corrections/time semantics |
| near_duplicates | 663 | Similarity candidates; repeated legitimate complaints can look alike |
| resolution_status | 138 | Lexical contradiction candidates; resolution text may describe an earlier workflow stage |
| personal_data | 520 | Pattern matches, not adjudicated PII; names and ordinary phrases can collide |

Counts and redacted row examples are in results/profile_b.json. Missing optional data is a profile characteristic, not automatically a defect.

| Column | Missing/empty |
|---|---:|
| unique_key | 0 |
| created_date | 0 |
| closed_date | 261 |
| agency | 0 |
| complaint_type | 0 |
| descriptor | 206 |
| status | 0 |
| resolution_description | 155 |
| incident_zip | 194 |
| borough | 0 |
| latitude | 142 |
| longitude | 142 |

## Controlled evaluation

Each problem has three held-out seeds and 1%, 5%, 15% requested corruption rates. Injected row IDs are stored separately from detector inputs. Duplicates append rows; their realized final fraction differs slightly. Schema rename/drop affects the whole batch, so row-rate control is inapplicable. Agency null spikes affect one agency. Both schema rename and drop occur across seeds.
**False-alarm caveat:** the uncorrupted holdout is structurally screened, not independently annotated for semantic correctness. The reported clean-row/batch flag rates are proxy FPR, not verified false-alarm rates. Real residual anomalies can be counted as apparent false alarms. Broad semantic validity needs human adjudication.
Throughput is measured on the execution host, not the applicant laptop. USD figures below are paid API charges only and exclude CPU/storage/operations. LLM NOT RUN is unavailable, never zero.

| Problem | Family | Injected-row detection | Clean proxy row flags | Clean proxy batch flags | Corrupt batch detection | Rows/sec | Paid API USD/million rows |
|---|---|---:|---:|---:|---:|---:|---|
| schema | rule | 100.00% | 0.00% | 0.00% | 100.00% | 23150 | 0; compute excluded |
| schema | statistical | 100.00% | 0.00% | 0.00% | 100.00% | 25853 | 0; compute excluded |
| schema | Gemini | NOT RUN | unavailable | unavailable | unavailable | unavailable | unavailable |
| type_change | rule | 100.00% | 0.00% | 0.00% | 100.00% | 28927 | 0; compute excluded |
| type_change | statistical | 100.00% | 0.00% | 0.00% | 100.00% | 26794 | 0; compute excluded |
| type_change | Gemini | NOT RUN | unavailable | unavailable | unavailable | unavailable | unavailable |
| date_format | rule | 100.00% | 0.00% | 0.00% | 100.00% | 25512 | 0; compute excluded |
| date_format | statistical | 100.00% | 0.00% | 0.00% | 100.00% | 21580 | 0; compute excluded |
| date_format | Gemini | NOT RUN | unavailable | unavailable | unavailable | unavailable | unavailable |
| swapped_coordinates | rule | 100.00% | 0.00% | 0.00% | 100.00% | 23966 | 0; compute excluded |
| swapped_coordinates | statistical | 100.00% | 0.00% | 0.00% | 100.00% | 27914 | 0; compute excluded |
| swapped_coordinates | Gemini | NOT RUN | unavailable | unavailable | unavailable | unavailable | unavailable |
| exact_duplicates | rule | 100.00% | 0.00% | 0.00% | 100.00% | 29193 | 0; compute excluded |
| exact_duplicates | statistical | 100.00% | 0.00% | 0.00% | 100.00% | 30275 | 0; compute excluded |
| exact_duplicates | Gemini | NOT RUN | unavailable | unavailable | unavailable | unavailable | unavailable |
| near_duplicates | rule | 100.00% | 0.00% | 0.00% | 100.00% | 17057 | 0; compute excluded |
| near_duplicates | statistical | 100.00% | 0.14% | 33.33% | 100.00% | 19796 | 0; compute excluded |
| near_duplicates | Gemini | NOT RUN | unavailable | unavailable | unavailable | unavailable | unavailable |
| agency_null_spike | rule | 72.00% | 0.00% | 0.00% | 33.33% | 24472 | 0; compute excluded |
| agency_null_spike | statistical | 96.00% | 0.00% | 0.00% | 66.67% | 24794 | 0; compute excluded |
| agency_null_spike | Gemini | NOT RUN | unavailable | unavailable | unavailable | unavailable | unavailable |
| reversed_dates | rule | 100.00% | 0.00% | 0.00% | 100.00% | 23707 | 0; compute excluded |
| reversed_dates | statistical | 100.00% | 0.00% | 0.00% | 100.00% | 24351 | 0; compute excluded |
| reversed_dates | Gemini | NOT RUN | unavailable | unavailable | unavailable | unavailable | unavailable |
| zip_borough | rule | 99.33% | 0.00% | 0.00% | 100.00% | 24749 | 0; compute excluded |
| zip_borough | statistical | 99.33% | 0.00% | 0.00% | 100.00% | 26802 | 0; compute excluded |
| zip_borough | Gemini | NOT RUN | unavailable | unavailable | unavailable | unavailable | unavailable |
| complaint_descriptor | rule | 97.33% | 1.81% | 100.00% | 100.00% | 27133 | 0; compute excluded |
| complaint_descriptor | statistical | 91.33% | 0.56% | 66.67% | 100.00% | 17798 | 0; compute excluded |
| complaint_descriptor | Gemini | NOT RUN | unavailable | unavailable | unavailable | unavailable | unavailable |
| resolution_status | rule | 100.00% | 1.11% | 100.00% | 100.00% | 28756 | 0; compute excluded |
| resolution_status | statistical | 100.00% | 0.00% | 0.00% | 100.00% | 28274 | 0; compute excluded |
| resolution_status | Gemini | NOT RUN | unavailable | unavailable | unavailable | unavailable | unavailable |
| personal_data | rule | 100.00% | 4.17% | 100.00% | 100.00% | 25638 | 0; compute excluded |
| personal_data | statistical | 64.00% | 2.92% | 100.00% | 100.00% | 28754 | 0; compute excluded |
| personal_data | Gemini | NOT RUN | unavailable | unavailable | unavailable | unavailable | unavailable |

Every implemented alert includes a reason; wording presence is measured, but explanation usefulness has not been human-scored. Statistical schema/type/date novelty overlaps with declarative contracts and is intentionally a weak baseline. No sophisticated ML performance is claimed.
Near-duplicates use bounded blocking (last 50 candidates); cross-block/cross-chunk matches may be missed. ZIP/borough and complaint/descriptor checks use observed source associations, not external authoritative mappings. PII rules cover formatted phone/email and cue-based names, not all names or personal data.

## Hybrid selected on validation, evaluated on held-out test

Selection score = injected-row recall minus clean-proxy row flag rate; prefer rules on ties. LLM is excluded from winner selection until measured. The choices are provisional for these corruption templates.

| Problem | Selected offline family | Held-out detection | Clean proxy row flags |
|---|---|---:|---:|
| agency_null_spike | statistical | 96.00% | 0.00% |
| complaint_descriptor | rule | 97.33% | 1.81% |
| date_format | rule | 100.00% | 0.00% |
| exact_duplicates | rule | 100.00% | 0.00% |
| near_duplicates | rule | 100.00% | 0.00% |
| personal_data | rule | 100.00% | 4.17% |
| resolution_status | statistical | 100.00% | 0.00% |
| reversed_dates | rule | 100.00% | 0.00% |
| schema | rule | 100.00% | 0.00% |
| swapped_coordinates | rule | 100.00% | 0.00% |
| type_change | rule | 100.00% | 0.00% |
| zip_borough | rule | 99.33% | 0.00% |

Joint-corruption end-to-end run: 1,040 rows in 0.0926 seconds (11237 rows/sec), 0 LLM calls, USD 0 paid API cost. Per-problem alert counts are in benchmark_b.json. Joint corruptions can overwrite earlier ones, so this stress run does not claim combined ground-truth recall.
Optional Gemini escalation reviews capped semantic candidates and reserves 20% of its row budget for otherwise unflagged sampling. It preserves deterministic hard-error alerts. Candidate backlog and unreviewed rows are explicit. This optional stage has not earned production selection on offline evidence.

## Scale design: 50 million rows/day across 120 customers (under two pages)

Assume 50 million rows/day is the **aggregate** across tenants, uniformly arriving: 578.7 rows/sec on average and 416,667 rows/customer/day if equally sized. Real tenant skew and bursts invalidate the equal-share assumption. At this sample's measured full-pipeline rate, a linear single-process extrapolation is 1.24 process wall-hours/day. This is a rough lower-bound planning estimate, not a load test; schema diversity, I/O, memory pressure, dedup state and traffic bursts are absent.
**Rules on ingestion.** Keep per-customer versioned schemas and explicit timestamp/coordinate contracts. Quarantine schema changes; never coerce silently. Partition by tenant/date/agency. Maintain idempotency keys and bounded indexed dedup windows so duplicates crossing batch boundaries are caught. Near-duplicate blocking needs recall audits and distributed state rather than a single in-memory sample.
**Statistics per window.** Retain tenant-and-agency baselines with minimum sample sizes, seasonality windows and approved updates. Use labelled alert review to tune thresholds; apply alert grouping and false-discovery controls across 120 schemas. Novel categories become review candidates, not automatic invalid data. Do not train baselines on quarantined corruptions.
**Bound LLM work.** If fraction f is reviewed and measured mean tokens/row is t, daily review tokens are 50,000,000*f*t. At f=0.001 there are 50,000 reviewed rows/day; f=0.01 gives 500,000. Multiply measured input/output tokens separately by verified model rates, include retry/thinking tokens and queue latency. No token cost is claimed while the live experiment is unrun. A free tier is an experiment constraint, not a production SLA.
**Protect the CFO dashboard.** Critical schema/date/duplicate failures quarantine affected batches. Semantic suspicion routes to review with lineage and redacted evidence. Use backpressure, tenant budgets and a dead-letter queue; expose freshness and quality status to downstream consumers. LLM failure cannot silently mark a batch healthy. Audit sampled accepted rows to measure blind spots.

Before production: independently adjudicate real clean/error labels, add corruption diversity and multi-error interactions, rerun on the actual laptop and a large streaming load, measure Gemini and freeze approved model/schema versions.
