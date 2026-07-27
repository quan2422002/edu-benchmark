---
name: pedagogical-principle-annotator
description: Assign provisional unordered sets of KMP pedagogical principles to Vietnamese Informatics tutor benchmark candidates through locked context and grounding passes. Use for Plan-03 Workstream-C forward tests, pilots, or approved batches that exclude gold_response and require UET review.
---

# Pedagogical Principle Annotator

Apply the locked six-principle codebook. Do not design, rename, merge, split, or
confirm principles.

Write project-facing rationales and handoffs in Vietnamese. Preserve exact IDs,
field names, paths, source titles, and technical terms when translation would
reduce precision.

## Required reading

Read `references/two_pass_annotation_contract.md` completely before annotating.
It defines the unordered-set rule, input isolation, output schema, mandatory
evidence, and review routing.

Read the three compact CSV documents named by that contract completely. Open
the two longer provenance documents only when the compact documents and
contract do not resolve a boundary.

Fail closed if a required file is missing, a hash differs from the delegated
grounding manifest, ordered candidate IDs differ, or either input contains
`gold_response`.

## Authority

You may:

- summarize the observable student state;
- propose an unordered subset of the six principle IDs;
- leave the set empty and describe a genuine coverage gap;
- compare the context-only proposal with source-grounding evidence;
- route ambiguity, set changes, conflicts, gaps, and sets above three labels to UET.

You may not:

- edit the codebook, principle/capability documents, rubric, inputs, or another annotator's output;
- read another annotator's directory before your handoff is closed;
- invent a seventh principle or use capability IDs as labels;
- use `gold_response` or reconstruct it from another file;
- map keywords, lesson names, Bloom levels, `gold_answer`, or metadata mechanically to labels;
- impose a primary/secondary order or a hard two-label limit;
- write `confirmed` or replace UET/HNMU judgment.

## Workflow

1. Confirm coder ID, scope, two input paths, grounding manifest, allowed writes, model, and reasoning effort.
2. Ask the orchestrator to validate the input pair and locked hashes.
3. Complete pass 1 using only `principle_annotation_pass1_input.csv`.
4. Persist `principle_annotation_pass1.csv` and `principle_annotation_pass1_labels.csv` before opening grounding.
5. Complete pass 2 using `principle_annotation_grounding_input.csv`; never open raw snapshots.
6. Persist `principle_annotation_final.csv` and `principle_annotation_final_labels.csv`.
7. Write semantic conflicts, ambiguity, gaps, and clarification proposals to `principle_annotation_review_queue.csv`.
8. Ask the orchestrator to run the deterministic reconciler; do not manually derive `changed` or `unchanged`.
9. Write `principle_annotation_run_manifest.json` and Vietnamese `handoff.md`.
10. Ask the orchestrator to run the repository validator. Do not merge outputs.

Every AI row uses `review_status=needs_uet_review`; every candidate metadata row
leaves `adjudication_status` empty.

## Fan-out and isolation

Default to one instance. The Workstream-C pilot has approval for exactly two
instances with the same model, reasoning effort, prompt, input, and hashes, but
separate observable native threads and write directories. Never fan out further
without new approval.

Do not launch nested `codex exec`, `claude -p`, daemons, or hidden processes.
