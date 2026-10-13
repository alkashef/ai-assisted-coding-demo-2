"""Calls OpenAI for structured replies and embeddings through the official async SDK.

The only module that calls OpenAI. It does not build prompts (`extraction.py` and
`recommendation.py` do), validate the meaning of a reply (the domain modules do) or retry a
failed call. Implements `StructuredCompleter` and `Embedder` (NFR-001, NFR-002, ERR-001, DEC-003,
DEC-006, DEC-011).
"""

from openai import AsyncOpenAI, OpenAIError
from openai.types.responses import ParsedResponse
from pydantic import BaseModel, ValidationError

from src.config import LlmSettings
from src.ports import LlmError, LlmOutputError


def build_sdk(settings: LlmSettings) -> AsyncOpenAI:
    """Builds the SDK client from the settings.

    The SDK's own retries are off, because a failed call is recorded, not retried (DEC-008).

    Args:
        settings: The API key, base URL and timeout.

    Returns:
        The async SDK client.
    """
    return AsyncOpenAI(
        api_key=settings.api_key,
        base_url=settings.base_url,
        timeout=float(settings.timeout_seconds),
        max_retries=0,
    )


class LlmClient:
    """Sends requests to OpenAI and wraps every failure in `LlmError`.

    Owns the SDK client and the typed settings. It holds no other state.
    """

    def __init__(self, settings: LlmSettings, sdk: AsyncOpenAI) -> None:
        """Creates the client.

        Args:
            settings: The model IDs and the output limit.
            sdk: The SDK client, from `build_sdk` or a fake in tests.
        """
        self._settings = settings
        self._sdk = sdk

    async def complete[T: BaseModel](self, system: str, user: str, schema: type[T]) -> T:
        """Sends one request and returns the validated answer.

        Args:
            system: The system text.
            user: The user text.
            schema: The shape the answer must have.

        Returns:
            An instance of the schema.

        Raises:
            LlmError: The provider call failed. The original error is chained.
            LlmOutputError: The answer is refused, empty or does not fit the schema.
        """
        model = self._settings.model
        try:
            response = await self._sdk.responses.parse(
                model=model,
                instructions=system,
                input=user,
                text_format=schema,
                max_output_tokens=self._settings.max_tokens,
                store=False,
            )
        except ValidationError as err:
            raise LlmOutputError(
                f"completion with model {model} returned an invalid answer", str(err)
            ) from err
        except OpenAIError as err:
            raise _provider_error("completion", model, err) from err
        if response.output_parsed is None:
            raise LlmOutputError(
                f"completion with model {model} returned no answer", _raw_text(response)
            )
        return response.output_parsed

    async def embed(self, text: str) -> list[float]:
        """Embeds one text.

        Args:
            text: The text to embed.

        Returns:
            The embedding vector.

        Raises:
            LlmError: The provider call failed. The original error is chained.
            LlmOutputError: The reply holds no embedding.
        """
        model = self._settings.embedding_model
        try:
            response = await self._sdk.embeddings.create(model=model, input=text)
        except OpenAIError as err:
            raise _provider_error("embedding", model, err) from err
        if not response.data:
            raise LlmOutputError(f"embedding with model {model} returned no vector", "")
        return list(response.data[0].embedding)


def _provider_error(operation: str, model: str, err: OpenAIError) -> LlmError:
    """Builds the error for a failed call. It names the error class, never the SDK message."""
    return LlmError(f"{operation} with model {model} failed: {type(err).__name__}")


def _raw_text[T: BaseModel](response: ParsedResponse[T]) -> str:
    """Joins the text and refusal parts of a reply, for the error that carries it."""
    parts: list[str] = []
    for item in response.output:
        if item.type != "message":
            continue
        for content in item.content:
            parts.append(content.refusal if content.type == "refusal" else content.text)
    return "\n".join(parts)
