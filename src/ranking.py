"""Completes a ranked list with the items that have no score.

Holds pure list logic only. It does not compute similarity (`vector_store.py` does) or
decide which items exist (the pipeline does). Implements MIS-002 and RNK-002: an item without a
vector stays in the ranking, last, and nothing else changes the order.
"""

from collections.abc import Iterable


def append_unscored(
    scored: list[tuple[str, float]], all_ids: Iterable[str]
) -> list[tuple[str, float | None]]:
    """Appends every item that has no score after the scored items, ordered by ID.

    Args:
        scored: (item ID, score) pairs, already ordered best first.
        all_ids: The ID of every item that must appear in the ranking.

    Returns:
        The scored pairs in their given order, then (item ID, `None`) for each
        remaining ID in ascending order.
    """
    scored_ids = {item_id for item_id, _ in scored}
    missing = sorted(set(all_ids) - scored_ids)
    return [*scored, *((item_id, None) for item_id in missing)]
