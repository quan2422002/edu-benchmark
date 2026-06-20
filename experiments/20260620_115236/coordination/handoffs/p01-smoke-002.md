# Specialist handoff

- Delegation ID: `p01-smoke-002`
- Agent: `teacher-collaboration-designer`
- Status: completed with revision required
- Native thread ID/label: `019ee393-7461-7703-94f3-0148b6d6e9d4` / Bohr

## Delegation prompt

Create a concise Vietnamese Teacher Author task card with examples and no technical work.

## Follow-up or steer messages

Add an escalation route when curriculum fit is uncertain and keep the card concise.

## Inputs read

- Canonical teacher collaboration skill and task-card schema.
- Provisional authoring requirement supplied inline.

## Outputs created

- Native task-card response.
- This handoff and append-only events.

## Result summary

The output was clear, concise, included positive/negative examples, and added a useful curriculum escalation path. It also exposed two workflow defects: implementation terminology appeared in teacher-facing text, and the author was asked to make reviewer decisions about the same sample.

## Orchestrator decision

Native spawn and interrupt steering passed. Canonical instructions require revision before the behavioral forward test can pass.

## Uncertainty

None about the two identified defects; both conflict with P03 role separation and plain-language principles.

## Open questions and next human decisions

- Re-run a fresh agent after tightening the canonical skill.
