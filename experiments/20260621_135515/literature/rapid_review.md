# F01 rapid evidence review

## Status and scope

This expanded rapid review searched literature through 2026-06-21. It is not
a full systematic review. The merged screening log contains more than 50
unique candidates and the evidence matrix contains 28 core records.

The review covers:

1. LLM/AI tutoring benchmarks;
2. feedback, scaffolding, hinting, learner-state diagnosis and multi-turn
   tutoring;
3. programming education, misconceptions and debugging feedback;
4. human rubric design and inter-rater reliability;
5. automatic evaluation and LLM-judge validity/bias;
6. multilingual, low-resource and middle-school evidence.

## Main findings

### Evidence: solving is not tutoring

Strong answer-generation or problem-solving performance does not imply strong
tutoring. MathDial, MRBench, MathTutorBench, TutorBench and programming-hint
studies all report gaps between subject correctness and pedagogical support
[LIT-002, LIT-005, LIT-006, LIT-007, LIT-015].

### Evidence: analytic criteria are preferable

The recurring observable dimensions are:

- subject-matter correctness;
- recognition of the learner's current state or error;
- correct issue localization;
- useful guidance and an actionable next step;
- coherence with the prompt, work and dialogue history;
- appropriate calibration to level and context;
- preservation of learner agency;
- avoidance of premature complete solutions;
- clarity, safety and fairness.

Agreement varies substantially by criterion. MRBench reported stronger
criterion-level reliability than several broader LearnLM constructs, whose
Krippendorff alpha values ranged from near zero/negative to about .66
[LIT-005, LIT-020]. A single total score would hide this variation.

### Evidence: generic automatic metrics are insufficient

Text-overlap and generic dialogue metrics can reward surface similarity or
complete answers rather than productive tutoring [LIT-003]. LLM judges can
approximate human preferences in some settings but exhibit order, verbosity,
self/family preference, prompt and language-resource biases
[LIT-022, LIT-023, LIT-024, LIT-025].

Automatic evaluation is therefore auxiliary. Curriculum fit, pedagogical
appropriateness and ambiguous partial performance remain teacher decisions.

### Evidence: programming feedback needs negative controls

Programming systems may correctly localize or repair an error without
providing useful tutoring [LIT-011, LIT-012]. Models can also fabricate issues
in correct code or suggest unnecessary changes [LIT-016, LIT-018].

Programming tasks should include:

- correct work as a negative control;
- multiple valid solution paths;
- teacher-approved expected behavior/test evidence;
- explicit environment constraints;
- a separate answer-revelation flag;
- one next tutor response rather than a hidden repaired solution.

### Evidence: multi-turn quality includes learner uptake

Longer dialogue is more difficult, and static scoring of one tutor turn misses
whether the learner follows, bypasses or meaningfully uses the support
[LIT-006, LIT-009, LIT-010]. Uptake is informative but is not itself a
learning outcome.

### Evidence: expert teachers are structural, not optional

Across the included studies, experts author examples, define taxonomies,
create rubrics, calibrate raters, annotate responses and adjudicate
disagreement [LIT-002, LIT-004, LIT-005, LIT-007, LIT-019, LIT-020,
LIT-021]. F01 therefore keeps independent teacher review and adjudication as
mandatory gates.

## Implications for the candidate task framework

### Stronger direct evidence

The literature directly supports these candidate tasks:

1. adaptive concept explanation;
2. feedback on student reasoning;
3. algorithm construction with incremental hints;
4. algorithm/program diagnosis and repair support.

### Provisional low-evidence transfer

These curriculum-relevant tasks have weaker direct tutoring-benchmark
evidence and must remain `provisional_low_evidence`:

1. digital information or conduct decision support;
2. digital product/simulation planning and review;
3. career exploration without stereotyping.

They may be piloted for curriculum coverage but must not be presented as
validated task families.

## Rubric scale

The literature uses binary, three-level, five-level and pairwise judgments.
No included source validates F01's six-level `0-5` scale for Vietnamese
Grade-9 Informatics. The scale is therefore a project design choice requiring
teacher calibration.

Primary reporting should use the vector of criterion scores. `N/A` remains
separate. Critical failures are flags and cannot be offset by a high average.
Weights and pass thresholds remain unset.

## Research gaps

- No direct validated Vietnamese Grade-9 Informatics tutoring benchmark.
- Sparse evidence for digital products, digital conduct and career guidance.
- Most tutoring studies are English mathematics.
- Most programming studies involve university learners and executable code.
- Limited validation of multilingual educational LLM judges.
- Simulated learners may not reproduce authentic misconceptions/help-seeking.
- Response quality and immediate uptake do not establish learning gains.

## Teacher-relevant findings

Teachers need to decide:

1. which content and terminology are appropriate for Grade 9;
2. what counts as a useful hint versus excessive solution disclosure;
3. valid alternative algorithms and representations;
4. the `0-5` anchor for each criterion;
5. which errors are critical failures;
6. how disagreements are adjudicated;
7. whether weak-reliability criteria are revised, merged or retained only as
   qualitative notes.

## Audit notes

The orchestrator rechecked metadata/abstract evidence for MathDial, MRBench,
MathTutorBench, TutorBench, LearnLM's evaluation framework, MM-Eval, the
programming-hint benchmark by Phung et al., and the logic-error study by
MacNeil et al. against primary ACL Anthology or arXiv records.

## References

The canonical bibliography is the `evidence_matrix.csv` URL/DOI column.
Reference IDs `LIT-001` through `LIT-028` are stable within F01.
