/*
 * retry.c — bounded retry with backoff. (Tier 1, coverage: deep)
 *
 * NOTE on the indirect call: retry_with_backoff() invokes a caller-supplied
 * `op` through a function pointer. This is a *generic utility* callback (the
 * target is whatever the caller passes), so there is no concrete intra-repo
 * edge the map should have linked — it is NOT counted as an unresolved
 * dependency. Contrast with route_table.c, where a *stored* pointer is wired
 * to a known in-tree handler the map ought to link but cannot (Tier 2).
 */

#include "errors.h"
#include "common.h"

int retry_with_backoff(pdlc_op_fn op, void *ctx, int max_attempts)
{
    int attempt;
    int rc = PDLC_ERR_CONFIG;

    if (!op || max_attempts <= 0)
        return PDLC_ERR_CONFIG;

    for (attempt = 0; attempt < max_attempts; attempt++) {
        rc = op(ctx);                         /* generic callback, not a tracked edge */
        if (rc == PDLC_OK)
            return PDLC_OK;
        if (!is_retryable((pdlc_status_t)rc)) /* -> errors/error_codes */
            return rc;
        /* a real impl would sleep with exponential backoff here */
    }
    return PDLC_ERR_RETRY_EXHAUSTED;
}
