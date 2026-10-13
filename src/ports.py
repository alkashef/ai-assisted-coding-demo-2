"""The contracts between the application and the outside systems, and the errors they raise.

Holds protocols and error types only. It does not call OpenAI (`llm_client.py` does) or Chroma
(`vector_store.py` does). Implements the ports in design section 4 (ERR-001, DEC-003, DEC-004).
"""

from typing import Protocol

from pydantic import BaseModel


class LlmError(Exception):
    """An LLM call failed. The message names the operation and the model, never a secret."""


class LlmOutputError(LlmError):
    """The LLM answered, but the answer is refused, malformed or invalid.

    Attributes:
        raw_output: What the model returned, for the failure list and the log.
    """

    def __init__(self, message: str, raw_output: str) -> None:
        """Creates the error.

        Args:
            message: What was wrong with the answer.
            raw_output: What the model returned.
        """
        super().__init__(message)
        self.raw_output = raw_output


class StructuredCompleter(Protocol):
    """Asks an LLM for an answer in the shape of a schema."""

    async def complete[T: BaseModel](self, system: str, user: str, schema: type[T]) -> T:
        """Sends one request and returns the validated answer.

        Args:
            system: The system text.
            user: The user text.
            schema: The shape the answer must have.

        Returns:
            An instance of the schema.

        Raises:
            LlmError: The provider call failed.
            LlmOutputError: The answer is refused or does not fit the schema.
        """
        ...


class Embedder(Protocol):
    """Turns a text into a vector."""

    async def embed(self, text: str) -> list[float]:
        """Embeds one text.

        Args:
            text: The text to embed.

        Returns:
            The embedding vector.

        Raises:
            LlmError: The provider call failed.
        """
        ...


class VectorIndex(Protocol):
    """Stores vectors by ID and finds the nearest ones."""

    def add(self, item_id: str, vector: list[float]) -> None:
        """Stores one vector.

        Args:
            item_id: The ID of the item, such as a file name.
            vector: The embedding vector.
        """
        ...

    def nearest(self, vector: list[float]) -> list[tuple[str, float]]:
        """Finds every stored item, nearest first.

        Args:
            vector: The query vector.

        Returns:
            One (item ID, cosine similarity) pair per stored item, best first.
        """
        ...
