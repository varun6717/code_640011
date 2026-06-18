/*
 * ledger_post.c — posts a settled transaction to the GL ledger.
 * (Tier 1, coverage: deep)
 */

#include "batch.h"
#include "errors.h"
#include "common.h"

/* Minimal in-memory ledger tail; a real impl would write to the GL. */
static uint64_t g_posted_minor;
static int      g_posted_count;

int ledger_post(const txn_t *t)
{
    if (!t)
        return PDLC_ERR_CONFIG;
    if (!(t->phase == TXN_SETTLE))
        return PDLC_ERR_SETTLE_DECLINED;

    g_posted_minor += t->amount_minor;
    g_posted_count++;
    return PDLC_OK;
}
