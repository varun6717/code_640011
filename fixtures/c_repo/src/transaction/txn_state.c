/*
 * txn_state.c — transaction phase state machine. (Tier 1, coverage: deep)
 * Pure predicate/mutator helpers; fully resolvable.
 */

#include "txn.h"
#include "errors.h"
#include "common.h"

int txn_advance(txn_t *t, txn_phase_t next)
{
    if (!t)
        return PDLC_ERR_CONFIG;

    /* Only forward transitions are legal. */
    if ((int)next < (int)t->phase)
        return PDLC_ERR_CONFIG;

    t->phase = next;
    if (next == TXN_REFUND)
        t->flags |= TXN_FLAG_REVERSED;
    return PDLC_OK;
}

int txn_is_terminal(const txn_t *t)
{
    if (!t)
        return 1;
    if (t->flags & TXN_FLAG_REVERSED)
        return 1;
    return (t->phase == TXN_SETTLE && (t->flags & TXN_FLAG_SETTLED)) ? 1 : 0;
}
