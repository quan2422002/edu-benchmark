# Resource fragmentation guidelines

Use this file when splitting learning resources into teacher-citable fragments.

## Fragmenting principle

Create fragments that are large enough to preserve meaning and small enough to cite in a benchmark sample.

Good fragment candidates:

- a lesson section;
- a worked example;
- a table or figure with caption;
- an exercise or task prompt;
- a short conceptual explanation.

Avoid fragments that are:

- only a heading without content;
- so broad that they span unrelated concepts;
- machine-OCR chunks without human-readable location notes.

## Multi-page fragments

If content spans pages, keep one fragment and record `page_start` and `page_end`. Do not create separate fragments just because of a page break.

## Multiple fragments on one page

Use separate `#F0001`, `#F0002`, etc. Store the reading order in `order_index`. If a new fragment is inserted later, do not renumber existing confirmed fragments.

## Review status

- OCR-only fragments start as `draft` or `needs_uet_review`.
- Pedagogically meaningful segmentation should be `needs_hnmu_review` until HNMU confirms it.
- Retire fragments rather than changing the meaning of an existing confirmed ID.
