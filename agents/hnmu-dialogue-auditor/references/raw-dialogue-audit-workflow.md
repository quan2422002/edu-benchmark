# Raw dialogue audit workflow

This workflow is for auditing raw HNMU dialogue samples before benchmark conversion.

## 1. Prepare the audit shard

Use only the sample IDs or shard delegated by the orchestrator. Check that each row has the fields needed for raw-data auditing, usually:

- class/grade;
- lesson or lesson position;
- student question;
- cognitive level;
- SGV answer or expected answer field;
- raw tutoring dialogue;
- row provenance from the HNMU source file.

If the row is structurally incomplete, record that as checklist evidence instead of inventing missing content.

## 2. Resolve learning-resource evidence

Use the learning-resource context and retrieval tools before reading large Markdown files manually.

Preferred order:

1. exact grade + SGK/SGV + lesson/page filters;
2. lesson title + keyword search;
3. broader keyword search within the same grade and book type;
4. mark `uncertain` if retrieval cannot find a reliable fragment. If a fragment is still `draft` but clearly matches the grade/lesson/page/keywords and content under review, treat draft status as traceability metadata, not as an automatic reason for `uncertain`.

Remember: SGK is mainly used for topic, lesson, student question, and scope checks. SGV is mainly used for answer/explanation checks.

## 3. Evaluate criteria independently

Do not collapse several criteria into one global judgment. For each criterion:

- state the criterion ID and name;
- decide `pass`, `fail`, `uncertain`, or `not_applicable`;
- cite the fragment ID or raw field evidence if available;
- give a concise reason;
- suggest a reviewer action when the decision is not a clean pass.

## 4. Scaffolding checks

Use `shared/learning_resources/agent_context/hnmu_scaffolding_method_canonical.md` as the canonical HNMU scaffolding reference. Look for evidence of support such as prompting, marking important features, reducing support gradually, or guiding the learner without jumping straight to the final answer.

A raw sample can have weak scaffolding and still be useful later, but it should be flagged clearly.

Keep the scaffolding-related criteria separate:

- `RAW-PED-01` checks whether there is any scaffolding signal at all.
- `RAW-PED-02` checks whether the tutor reveals the final answer, formula, or full solution too early. It is acceptable to state or confirm the answer after enough guidance, learner response, or closing support has happened.
- `RAW-PED-03` checks whether the dialogue sequence is coherent across turns, not merely whether one turn contains a scaffolding phrase.
- `RAW-PED-04` checks for low-value turns within the same learning path, such as generic praise, repetition, or turns that add no feedback, prompt, correction, or next learning step.
- `RAW-PED-06` checks avoidance or off-task redirection: the tutor replaces support with content unrelated to the learner's request, lesson, or question.

## 5. Confidence scoring

Confidence is criterion-level, not sample-level. Lower confidence when:

- the relevant SGK/SGV fragment is missing, weakly matched, or ambiguous;
- the raw row metadata conflicts with dialogue content;
- the dialogue is too short to judge scaffolding;
- the SGV answer is vague or copied without enough context;
- the sample needs expert teacher interpretation.

## 6. Aggregate only after detailed rows exist

After completing detailed checklist rows, propose sample-level outcomes:

- pass for conversion only when all criteria are `pass` or `not_applicable`;
- needs HNMU/UET review when at least one criterion is `uncertain` and none is `fail`;
- failed/exclude from the current batch when at least one criterion is `fail`.

These are suggestions, not final decisions.

The aggregation must be mechanical and auditable:

1. detailed checklist rows first;
2. sample-level decision from criterion results;
3. sample-level confidence from the criteria that triggered the decision;
4. review queue from every non-pass sample.

Do not mark a sample as pass if any required criterion is `uncertain` or `fail`.

## 7. Stop conditions

Stop and report to the orchestrator if:

- delegated write paths are unclear;
- required checklist or learning-resource context files are missing;
- many samples fail because of a shared schema mismatch;
- retrieval evidence is systematically unavailable for the grade/book being audited.
