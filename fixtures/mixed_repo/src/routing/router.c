#include "router.h"
#include "../config/config.h"

/* Routes a transaction to the correct card-brand handler. */
int route_transaction(const txn *t)
{
    const brand_rule *rule = get_brand_rule(t);
    if (rule == 0) {
        return -1;
    }
    return rule->handler_id;
}

void register_brand(const char *brand)
{
    set_brand_enabled(brand, 1);
}
