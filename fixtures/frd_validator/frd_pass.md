<!-- frd_validator fixture: PASS case (TASK-045).
     Identical to the TASK-044 frd_author output — see fixtures/frd_author/expected_frd.md.
     Maps to core/scripts/frd_validator.py _demo() PASS case: score 100, eligible=True.

     All 8 frd_profile topics trace validly to real BRD v1 anchors and carry their testability
     artifact (acceptance criteria for actor_flow/system_behavior/data_contract/error_state; a
     measurable target for nfrs.certification). Every BRD requirement is traced or out-of-scope:
       traced:       business_context.{mandate,brand_rules}, scope_objectives.card_brand,
                     requirements.certification, code_impact.{routing,settlement},
                     success_metrics.reporting
       out-of-scope: requirements.interchange_fees, constraints_assumptions.compliance_deadline
     → traceability=1.0, testability=1.0, score=100, coverage_ok=True → eligible=True.

     The full FRD markdown (header pin v1, system_behaviors with file/function detail, the
     <!-- traces: {...} --> block) is fixtures/frd_author/expected_frd.md; it is not duplicated here. -->
