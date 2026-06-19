#ifndef ROUTER_H
#define ROUTER_H

/* Public routing interface — the majority C surface of mixed_repo. */

typedef struct txn txn;

int  route_transaction(const txn *t);
void register_brand(const char *brand);

#endif /* ROUTER_H */
