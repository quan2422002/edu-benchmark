# Evidence matrix schema

Required CSV columns:

| Column | Meaning |
|---|---|
| `record_id` | Stable local identifier. |
| `title` | Study title. |
| `year` | Publication or preprint year. |
| `venue` | Venue or repository. |
| `url_or_doi` | Stable URL or DOI. |
| `publication_status` | `peer_reviewed`, `preprint`, `thesis`, or `other`. |
| `study_type` | Benchmark, dataset, experiment, review, method, or other. |
| `education_domain` | Subject area or general education. |
| `learner_level` | Learner age/grade/level. |
| `tutoring_capabilities` | Capabilities studied. |
| `task_or_dataset` | Evaluation task or dataset. |
| `human_expert_role` | Authoring, review, annotation, adjudication, validation, or none reported. |
| `rubric_or_metric` | Rubric and metrics. |
| `reliability_evidence` | Agreement, validation, or `not_reported`. |
| `main_findings` | Concise source-grounded findings. |
| `limitations` | Reported or clearly identified limitations. |
| `relevance_to_project` | Relevance to Vietnamese grade-9 informatics tutoring. |
| `evidence_location` | Section/page/table/figure supporting key extraction. |
| `reviewer_notes` | Uncertainty and follow-up notes. |

Separate multi-value entries with semicolons. Do not encode missing evidence as zero; use `not_reported` or leave optional descriptive fields blank.
