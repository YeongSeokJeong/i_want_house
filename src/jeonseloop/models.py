from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


class ModelValidationError(ValueError):
    def __init__(self, model_name: str, field_name: str, reason: str) -> None:
        self.model_name = model_name
        self.field_name = field_name
        self.reason = reason
        super().__init__(f"{model_name}.{field_name}: {reason}")


@dataclass(frozen=True)
class NormalizedListing:
    complex_id: str
    price_krw: int
    area_m2: float
    floor: Any
    link: str
    listing_id: str | None = None
    title: str | None = None
    building: str | None = None
    posted_at: str | None = None
    description: str | None = None
    extras: dict[str, Any] = field(default_factory=dict)
    _present_optional_fields: tuple[str, ...] = field(default_factory=tuple, repr=False, compare=False)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> NormalizedListing:
        _require_mapping("NormalizedListing", payload)
        known_fields = {
            "listing_id",
            "complex_id",
            "title",
            "price_krw",
            "area_m2",
            "building",
            "floor",
            "posted_at",
            "description",
            "link",
        }
        present_optional = tuple(field_name for field_name in _LISTING_OPTIONAL_FIELDS if field_name in payload)
        return cls(
            listing_id=_optional_str(payload, "listing_id"),
            complex_id=_required_str(payload, "complex_id", model_name="NormalizedListing"),
            title=_optional_str(payload, "title"),
            price_krw=_required_int(payload, "price_krw", model_name="NormalizedListing"),
            area_m2=_required_float(payload, "area_m2", model_name="NormalizedListing"),
            building=_optional_str(payload, "building"),
            floor=_required_value(payload, "floor", model_name="NormalizedListing"),
            posted_at=_optional_str(payload, "posted_at"),
            description=_optional_str(payload, "description"),
            link=_required_str(payload, "link", model_name="NormalizedListing"),
            extras={str(key): value for key, value in payload.items() if str(key) not in known_fields},
            _present_optional_fields=present_optional,
        )

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.extras)
        for field_name in _LISTING_OPTIONAL_FIELDS:
            value = getattr(self, field_name)
            if value is not None or field_name in self._present_optional_fields:
                payload[field_name] = value
        payload.update(
            {
                "complex_id": self.complex_id,
                "price_krw": self.price_krw,
                "area_m2": self.area_m2,
                "floor": self.floor,
                "link": self.link,
            }
        )
        return payload


@dataclass(frozen=True)
class CandidateRecord:
    complex_id: str
    listing_key: str
    price_krw: int
    decision: str
    reason: str
    listing: NormalizedListing
    extras: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> CandidateRecord:
        _require_mapping("CandidateRecord", payload)
        known_fields = {"complex_id", "listing_key", "price_krw", "decision", "reason", "listing"}
        listing_payload = _required_mapping(payload, "listing", model_name="CandidateRecord")
        return cls(
            complex_id=_required_str(payload, "complex_id", model_name="CandidateRecord"),
            listing_key=_required_str(payload, "listing_key", model_name="CandidateRecord"),
            price_krw=_required_int(payload, "price_krw", model_name="CandidateRecord"),
            decision=_required_str(payload, "decision", model_name="CandidateRecord"),
            reason=_required_str(payload, "reason", model_name="CandidateRecord"),
            listing=NormalizedListing.from_dict(listing_payload),
            extras={str(key): value for key, value in payload.items() if str(key) not in known_fields},
        )

    @classmethod
    def from_candidate(cls, candidate: Any) -> CandidateRecord:
        return cls(
            complex_id=_required_attr(candidate, "complex_id", model_name="CandidateRecord"),
            listing_key=_required_attr(candidate, "listing_key", model_name="CandidateRecord"),
            price_krw=_required_int_attr(candidate, "price_krw", model_name="CandidateRecord"),
            decision=_required_attr(candidate, "decision", model_name="CandidateRecord"),
            reason=_required_attr(candidate, "reason", model_name="CandidateRecord"),
            listing=NormalizedListing.from_dict(
                _required_mapping({"listing": getattr(candidate, "listing", None)}, "listing", model_name="CandidateRecord")
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.extras)
        payload.update(
            {
                "complex_id": self.complex_id,
                "listing_key": self.listing_key,
                "price_krw": self.price_krw,
                "decision": self.decision,
                "reason": self.reason,
                "listing": self.listing.to_dict(),
            }
        )
        return payload


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    started_at: str
    finished_at: str
    status: str
    reason: str
    counts: dict[str, int]
    extras: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> RunRecord:
        _require_mapping("RunRecord", payload)
        known_fields = {"run_id", "started_at", "finished_at", "status", "reason", "counts"}
        counts = _required_mapping(payload, "counts", model_name="RunRecord")
        return cls(
            run_id=_required_str(payload, "run_id", model_name="RunRecord"),
            started_at=_required_str(payload, "started_at", model_name="RunRecord"),
            finished_at=_required_str(payload, "finished_at", model_name="RunRecord"),
            status=_required_str(payload, "status", model_name="RunRecord"),
            reason=_required_str(payload, "reason", model_name="RunRecord"),
            counts={str(key): _coerce_int(value, "RunRecord", f"counts.{key}") for key, value in counts.items()},
            extras={str(key): value for key, value in payload.items() if str(key) not in known_fields},
        )

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.extras)
        payload.update(
            {
                "run_id": self.run_id,
                "started_at": self.started_at,
                "finished_at": self.finished_at,
                "status": self.status,
                "reason": self.reason,
                "counts": dict(self.counts),
            }
        )
        return payload


@dataclass(frozen=True)
class FeedItem:
    complex_id: str
    listing_key: str
    decision: str
    reason: str
    price_krw: int
    alert_planned: bool
    title: str | None = None
    description: str | None = None
    building: str | None = None
    floor: Any = None
    area_m2: float | None = None
    link: str | None = None
    extras: dict[str, Any] = field(default_factory=dict)
    _present_optional_fields: tuple[str, ...] = field(default_factory=tuple, repr=False, compare=False)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> FeedItem:
        _require_mapping("FeedItem", payload)
        known_fields = {
            "complex_id",
            "listing_key",
            "decision",
            "reason",
            "price_krw",
            "alert_planned",
            "title",
            "description",
            "building",
            "floor",
            "area_m2",
            "link",
        }
        present_optional = tuple(field_name for field_name in _FEED_OPTIONAL_FIELDS if field_name in payload)
        return cls(
            complex_id=_required_str(payload, "complex_id", model_name="FeedItem"),
            listing_key=_required_str(payload, "listing_key", model_name="FeedItem"),
            decision=_required_str(payload, "decision", model_name="FeedItem"),
            reason=_required_str(payload, "reason", model_name="FeedItem"),
            price_krw=_required_int(payload, "price_krw", model_name="FeedItem"),
            alert_planned=_required_bool(payload, "alert_planned", model_name="FeedItem"),
            title=_optional_str(payload, "title"),
            description=_optional_str(payload, "description"),
            building=_optional_str(payload, "building"),
            floor=payload.get("floor"),
            area_m2=_optional_float(payload, "area_m2", model_name="FeedItem"),
            link=_optional_str(payload, "link"),
            extras={str(key): value for key, value in payload.items() if str(key) not in known_fields},
            _present_optional_fields=present_optional,
        )

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.extras)
        payload.update(
            {
                "complex_id": self.complex_id,
                "listing_key": self.listing_key,
                "decision": self.decision,
                "reason": self.reason,
                "price_krw": self.price_krw,
                "alert_planned": self.alert_planned,
            }
        )
        for field_name in _FEED_OPTIONAL_FIELDS:
            value = getattr(self, field_name)
            if value is not None or field_name in self._present_optional_fields:
                payload[field_name] = value
        return payload


_LISTING_OPTIONAL_FIELDS = ("listing_id", "title", "building", "posted_at", "description")
_FEED_OPTIONAL_FIELDS = ("title", "description", "building", "floor", "area_m2", "link")


def _require_mapping(model_name: str, payload: Mapping[str, Any]) -> None:
    if not isinstance(payload, Mapping):
        raise ModelValidationError(model_name, "<payload>", "must be a mapping")


def _required_mapping(payload: Mapping[str, Any], field_name: str, *, model_name: str) -> Mapping[str, Any]:
    value = _required_value(payload, field_name, model_name=model_name)
    if not isinstance(value, Mapping):
        raise ModelValidationError(model_name, field_name, "must be a mapping")
    return value


def _required_value(payload: Mapping[str, Any], field_name: str, *, model_name: str) -> Any:
    if field_name not in payload:
        raise ModelValidationError(model_name, field_name, "is required")
    return payload[field_name]


def _required_str(payload: Mapping[str, Any], field_name: str, *, model_name: str) -> str:
    value = _required_value(payload, field_name, model_name=model_name)
    if value is None:
        raise ModelValidationError(model_name, field_name, "is required")
    text = str(value).strip()
    if not text:
        raise ModelValidationError(model_name, field_name, "must not be blank")
    return text


def _optional_str(payload: Mapping[str, Any], field_name: str) -> str | None:
    if field_name not in payload or payload[field_name] is None:
        return None
    return str(payload[field_name])


def _required_int(payload: Mapping[str, Any], field_name: str, *, model_name: str) -> int:
    return _coerce_int(_required_value(payload, field_name, model_name=model_name), model_name, field_name)


def _required_int_attr(candidate: Any, field_name: str, *, model_name: str) -> int:
    if not hasattr(candidate, field_name):
        raise ModelValidationError(model_name, field_name, "is required")
    return _coerce_int(getattr(candidate, field_name), model_name, field_name)


def _coerce_int(value: Any, model_name: str, field_name: str) -> int:
    if isinstance(value, bool):
        raise ModelValidationError(model_name, field_name, "must be an integer")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ModelValidationError(model_name, field_name, "must be an integer") from exc


def _required_float(payload: Mapping[str, Any], field_name: str, *, model_name: str) -> float:
    value = _required_value(payload, field_name, model_name=model_name)
    return _coerce_float(value, model_name, field_name)


def _optional_float(payload: Mapping[str, Any], field_name: str, *, model_name: str) -> float | None:
    if field_name not in payload or payload[field_name] is None:
        return None
    return _coerce_float(payload[field_name], model_name, field_name)


def _coerce_float(value: Any, model_name: str, field_name: str) -> float:
    if isinstance(value, bool):
        raise ModelValidationError(model_name, field_name, "must be a number")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ModelValidationError(model_name, field_name, "must be a number") from exc


def _required_bool(payload: Mapping[str, Any], field_name: str, *, model_name: str) -> bool:
    value = _required_value(payload, field_name, model_name=model_name)
    if not isinstance(value, bool):
        raise ModelValidationError(model_name, field_name, "must be a boolean")
    return value


def _required_attr(candidate: Any, field_name: str, *, model_name: str) -> str:
    if not hasattr(candidate, field_name):
        raise ModelValidationError(model_name, field_name, "is required")
    value = getattr(candidate, field_name)
    if value is None:
        raise ModelValidationError(model_name, field_name, "is required")
    text = str(value).strip()
    if not text:
        raise ModelValidationError(model_name, field_name, "must not be blank")
    return text
