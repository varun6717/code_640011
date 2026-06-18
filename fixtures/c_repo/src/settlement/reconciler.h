#ifndef PDLC_RECONCILER_H
#define PDLC_RECONCILER_H

#include "txn.h"

/*
 * reconciler.h — settlement reconciliation interface.
 * reconcile_txn() is the middle node of the scope_ripple chain: it is called
 * by routing/brand_router.c and it calls messaging/formatter.c
 * (format_settlement_msg) — both clean Tier-1 edges.
 */

int reconcile_txn(txn_t *t);
int reconcile_close_window(int window_id);

#endif /* PDLC_RECONCILER_H */
