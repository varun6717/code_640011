/*
 * feature_flags.c — build-time feature toggles + Stratus registration.
 * (Tier 3, coverage: coarse / unresolved)
 *
 * EXTRACTOR HAZARDS (two, compounded):
 *   1. #ifdef conditional compilation: entire registration blocks are guarded
 *      by ENABLE_DISCOVER / ENABLE_STRATUS_SVC. A static indexer does not know
 *      which branches the Stratus build activates, so the symbols and calls
 *      inside inactive branches are neither indexed nor traceable.
 *   2. Non-standard Stratus include: tpf_compat.h is pulled via a relative
 *      path that escapes the src/ + include/ index roots, so STRATUS_SVC()
 *      and stratus_svc_dispatch() resolve to nothing in the index.
 *
 * Net: this file's registrations cannot be reliably extracted -> it is one of
 * the files_unresolved in coverage_report.
 */

#include "brand.h"
#include "errors.h"
#include "common.h"

/* Non-standard include path: escapes the index roots (src/, include/). */
#include "../../vendor/stratus/tpf_compat.h"

/* Forward decls of macro-generated handlers (see config/brand_rules.c). */
int visa_route(txn_t *t);
int mastercard_route(txn_t *t);
int amex_route(txn_t *t);
#ifdef ENABLE_DISCOVER
int discover_route(txn_t *t);
#endif

int feature_register_brands(void)
{
    int rc = PDLC_OK;

    /* Always-on brands. */
    PDLC_LOG("cfg", "registering core brands");

#ifdef ENABLE_STRATUS_SVC
    /* Stratus-only registration path: invisible to a portable indexer. */
    rc = STRATUS_SVC(0x41, visa_route);
    rc = STRATUS_SVC(0x42, mastercard_route);
    rc = STRATUS_SVC(0x43, amex_route);
#else
    PDLC_UNUSED(visa_route);
    PDLC_UNUSED(mastercard_route);
    PDLC_UNUSED(amex_route);
#endif

#ifdef ENABLE_DISCOVER
    /* Entire Discover enablement block is conditionally compiled. */
    rc = STRATUS_SVC(0x44, discover_route);
    stratus_yield();
#endif

    return rc;
}
