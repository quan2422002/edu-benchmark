# Topic mapping guidelines

Use this file when grouping Tin học THCS topics or linking grade-9 content to grade-6–8 prerequisites.

## Required separation

Label each statement as one of:

- `source_evidence`: directly visible in a curriculum or learning-resource source;
- `curator_inference`: a reasonable grouping or prerequisite relation inferred by UET/agent;
- `needs_hnmu_review`: a pedagogical decision requiring HNMU confirmation.

## Topic map columns

Recommended columns for `topic_map_grade6_9.csv`:

```text
topic_group_id, topic_group_name, grade, source_topic_label, learning_material_ids, evidence_note, status
```

## Prerequisite map columns

Recommended columns for `grade9_prerequisite_map.csv`:

```text
grade9_topic_id, grade9_learning_material_ids, prerequisite_grade, prerequisite_topic_label, prerequisite_learning_material_ids, relation_note, evidence_type, status
```

## Rules

- Do not force exact topic names across grades when sources use different labels.
- Prefer a small number of stable topic groups and record local source labels separately.
- Mark uncertain prerequisite links as `needs_hnmu_review`.
- Do not claim a prerequisite is required unless a source or HNMU confirms it.
