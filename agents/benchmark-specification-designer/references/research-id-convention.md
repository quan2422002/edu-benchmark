# Research ID convention v0

Prefer stable natural IDs from the source.

## arXiv

For files such as:

```text
2510.02663v1.pdf
2502.18940v2.pdf
```

Use:

```text
RS-ARXIV-2510-02663-V1
RS-ARXIV-2502-18940-V2
```

Use the versionless form only when referring to the logical paper across versions:

```text
RS-ARXIV-2510-02663
```

## DOI

For DOI-based sources, normalize with uppercase, replace `/` and punctuation that break IDs with hyphens, and preserve the DOI in a separate source field:

```text
RS-DOI-10-1145-EXAMPLE
```

## Other sources

When no DOI/arXiv/OpenReview ID exists, use:

```text
RS-<FIRSTAUTHOR>-<YEAR>-<TITLEKEY>
```

If two IDs collide, append `-A`, `-B`, etc. Record the original citation and URL in the evidence matrix.

## Rules

- Never invent a DOI, arXiv ID, sample size, or publication status.
- Keep the source citation and URL/DOI in the research artifact; IDs are lookup keys.
- Mark publication status separately from the ID.
