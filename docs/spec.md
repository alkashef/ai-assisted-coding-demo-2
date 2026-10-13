# Spec — ai-assisted-coding-demo-2

Status: Draft

What to build. Written with `/write-spec`. Change only with the user's approval. Each requirement is
in EARS syntax and has an ID that tests cite.

## 1. Purpose and scope

An app that takes a folder of CVs/resumes in PDF format and extracts information from each one. The user enters a search criteria. The app finds and ranks the best matching CVs. The search must be intelligent and semantic, not only keyword matching. This is a demo light-weight app.

Record the business problem, affected people, current workaround, desired
improvement, in-scope work, exclusions, and binding constraints.
Record how the business outcome will be evaluated when applicable.

## 2. Roles and glossary

Define the relevant user roles, decision-makers, and ambiguous domain terms.

## 3. User scenarios

For each `SCN-NNN`, record:

- Actor and goal
- Trigger and preconditions
- Main success path
- Relevant alternate paths and failure paths
- Observable result
- Source and confirmation status

## 4. Functional requirements

| ID | EARS requirement | Priority | Status | Business reason | Source | Scenarios | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- |

Use `AREA-NNN` for IDs, for example `PAY-001`. Distinguish Proposed, Confirmed, and Withdrawn
requirements. A confirmed requirement still needs the spec approval before implementation.

## 5. Non-functional requirements

| ID | EARS requirement | Priority | Status | Business reason | Source | Acceptance evidence |
| --- | --- | --- | --- | --- | --- | --- |

Use `NFR-NNN` for IDs. State the relevant workload, conditions, and measurable acceptance limits.
Keep unknown limits in the open questions. Do not invent values.

## 6. Acceptance examples

| ID | Requirement IDs | Situation and input | Expected result | Reviewed by |
| --- | --- | --- | --- | --- |

Record the actual reviewer or mark the example as awaiting review.
Link rules by ID instead of repeating their text.

## 7. Assumptions and open questions

| Item | Evidence or assumption | Consequence if wrong | Owner | Resolution or revisit condition |
| --- | --- | --- | --- | --- |

Identify what each material unresolved question blocks.
Record deliberately deferred decisions with their limits.

## 8. Review and approval

Record the actual approval, its scope, and remaining exclusions when it occurs.
Do not prefill approval or treat silence as consent. When the spec is approved, change `Status`
to `Approved`.

For amendments, record the approved change and affected IDs here. Preserve IDs and withdrawn rows.
