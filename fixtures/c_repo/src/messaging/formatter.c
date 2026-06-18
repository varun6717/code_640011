/*
 * formatter.c — settlement + transaction message formatting. (Tier 1, deep)
 *
 * format_settlement_msg() is the tail of the scope_ripple chain (called by
 * settlement/reconciler.c). It composes an ISO 8583 message by calling into
 * iso8583.c — all clean, statically-resolvable calls.
 */

#include "message.h"
#include "txn.h"
#include "errors.h"
#include "common.h"

int format_settlement_msg(txn_t *t, char *buf, int len)
{
    iso_msg_t m;

    if (!t || !buf || len <= 0)
        return -1;

    memset(&m, 0, sizeof(m));
    m.mti = 0x0220;                          /* financial advice */
    m.fields[3]  = (char *)"000000";         /* processing code */
    m.fields[4]  = (char *)"settle";         /* amount placeholder */
    m.fields[49] = t->currency;

    return build_iso8583(&m, buf, len);      /* -> messaging/iso8583 (clean) */
}

int parse_iso8583(const char *raw, int len, iso_msg_t *out)
{
    if (!raw || !out || len < 4)
        return PDLC_ERR_MSG_MALFORMED;

    memset(out, 0, sizeof(*out));
    out->mti = (uint16_t)((raw[0] << 8) | raw[1]);
    /* A real parser would walk the bitmap; the fixture stubs the body. */
    return PDLC_OK;
}
