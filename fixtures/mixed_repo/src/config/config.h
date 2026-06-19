#ifndef CONFIG_H
#define CONFIG_H

#include "../routing/router.h"

typedef struct brand_rule {
    int handler_id;
} brand_rule;

const brand_rule *get_brand_rule(const txn *t);
void set_brand_enabled(const char *brand, int enabled);

#endif /* CONFIG_H */
