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
    model: str = "gpt-4.1"
    endpoint: str = "https://api.openai.com/v1/responses"

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "LlmReviewConfig":
        values = env if env is not None else os.environ
        requested = values.get("JEONSELOOP_LLM_REVIEW", "").strip().lower() in {"1", "true", "yes", "on"}
        api_key = values.get("OPENAI_API_KEY", "").strip()
        return cls(
            enabled=requested and bool(api_key),
            api_key=api_key,
            model=values.get("JEONSELOOP_LLM_MODEL", "gpt-4.1").strip() or "gpt-4.1",
        )


CandidateReviewer = Callable[[Candidate], str]


class CandidateReviewService:
    def __init__(
        self,
        *,
        config: LlmReviewConfig | None = None,
        reviewer: CandidateReviewer | None = None,
    ) -> None:
        self._config = config if config is not None else LlmReviewConfig.from_env()
        self._reviewer = reviewer

    def apply(self, candidates: Iterable[Candidate]) -> list[Candidate]:
        candidate_list = list(candidates)
        if not self._config.enabled:
            return candidate_list

        review = self._reviewer if self._reviewer is not None else OpenAiCandidateReviewer(self._config).review
        reviewed: list[Candidate] = []
        for candidate in candidate_list:
            if candidate.decision != "approve":
                reviewed.append(candidate)
                continue
            try:
                result = self.parse_response(review(candidate))
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

    @staticmethod
    def parse_response(text: str) -> dict[str, str]:
        return parse_review_response(text)


def apply_llm_review(
    candidates: Iterable[Candidate],
    *,
    config: LlmReviewConfig | None = None,
    reviewer: CandidateReviewer | None = None,
) -> list[Candidate]:
    return CandidateReviewService(config=config, reviewer=reviewer).apply(candidates)


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


class OpenAiCandidateReviewer:
    def __init__(self, config: LlmReviewConfig, opener: Callable[..., object] = request.urlopen) -> None:
        self._config = config
        self._opener = opener

    def review(self, candidate: Candidate) -> str:  # pragma: no cover - live network path
        body = json.dumps(self._build_payload(candidate), ensure_ascii=False).encode("utf-8")
        req = request.Request(
            self._config.endpoint,
            data=body,
            method="POST",
            headers={
                "content-type": "application/json",
                "authorization": f"Bearer {self._config.api_key}",
            },
        )
        with self._opener(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return _extract_response_text(payload)

    def _build_payload(self, candidate: Candidate) -> dict:
        candidate_payload = {
            "complex_id": candidate.complex_id,
            "listing_key": candidate.listing_key,
            "price_krw": candidate.price_krw,
            "reason": candidate.reason,
            "listing": candidate.listing,
        }
        return {
            "model": self._config.model,
            "instructions": (
                "Review this JeonseLoop rental candidate before Telegram notification. "
                "Approve only when the candidate is plausibly actionable. "
                "Return JSON that matches the requested schema."
            ),
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": json.dumps(candidate_payload, ensure_ascii=False, sort_keys=True),
                        }
                    ],
                }
            ],
            "max_output_tokens": 256,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "jeonseloop_candidate_review",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "decision": {"type": "string", "enum": ["approve", "hold", "reject"]},
                            "reason": {"type": "string"},
                        },
                        "required": ["decision", "reason"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                }
            },
        }


def _extract_response_text(payload: dict) -> str:
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    output = payload.get("output", [])
    if not isinstance(output, list):
        raise ReviewError("missing review output")
    for item in output:
        if not isinstance(item, dict):
            continue
        content = item.get("content", [])
        if not isinstance(content, list):
            continue
        for part in content:
            if isinstance(part, dict) and isinstance(part.get("text"), str) and part["text"].strip():
                return part["text"]
    raise ReviewError("missing review output text")


def _replace_decision(candidate: Candidate, decision: str, reason: str) -> Candidate:
    return Candidate(
        candidate.complex_id,
        candidate.listing_key,
        candidate.price_krw,
        decision,
        reason,
        candidate.listing,
    )
