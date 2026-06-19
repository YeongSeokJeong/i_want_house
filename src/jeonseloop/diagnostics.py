from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from .watchlist import WatchTarget, Watchlist


class LoopDiagnostics:
    def __init__(self, env: Mapping[str, str] | None = None) -> None:
        self._env = env if env is not None else os.environ

    def collector_failure(
        self,
        run_record: dict[str, Any],
        reason: str,
        error: Exception,
        target_complex_ids: tuple[str, ...],
    ) -> dict[str, Any]:
        source_kind = self.listing_source_kind()
        diagnostics: dict[str, Any] = {
            "run_id": run_record["run_id"],
            "generated_at": run_record["finished_at"],
            "run_reason": reason,
            "failure_stage": _failure_stage(reason),
            "source_kind": source_kind,
            "error_type": type(error).__name__,
            "error": str(error),
            "targets": [{"complex_id": complex_id} for complex_id in target_complex_ids],
        }
        if source_kind == "hogangnono" and "JEONSELOOP_HOGANGNONO_APT_HASH_MAP" in str(error):
            missing_targets = self._missing_hogangnono_mapping_targets(target_complex_ids)
            if missing_targets:
                diagnostics["required_env"] = "JEONSELOOP_HOGANGNONO_APT_HASH_MAP"
                diagnostics["missing_mapping_targets"] = missing_targets
        return diagnostics

    def listing_diagnostics(
        self,
        watchlist: Watchlist,
        records_by_complex: dict[str, list[dict[str, Any]]],
        *,
        fixture_path: Path | None,
    ) -> dict[str, Any]:
        source_kind = "fixture" if fixture_path is not None else self.listing_source_kind()
        return {
            "source_kind": source_kind,
            "targets": [
                self._target_listing_diagnostics(source_kind, target, records_by_complex.get(target.complex_id, []))
                for target in watchlist.complexes
            ],
        }

    def listing_source_kind(self) -> str:
        kind = self._env_text("JEONSELOOP_LISTING_SOURCE_KIND")
        if kind:
            return kind
        if self._env_text("JEONSELOOP_LISTING_SOURCE_URL"):
            return "http-json"
        return "unconfigured"

    def _target_listing_diagnostics(
        self,
        source_kind: str,
        target: WatchTarget,
        records: list[dict[str, Any]],
    ) -> dict[str, Any]:
        listing_count = len(records)
        status = "listings_found" if listing_count else "empty_response"
        diagnostic: dict[str, Any] = {
            "complex_id": target.complex_id,
            "source_kind": source_kind,
            "listing_count": listing_count,
            "status": status,
        }

        if source_kind == "hogangnono":
            diagnostic["source_id"] = self._hogangnono_apt_hash_for_diagnostics(target.complex_id)
            diagnostic["trade_types"] = self._env_text("JEONSELOOP_HOGANGNONO_TRADE_TYPES") or "0"
            diagnostic["diagnosis"] = (
                "hogangnono_apt_items_empty" if listing_count == 0 else "hogangnono_apt_items_returned"
            )
        elif listing_count == 0:
            diagnostic["diagnosis"] = f"{source_kind}_returned_no_records"

        return diagnostic

    def _hogangnono_apt_hash_for_diagnostics(self, complex_id: str) -> str | None:
        mapping = self._env_text("JEONSELOOP_HOGANGNONO_APT_HASH_MAP")
        if mapping:
            try:
                parsed = json.loads(mapping)
            except json.JSONDecodeError:
                parsed = {}
            if isinstance(parsed, dict):
                mapped = str(parsed.get(complex_id, "")).strip()
                if mapped:
                    return mapped
        text = str(complex_id).strip()
        if text and text.isalnum() and any(ch.isdigit() for ch in text):
            return text
        return None

    def _missing_hogangnono_mapping_targets(self, target_complex_ids: tuple[str, ...]) -> list[dict[str, str]]:
        missing: list[dict[str, str]] = []
        for complex_id in target_complex_ids:
            if self._hogangnono_apt_hash_for_diagnostics(complex_id):
                continue
            missing.append(
                {
                    "complex_id": complex_id,
                    "example_entry": f'"{complex_id}":"<hogangnono_apt_hash>"',
                }
            )
        return missing

    def _env_text(self, name: str) -> str:
        return self._env.get(name, "").strip()


def _failure_stage(reason: str) -> str:
    if reason in {"listing_source_unconfigured", "collector_failed"}:
        return "listing_collection"
    if reason == "trade_source_failed":
        return "trade_collection"
    return "runtime"
