# Provenance matrix guidelines

The provenance matrix explains why a task, rubric, or serious error exists.

## Required relationship

Each row connects one item to its support:

```text
item_id, item_type, research_ids, learning_material_ids, rationale, status
```

## Support types

- `research_ids`: IDs from evidence review artifacts.
- `learning_material_ids`: IDs from learning-resource source or fragment mappings.
- `rationale`: Vietnamese explanation connecting support to the item.

## Label uncertainty

If support is incomplete, do not hide the gap. Use `needs_uet_review` or `needs_hnmu_review` and explain what decision is missing.

## Do not backfill evidence

Do not edit source evidence or learning-resource mappings just to make a proposed item look supported. Create an open question instead.
