# Specialist handoff

- Delegation ID: `p03-review-protocol-evidence-label-clarification-007`
- Agent: `research-methodologist`
- Status: `completed via single-agent fallback`
- Native thread ID/label: `null` / parent thread

## Delegation prompt

Làm rõ phần “Quy tắc nhãn bằng chứng” trong `review_protocol.md`: nhãn này nghĩa là gì, dùng ở đâu, và dùng như thế nào trong paper summaries/evidence matrix/synthesis.

## Follow-up or steer messages

Người phụ trách dự án hỏi trực tiếp: “Cái này có nghĩa là gì? được dùng ở đâu và dùng như thế nào?”

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260705_215045/roadmap.md`
- `agents/research-methodologist/SKILL.md`
- `agents/research-methodologist/references/review-protocol.md`
- `agents/research-methodologist/references/evidence-schema.md`
- `agents/research-methodologist/scripts/validate_evidence_matrix.py`
- `experiments/20260705_215045/literature_notes/review_protocol.md`

## Outputs created

- `experiments/20260705_215045/literature_notes/review_protocol.md` — clarified Section 4.
- `experiments/20260705_215045/metadata.yaml` — added this handoff artifact.

## Result summary

Section 4 now explains that evidence labels separate source-supported claims, project inferences, and open decisions. It also states where labels appear: paper summaries, future `evidence_to_design_matrix.csv`, and final synthesis. The protocol clarifies how to map labels to the current validator schema.

## Orchestrator decision

Only the protocol was changed; existing paper summaries were not rewritten because they already contain a `Nhãn` column in candidate-claim tables. Evidence matrix remains deferred to a later step.

## Uncertainty

- The exact column name for the future claim-level matrix should be finalized before creating `evidence_to_design_matrix.csv`; suggested name: `support_label`.

## Open questions and next human decisions

- Should P03 create a claim-level `evidence_to_design_matrix.csv` with `support_label`, or a validator-compatible study-level `evidence_matrix.csv`, or both?
