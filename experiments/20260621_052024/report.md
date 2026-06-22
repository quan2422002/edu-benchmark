# C01 implementation report

## Status

`AWAITING_EXPERT_TEACHER_REVIEW`

C01 has completed curriculum grounding, workbook inspection, example-type classification and authoring of the project-lead-approved provisional set. The remaining acceptance gate is independent expert-teacher review.

## Sources reviewed

Both specialists reviewed:

1. the Grade-9 Informatics curriculum issued with Circular 32/2018/TT-BGDĐT;
2. the 2019 BGDDT/HNUE explanatory curriculum guide;
3. the workbook only as an internal draft reference.

The normative Grade-9 requirements were located on printed pages 37–40. The explanatory guide confirms that teaching materials and assessment must reference learning requirements and respect the stated action/level to avoid over-demanding students.

## Artifacts created

- source registry with authority roles;
- focused Grade-9 reference matrix;
- reference contract;
- workbook field/audit notes;
- sample data template;
- example coverage proposal;
- teacher review questions;
- append-only coordination events and specialist handoffs.

## Workbook findings

- 160 unique item IDs; 40 Grade-9 items.
- Grade 9: 12 DL, 12 ICT, 16 CS.
- All Grade-9 item statuses are `draft_v1`.
- All Grade-9 expert-review and pilot fields are empty.
- `Expert_Form` currently matches Item Bank on displayed fields but is a static snapshot.
- Workbook fields and examples are useful references but do not establish curriculum alignment, correctness, difficulty or rubric validity.
- Workbook SHA-256 remained `2CDAF31FF65B2BA65A4C167E97AAF9568A13795E14E39B847CE13C3D4E654001`.

## Coverage proposal

Eight core example types:

1. explain a Grade-9 concept;
2. evaluate information or digital conduct;
3. give feedback on student reasoning;
4. plan a digital activity/product;
5. review a digital product/simulation result;
6. construct an algorithm;
7. diagnose an algorithm/program;
8. explore career fit without stereotyping.

One conditional module:

9. repair an earlier-THCS prerequisite that blocks a Grade-9 target.

Proposed core sizes:

- minimum: 18;
- better coverage: 29.

Optional advanced-spreadsheet and video topics are excluded from the core until local selection is confirmed.

## Project-lead decision

Approved on 2026-06-21:

- Types 1–8: `2, 3, 2, 2, 2, 3, 2, 2`;
- total: 18 core examples;
- Type 9: excluded;
- optional advanced-spreadsheet and video topics: excluded;
- unspecified tools/programming environment: examples remain tool-neutral.

## Examples created

- 18 samples: `C01-S001` through `C01-S018`.
- Exact approved type distribution is satisfied.
- Every sample has at least one curriculum reference.
- Every sample has three rubric criteria:
  - curriculum-content criterion: `supported`;
  - tutoring-behavior criterion: `provisional`, pending P02;
  - local/pedagogical criterion: `teacher_judgment`.
- No sample is presented as teacher-approved.

## Validation

- source IDs and reference IDs are unique;
- every reference row points to a known source;
- curriculum rows contain page and location information;
- sample template contains the required reference and teacher-judgment fields;
- coordination JSONL contains required event fields;
- all four delegation handoffs exist;
- 18 sample IDs are sequential and unique;
- type counts exactly match `2, 3, 2, 2, 2, 3, 2, 2`;
- 54 rubric criterion IDs are unique;
- every curriculum reference used by a sample exists in the reference matrix;
- workbook hash is unchanged;
- no file under `document/` was modified;
- `git diff --check` passes for the experiment.

Validation executable:

`D:\conda-envs\benchmark_env\python.exe`

Workbook reader:

`openpyxl==3.1.5`

## Review required

Independent expert teachers must review all 18 samples and record `accept`, `revise` or `reject` with rationale. C01 remains running until that review and any recorded revisions are complete.
