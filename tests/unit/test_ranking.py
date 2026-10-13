"""Tests for `src/ranking.py`."""

from src.ranking import append_unscored


def test_mis_002_item_without_a_score_is_ranked_last() -> None:
    ranked = append_unscored([("b.txt", 0.9), ("a.txt", 0.1)], ["a.txt", "b.txt", "c.txt"])

    assert ranked == [("b.txt", 0.9), ("a.txt", 0.1), ("c.txt", None)]


def test_mis_002_unscored_items_are_ordered_by_id() -> None:
    ranked = append_unscored([("m.txt", 0.5)], ["z.txt", "m.txt", "a.txt", "k.txt"])

    assert [item_id for item_id, _ in ranked] == ["m.txt", "a.txt", "k.txt", "z.txt"]
    assert [score for _, score in ranked[1:]] == [None, None, None]


def test_mis_002_no_item_is_dropped() -> None:
    ranked = append_unscored([], ["b.txt", "a.txt"])

    assert ranked == [("a.txt", None), ("b.txt", None)]
