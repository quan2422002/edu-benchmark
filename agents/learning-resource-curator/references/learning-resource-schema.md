# Learning-resource schema v0

Use this schema for early, auditable mappings. The mapping table is the source of truth; IDs are lookup keys, not full encodings of every page or section.

## Source map: `learning_resource_source_map.csv`

Required columns:

| Column | Meaning |
|---|---|
| `learning_material_id` | Unique v0 learning-material ID, for example `LM-SGK-TIN9-4700233123` or `LM-SGK-TIN9-0001`. |
| `source_title` | Human-readable title of the source. |
| `material_type` | `SGK`, `SGV`, `SBT`, `tap_huan`, or another explicit type. |
| `grade` | Grade or grade range, for example `9`, `6-9`, or `THCS`. |
| `source_url` | Original URL when available. |
| `source_key` | Stable key visible in the source when available, such as a taphuan numeric key. |
| `local_file_path` | Local file path when downloaded or OCR processed. |
| `version_label` | Version, import date, or processing date. |
| `status` | `draft`, `needs_uet_review`, `needs_hnmu_review`, `confirmed`, or `retired`. |
| `notes` | Retrieval notes, warnings, or unresolved issues. |

At least one of `source_url`, `local_file_path`, or `notes` must explain how to retrieve the source.

## Fragment map: `learning_resource_fragments.csv`

Required columns when fragments exist:

| Column | Meaning |
|---|---|
| `fragment_id` | Unique fragment ID, usually `<learning_material_id>#F0001`. |
| `learning_material_id` | Parent source ID from the source map. |
| `page_start` | First page if known. |
| `page_end` | Last page if known. |
| `section_label` | Lesson, section, table, exercise, or heading if known. |
| `order_index` | Reading order within the parent source or page. |
| `location_note` | Natural-language location note. |
| `status` | Same status vocabulary as source map. |

A fragment should have at least one useful locator: page, section label, or location note.

## Status rules

- Use `draft` for machine/OCR/import outputs that have not been checked.
- Use `needs_uet_review` for technical cleanup or mapping questions.
- Use `needs_hnmu_review` for subject-matter or pedagogical confirmation.
- Use `confirmed` only when the relevant human reviewer has accepted the item.
- Use `retired` instead of deleting IDs that were already referenced.
