# Makefile — stub build for the synthetic Stratus merchant-routing-svc fixture.
#
# This is a *fixture*, not a shippable service: the bodies reference an
# out-of-tree Stratus runtime and are not expected to link. The Makefile
# exists so the tree is a plausible single-repo clone target and so language
# detection (TASK-008) has a build-manifest signal that this is a C repo.
#
# It is intentionally NOT required to build for the extractor (TASK-009),
# which reads syntax via ctags/cscope, not compiled objects.

CC      ?= cc
CFLAGS  ?= -std=c99 -Wall -Iinclude
SRC     := $(shell find src -name '*.c')
OBJ     := $(SRC:.c=.o)

.PHONY: all tags clean
all: $(OBJ)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Generate ctags/cscope indexes the extractor wraps (scans src + include only;
# vendor/ is deliberately excluded, mirroring the real Stratus -I convention).
tags:
	ctags -R --c-kinds=+p --fields=+S src include
	cscope -bR -s src -s include

clean:
	rm -f $(OBJ) tags cscope.out
