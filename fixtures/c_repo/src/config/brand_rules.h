#ifndef PDLC_BRAND_RULES_H
#define PDLC_BRAND_RULES_H

#include "brand.h"

/*
 * brand_rules.h — brand rule-table lookup.
 *
 * get_brand_rule() is a clean, resolvable symbol (the depends_on edge from
 * routing/brand_router.c lands here). But brand_rules.c ALSO uses the
 * DECLARE_BRAND_HANDLER() token-pasting macro to generate one route function
 * per brand (e.g. visa_route, discover_route). Those generated functions are
 * invisible to ctags, so the file's real interface is under-reported and the
 * file is classified coverage:coarse / unresolved.
 */

typedef struct brand_rule {
    brand_id_t brand;
    int        max_retries;
    int        requires_3ds;     /* 3-D Secure required */
    int        settle_window_s;  /* settlement window in seconds */
} brand_rule_t;

const brand_rule_t *get_brand_rule(brand_id_t brand);

#endif /* PDLC_BRAND_RULES_H */
