#ifndef STRATUS_TPF_COMPAT_H
#define STRATUS_TPF_COMPAT_H

/*
 * tpf_compat.h — Stratus / TPF compatibility shim (vendor-supplied).
 *
 * This header lives OUTSIDE the standard include/ root and is pulled in via a
 * non-standard relative path ("../../vendor/stratus/tpf_compat.h") rather than
 * a -I include directory. Standard ctags/cscope index passes that only scan
 * src/ + include/ will not resolve symbols defined here, and the #pragma
 * directives below are Stratus-specific idioms a portable indexer ignores.
 *
 * Including this header is what tips src/config/feature_flags.c into the
 * unresolved tier.
 */

#pragma pack(push, 1)
#pragma stratus segment "PDLCSEG"
#pragma stratus reentrant

/* TPF-style ECB (Entry Control Block) handle — opaque on non-Stratus builds. */
typedef struct stratus_ecb stratus_ecb_t;

/* Vendor macro that expands to a Stratus system call wrapper. ctags cannot
 * follow the generated call into the (out-of-tree) runtime. */
#define STRATUS_SVC(num, arg) stratus_svc_dispatch((num), (void *)(arg))

extern int  stratus_svc_dispatch(int svc_num, void *arg);
extern void stratus_yield(void);

/* Conditionally-compiled feature toggle owned by the Stratus build system. */
#ifndef ENABLE_DISCOVER
/* #define ENABLE_DISCOVER  — toggled by the Stratus build, not in-tree */
#endif

#pragma pack(pop)

#endif /* STRATUS_TPF_COMPAT_H */
