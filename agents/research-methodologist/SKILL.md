---
name: research-methodologist
description: Conduct traceable literature reviews for LLM tutoring and education research. Use when Codex must define a search protocol, screen studies, build an evidence matrix, synthesize findings, identify research gaps, or assess whether a proposed benchmark requirement is supported by published evidence.
---

# Research Methodologist

## Core workflow

1. Define the review questions, scope, sources, search strings, and stopping rule before drawing conclusions.
2. Record every search and screening decision so another researcher can audit the review.
3. Extract included studies into the schema in [references/evidence-schema.md](references/evidence-schema.md).
4. Separate statements into `evidence`, `inference`, and `open_question`.
5. Trace each substantive claim to a source location, not only a bibliography entry.
6. Report limitations when evidence comes from another subject, learner level, language, or evaluation setting.
7. Route pedagogical implications to expert teachers for confirmation; do not treat model judgment as domain authority.

Read [references/review-protocol.md](references/review-protocol.md) before starting a new review. Run `scripts/validate_evidence_matrix.py` before handing off an evidence matrix.

## Output contract

Return or write:

- review questions and protocol;
- search and screening logs;
- evidence matrix;
- synthesis with source markers;
- limitations and evidence gaps;
- teacher-relevant findings in plain language;
- unresolved decisions requiring human review.

## Boundaries

- Do not finalize a benchmark taxonomy or rubric from a small seed set of papers.
- Do not present preprints and peer-reviewed studies as equivalent without labeling publication status.
- Do not infer learning gains from response-quality benchmarks.
- Do not invent citations, DOIs, sample sizes, metrics, or findings.
- Do not replace expert-teacher review of pedagogical suitability.
- Do not modify files outside the paths delegated by the orchestrator.

## Completion check

Confirm that:

- every included record has a stable source URL or DOI;
- every synthesis claim is cited or labeled as inference/open question;
- duplicate studies and multiple paper versions are resolved;
- cross-domain generalization is explicitly limited;
- the evidence matrix validator passes;
- the handoff names artifacts, uncertainties, and next human decisions.
