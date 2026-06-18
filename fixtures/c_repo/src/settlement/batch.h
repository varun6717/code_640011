#ifndef PDLC_SETTLEMENT_BATCH_H
#define PDLC_SETTLEMENT_BATCH_H

#include "txn.h"

/*
 * batch.h — settlement batching + ledger posting interfaces.
 * (src/settlement/settlement_batch.c, src/settlement/ledger_post.c)
 */

typedef struct settle_batch {
    int   window_id;
    int   count;
    uint64_t total_minor;
} settle_batch_t;

int batch_add(settle_batch_t *b, const txn_t *t);
int batch_flush(settle_batch_t *b);

/* Ledger posting (src/settlement/ledger_post.c). */
int ledger_post(const txn_t *t);

#endif /* PDLC_SETTLEMENT_BATCH_H */
