# Expected ordered section plan — `brd_author` merge proof (TASK-037)

Proof for the deterministic baseline+profile merge (D2) in
`core/skills/brd_author.skill.md` § "Merge — baseline + profile".

**Inputs**
- Baseline skeleton (inline in the skill): the nine universal sections, skeleton only.
- Profile: `core/profiles/payment_brand/brd_profile.payment_brand.yaml` (TASK-015).

**Merge trace**
1. Start from baseline skeleton (orders 10–80 + `executive_summary` pinned last).
2. Deep-merge profile entries by `id`:
   - `business_context` (10), `scope_objectives` (20), `requirements` (50),
     `success_metrics` (60) — `position: null` → keep baseline order; profile supplies
     `sources` + `requirements`.
   - `constraints_assumptions` (70) — same, and profile **raises** `required` `false → true`.
3. Insert net-new `code_impact` at `position: "after:requirements"` → between `requirements`
   (50) and `success_metrics` (60).
4. Baseline sections untouched by the profile keep their skeleton (no `requirements`):
   `stakeholders` (30), `current_state` (40), `out_of_scope` (80).
5. `executive_summary` pinned last, drafted last.

**Expected ordered authoring plan (the iteration order)**

| # | id                       | required | sources                | topics (implicit) |
|---|--------------------------|----------|------------------------|-------------------|
| 1 | business_context         | yes      | confluence, sharepoint | mandate, brand_rules |
| 2 | scope_objectives         | yes      | confluence, sharepoint | card_brand |
| 3 | stakeholders             | yes      | —                      | — |
| 4 | current_state            | no       | —                      | — |
| 5 | requirements             | yes      | confluence, sharepoint | certification, interchange_fees |
| 6 | code_impact              | yes      | bitbucket              | routing, settlement |
| 7 | success_metrics          | no       | confluence, sharepoint | reporting |
| 8 | constraints_assumptions  | yes ↑    | confluence, sharepoint | compliance_deadline |
| 9 | out_of_scope             | yes      | —                      | — |
|10 | executive_summary        | yes      | —                      | — (draft LAST) |

**Checks demonstrated**
- Generic engine: no domain content in the skill; all topics/`must_capture` come from the profile (FR-BR-01).
- Merge per D2: deep-merge by `id`, net-new insert by `position`, `required` raised not lowered.
- `executive_summary` pinned last and drafted last (FR-BR-02).
- `code_impact` ordered after `requirements` and before `success_metrics` via `after:requirements`.
