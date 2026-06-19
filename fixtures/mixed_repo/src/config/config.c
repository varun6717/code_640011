#include "config.h"

static brand_rule rules[8];

/* Looks up the brand rule for a transaction. */
const brand_rule *get_brand_rule(const txn *t)
{
    (void)t;
    return &rules[0];
}

void set_brand_enabled(const char *brand, int enabled)
{
    (void)brand;
    (void)enabled;
}
