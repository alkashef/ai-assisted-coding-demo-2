"""Wraps a document in a fixed tag, so the LLM can tell the data from the instructions.

Pure and synchronous, standard library only. It does not choose what goes in the user text
(`extraction.py` and `recommendation.py` do) or send it (`llm_client.py` does). Implements DEC-016:
the angle bracket of any copy of a known tag inside the data is replaced by `&lt;`, so the data
cannot close its own tag. There is no template substitution.
"""

import re
from enum import StrEnum


class Tag(StrEnum):
    """The tags that mark untrusted data in the user text."""

    CV = "cv"
    JOB_DESCRIPTION = "job_description"
    CANDIDATE_FACTS = "candidate_facts"


def tagged(tag: Tag, text: str) -> str:
    """Wraps a text in a tag, after escaping every copy of a known tag inside it.

    Args:
        tag: The tag that names the kind of data.
        text: The untrusted data.

    Returns:
        The opening tag, the escaped text and the closing tag, one per line.
    """
    return f"<{tag}>\n{_escape_tags(text)}\n</{tag}>"


def _escape_tags(text: str) -> str:
    """Replaces the `<` of every known opening or closing tag, in any case, by `&lt;`."""
    names = "|".join(tag.value for tag in Tag)
    # The lookahead keeps the rest of the tag, so `</cv>` reads `&lt;/cv>` and `<cvs>` is unchanged.
    return re.sub(rf"<(?=\s*/?\s*(?:{names})\b)", "&lt;", text, flags=re.IGNORECASE)
