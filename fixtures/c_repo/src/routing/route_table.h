#ifndef PDLC_ROUTE_TABLE_H
#define PDLC_ROUTE_TABLE_H

#include "txn.h"
#include "brand.h"

/*
 * route_table.h — the dispatch-table interface (src/routing/route_table.c).
 *
 * The table maps a brand_id to a handler vtable. route_via_table() indexes
 * into the table and invokes `entry->route(txn)` through a function pointer.
 * ctags/cscope can see the table array and route_via_table(), but cannot
 * resolve which concrete handler `entry->route` calls — this is the routing
 * -> transaction cross-module edge that merge_edges cannot fully stitch.
 */

typedef struct route_entry {
    brand_id_t             brand;
    const brand_handler_t *handler;
} route_entry_t;

int route_via_table(txn_t *t);
int route_table_install(brand_id_t brand, const brand_handler_t *h);

#endif /* PDLC_ROUTE_TABLE_H */
