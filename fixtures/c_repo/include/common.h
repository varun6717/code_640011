#ifndef PDLC_COMMON_H
#define PDLC_COMMON_H

#include <stddef.h>
#include <string.h>
#include <stdint.h>

/*
 * common.h — shared utility macros. The function-like macros here are simple
 * (expression macros), so they do NOT defeat the extractor on their own; the
 * macro hazard lives in src/config/brand_rules.c, which uses a token-pasting
 * macro that *generates whole functions*.
 */

#define PDLC_ARRAY_LEN(a)   (sizeof(a) / sizeof((a)[0]))
#define PDLC_UNUSED(x)      ((void)(x))
#define PDLC_MIN(a, b)      ((a) < (b) ? (a) : (b))
#define PDLC_MAX(a, b)      ((a) > (b) ? (a) : (b))

/* Bounded field accessor used by the messaging + settlement modules. */
#define FIELD_OR(msg, idx, dflt) \
    ((msg)->fields[(idx)] ? (msg)->fields[(idx)] : (dflt))

/* Lightweight logging stub (no-op in the fixture). */
#define PDLC_LOG(tag, fmt, ...)  do { (void)(tag); } while (0)

#endif /* PDLC_COMMON_H */
