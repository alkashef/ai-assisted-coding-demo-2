"""Tests for `src/llm_client.py`. No test uses the network: the SDK is a fake."""

from types import SimpleNamespace
from typing import cast

import pytest
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel

from src.config import LlmSettings
from src.llm_client import LlmClient, build_sdk
from src.ports import LlmError, LlmOutputError

_KEY = "sk-test-secret-123"


class _Reply(BaseModel):
    answer: str


def _settings() -> LlmSettings:
    return LlmSettings(
        api_key=_KEY,
        base_url="https://example.test/v1",
        model="chat-model-a",
        max_tokens=100,
        embedding_model="embed-model-a",
        timeout_seconds=30,
        max_concurrency=2,
    )


class _FakeResponses:
    def __init__(self, result: object = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.calls: list[dict[str, object]] = []

    async def parse(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.result


class _FakeEmbeddings:
    def __init__(self, result: object = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.calls: list[dict[str, object]] = []

    async def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.result


def _client(
    responses: _FakeResponses | None = None, embeddings: _FakeEmbeddings | None = None
) -> LlmClient:
    fake = SimpleNamespace(
        responses=responses or _FakeResponses(), embeddings=embeddings or _FakeEmbeddings()
    )
    return LlmClient(_settings(), cast("AsyncOpenAI", fake))


def _parsed(parsed: _Reply | None, refusal: str | None = None) -> SimpleNamespace:
    if refusal is not None:
        content = SimpleNamespace(type="refusal", refusal=refusal)
    else:
        content = SimpleNamespace(type="output_text", text="raw text", parsed=parsed)
    message = SimpleNamespace(type="message", content=[content])
    return SimpleNamespace(output=[message], output_parsed=parsed)


def _auth_error() -> OpenAIError:
    return OpenAIError(f"Incorrect API key provided: {_KEY}")


def test_nfr_001_client_is_built_with_the_configured_base_url() -> None:
    sdk = build_sdk(_settings())

    assert str(sdk.base_url).rstrip("/") == "https://example.test/v1"
    assert sdk.api_key == _KEY
    assert sdk.max_retries == 0


async def test_nfr_001_completion_sends_only_the_given_system_and_user_text() -> None:
    responses = _FakeResponses(_parsed(_Reply(answer="ok")))

    await _client(responses=responses).complete("system text", "user text", _Reply)

    assert responses.calls == [
        {
            "model": "chat-model-a",
            "instructions": "system text",
            "input": "user text",
            "text_format": _Reply,
            "max_output_tokens": 100,
            "store": False,
        }
    ]


async def test_err_001_provider_error_becomes_llm_error_naming_the_operation_and_model() -> None:
    error = _auth_error()
    client = _client(responses=_FakeResponses(error=error))

    with pytest.raises(LlmError) as raised:
        await client.complete("s", "u", _Reply)

    assert "completion" in str(raised.value)
    assert "chat-model-a" in str(raised.value)
    assert raised.value.__cause__ is error


async def test_err_001_embedding_provider_error_names_the_operation_and_model() -> None:
    client = _client(embeddings=_FakeEmbeddings(error=_auth_error()))

    with pytest.raises(LlmError) as raised:
        await client.embed("text")

    assert "embedding" in str(raised.value)
    assert "embed-model-a" in str(raised.value)


async def test_err_001_refusal_raises_llm_output_error_with_the_raw_output() -> None:
    client = _client(responses=_FakeResponses(_parsed(None, refusal="I cannot help")))

    with pytest.raises(LlmOutputError) as raised:
        await client.complete("s", "u", _Reply)

    assert raised.value.raw_output == "I cannot help"


async def test_err_001_invalid_json_raises_llm_output_error_with_the_raw_output() -> None:
    try:
        _Reply.model_validate_json('{"wrong": 1}')
    except ValueError as err:
        invalid = err
    client = _client(responses=_FakeResponses(error=invalid))

    with pytest.raises(LlmOutputError) as raised:
        await client.complete("s", "u", _Reply)

    assert "wrong" in raised.value.raw_output


async def test_err_001_reply_without_parsed_content_raises_llm_output_error() -> None:
    client = _client(responses=_FakeResponses(_parsed(None)))

    with pytest.raises(LlmOutputError) as raised:
        await client.complete("s", "u", _Reply)

    assert raised.value.raw_output == "raw text"


async def test_err_001_embedding_reply_without_data_raises_llm_output_error() -> None:
    client = _client(embeddings=_FakeEmbeddings(SimpleNamespace(data=[])))

    with pytest.raises(LlmOutputError):
        await client.embed("text")


async def test_nfr_002_llm_error_message_excludes_the_api_key() -> None:
    client = _client(responses=_FakeResponses(error=_auth_error()))

    with pytest.raises(LlmError) as raised:
        await client.complete("s", "u", _Reply)

    assert _KEY not in str(raised.value)


async def test_dec_003_complete_returns_an_instance_of_the_schema() -> None:
    client = _client(responses=_FakeResponses(_parsed(_Reply(answer="ok"))))

    result = await client.complete("s", "u", _Reply)

    assert result == _Reply(answer="ok")


async def test_dec_003_embed_returns_the_vector_for_the_text() -> None:
    embeddings = _FakeEmbeddings(SimpleNamespace(data=[SimpleNamespace(embedding=[0.5, -1.0])]))

    vector = await _client(embeddings=embeddings).embed("some text")

    assert vector == [0.5, -1.0]
    assert embeddings.calls == [{"model": "embed-model-a", "input": "some text"}]
