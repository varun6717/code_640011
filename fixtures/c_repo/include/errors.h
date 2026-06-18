#ifndef PDLC_ERRORS_H
#define PDLC_ERRORS_H

/*
 * errors.h — canonical status codes and the retry/fallback API.
 *
 * retry_with_backoff() takes a function-pointer operation argument; the
 * indirect call through `op` is another site cscope cannot resolve to a
 * concrete target (see src/errors/retry.c).
 */

typedef enum pdlc_status {
    PDLC_OK                 = 0,
    PDLC_ERR_BRAND_UNKNOWN  = 1001,
    PDLC_ERR_ROUTE_FAILED   = 1002,
    PDLC_ERR_SETTLE_DECLINED= 1003,
    PDLC_ERR_MSG_MALFORMED  = 1004,
    PDLC_ERR_TIMEOUT        = 1005,
    PDLC_ERR_RETRY_EXHAUSTED= 1006,
    PDLC_ERR_CONFIG         = 1007
} pdlc_status_t;

/* Generic retryable operation signature. */
typedef int (*pdlc_op_fn)(void *ctx);

const char    *pdlc_strerror(pdlc_status_t s);
int            retry_with_backoff(pdlc_op_fn op, void *ctx, int max_attempts);

/* Map a hard error to a fallback disposition (src/errors/fallback.c). */
pdlc_status_t  error_fallback(pdlc_status_t s);
int            is_retryable(pdlc_status_t s);

#endif /* PDLC_ERRORS_H */
