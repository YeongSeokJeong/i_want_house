from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Callable, Iterable
from urllib import request

from .analyzer import Candidate


class ReviewError(ValueError):
    """Raised when an LLM review response cannot be safely used."""


@dataclass(frozen=True)
class LlmReviewConfig:
    enabled: bool = False
    api_key: str = ""
    model: str = "claude-3-5-haiku-latest"
    endpoint: str = "https://api.anthropic.com/v1/messages"

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "LlmReviewConfig":
        values = env if env is not None else os.environ
        requested = values.get("JEONSELOOP_LLM_REVIEW", "").strip().lower() in {"1", "true", "yes", "on"}
        api_key = values.get("ANTHROPIC_API_KEY", "").strip()
        return cls(
            enabled=requested and bool(api_key),
            api_key=api_key,
            model=values.get("JEONSELOOP_LLM_MODEL", "claude-3-5-haiku-latest").strip()
            or "claude-3-5-haiku-latest",
        )


CandidateReviewer = Callable[[Candidate], str]


def apply_llm_review(
    candidates: Iterable[Candidate],
    *,
    config: LlmReviewConfig | None = None,
    reviewer: CandidateReviewer | None = None,
) -> list[Candidate]:
    review_config = config if config is not None else LlmReviewConfig.from_env()
    candidate_list = list(candidates)
    if not review_config.enabled:
        return candidate_list

    review = reviewer if reviewer is not None else AnthropicCandidateReviewer(review_config).review
    reviewed: list[Candidate] = []
    for candidate in candidate_list:
        if candidate.decision != "approve":
            reviewed.append(candidate)
            continue
        try:
            result = parse_review_response(review(candidate))
        except ReviewError:
            reviewed.append(_replace_decision(candidate, "hold", "llm_invalid_response"))
            continue
        except Exception as exc:  # pragma: no cover - live network path
            reviewed.append(_replace_decision(candidate, "hold", f"llm_review_error:{type(exc).__name__}"))
            continue

        if result["decision"] == "approve":
            reviewed.append(candidate)
        else:
            reviewed.append(_replace_decision(candidate, result["decision"], f"llm_{result['reason']}"))
    return reviewed


def parse_review_response(text: str) -> dict[str, str]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ReviewError("review response must be a JSON object") from exc
    if not isinstance(payload, dict):
        raise ReviewError("review response must be a JSON object")

    decision = str(payload.get("decision", "")).strip().lower()
    if decision not in {"approve", "hold", "reject"}:
        raise ReviewError("review decision must be approve, hold, or reject")

    reason = str(payload.get("reason", "")).strip()
    if not reason:
        raise ReviewError("review reason is required")
    return {"decision": decision, "reason": reason}


class AnthropicCandidateReviewer:
    def __init__(self, config: LlmReviewConfig) -> None:
        self._config = config

    def review(self, candidate: Candidate) -> str:  # pragma: no cover - live network path
        body = json.dumps(
            {
                "model": self._config.model,
                "max_tokens": 256,
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "Review this JeonseLoop candidate. Respond only as JSON with "
                            'decision "approve", "hold", or "reject" and a short reason.\n'
                            + json.dumps(
                                {
                                    "complex_id": candidate.complex_id,
                                    "price_krw": candidate.price_krw,
                                    "reason": candidate.reason,
                                    "listing": candidate.listing,
                                },
                                ensure_ascii=False,
                                sort_keys=True,
                            )
                        ),
                    }
                ],
            },
            ensure_ascii=False,
        ).encode("utf-8")
        req = request.Request(
            self._config.endpoint,
            data=body,
            method="POST",
            headers={
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
                "x-api-key": self._config.api_key,
            },
        )
        with request.urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        content = payload.get("content", [])
        if not content or not isinstance(content[0], dict):
            raise ReviewError("missing review content")
        return str(content[0].get("text", ""))


def _replace_decision(candidate: Candidate, decision: str, reason: str) -> Candidate:
    return Candidate(
        candidate.complex_id,
        candidate.listing_key,
        candidate.price_krw,
        decision,
        reason,
        candidate.listing,
    )
