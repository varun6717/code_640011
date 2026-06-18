/*
 * capture_handler.c — capture-phase handler. (Tier 1, coverage: deep)
 */

#include "txn.h"
#include "transaction.h"
#include "errors.h"
#include "common.h"

int capture_handle(txn_t *t)
{
    if (!t)
        return PDLC_ERR_CONFIG;
    if (!(t->flags & TXN_FLAG_RETRYABLE))
        return PDLC_ERR_ROUTE_FAILED;   /* must be authorized first */

    t->last_status = PDLC_OK;
    return PDLC_OK;
}
