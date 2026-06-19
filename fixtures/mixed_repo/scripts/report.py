"""Residue file (Python) — no frozen extractor, routes to the model fallback (TASK-010).

A small reporting helper that would ship alongside the C service. Its presence makes
mixed_repo polyglot; the dispatcher should map it via model fallback marked coarse, not drop it.
"""


def summarize_routes(rows):
    """Return a count of transactions per handler id."""
    counts = {}
    for row in rows:
        counts[row["handler_id"]] = counts.get(row["handler_id"], 0) + 1
    return counts


if __name__ == "__main__":
    print(summarize_routes([{"handler_id": 1}, {"handler_id": 1}, {"handler_id": 2}]))
