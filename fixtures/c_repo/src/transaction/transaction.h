#ifndef PDLC_TRANSACTION_H
#define PDLC_TRANSACTION_H

#include "txn.h"

/*
 * transaction.h — internal interfaces of the transaction module beyond the
 * lifecycle entry points declared in txn.h. The per-phase handlers here are
 * the concrete targets that route_table.c's function pointers eventually
 * reach at runtime (but which static analysis cannot link from the table).
 */

/* Concrete brand-agnostic phase handlers. */
int auth_handle(txn_t *t);       /* src/transaction/auth_handler.c    */
int capture_handle(txn_t *t);    /* src/transaction/capture_handler.c */
int settle_handle(txn_t *t);     /* src/transaction/settle_handler.c  */

#endif /* PDLC_TRANSACTION_H */
