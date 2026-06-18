#ifndef PDLC_CODEC_H
#define PDLC_CODEC_H

#include "message.h"

/*
 * codec.h — per-field codec table interface (src/messaging/field_codec.c).
 *
 * The codec table holds a function pointer per ISO 8583 field number. The
 * encode/decode dispatch goes through `codec_table[field].encode(...)`,
 * which the extractor cannot resolve to a concrete encoder (Tier 2). The
 * field codec table is wired up at module init.
 */

typedef int (*field_encode_fn)(const iso_msg_t *m, int field, char *buf, int len);
typedef int (*field_decode_fn)(iso_msg_t *m, int field, const char *raw, int len);

typedef struct field_codec {
    int             field;
    field_encode_fn encode;
    field_decode_fn decode;
} field_codec_t;

int codec_register(int field, field_encode_fn enc, field_decode_fn dec);

#endif /* PDLC_CODEC_H */
