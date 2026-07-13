"""Filtering services for raw candidate-database records."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import Settings


@dataclass(frozen=True, slots=True)
class QueryFilters:
    name: str | None = None
    tc_min: float | None = None
    tc_max: float | None = None
    pressure_min: float | None = None
    pressure_max: float | None = None
    synthesis_method: str | None = None
    material_class: str | None = None
    feasibility_score_min: float | None = None


def load_database(path: str | Path | None = None) -> list[dict[str, Any]]:
    database_path = Path(path) if path is not None else Settings.from_env().database_path
    with database_path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)
    if not isinstance(records, list):
        raise ValueError(f"Candidate database must contain a JSON list: {database_path}")
    return [record for record in records if isinstance(record, dict)]


def query(
    records: Iterable[Mapping[str, Any]],
    filters: QueryFilters | object,
) -> list[dict[str, Any]]:
    values = _coerce_filters(filters)
    _validate_filters(values)
    return [dict(record) for record in records if _matches(record, values)]


def high_throughput_screening(
    records: Iterable[Mapping[str, Any]],
    *,
    min_tc: float = 100,
    max_tc: float = 500,
    max_pressure: float = 250,
    min_feasibility: float = 0.5,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    if max_results <= 0:
        return []
    selected = query(
        records,
        QueryFilters(
            tc_min=min_tc,
            tc_max=max_tc,
            pressure_max=max_pressure,
            feasibility_score_min=min_feasibility,
        ),
    )
    selected.sort(key=lambda record: _number(record.get("Tc"), float("-inf")), reverse=True)
    return selected[:max_results]


def _coerce_filters(value: QueryFilters | object) -> QueryFilters:
    if isinstance(value, QueryFilters):
        return value
    return QueryFilters(
        name=getattr(value, "name", None),
        tc_min=getattr(value, "tc_min", None),
        tc_max=getattr(value, "tc_max", None),
        pressure_min=getattr(value, "pressure_min", None),
        pressure_max=getattr(value, "pressure_max", None),
        synthesis_method=getattr(value, "synthesis_method", None)
        or getattr(value, "synthesis", None),
        material_class=getattr(value, "material_class", None),
        feasibility_score_min=getattr(value, "feasibility_score_min", None),
    )


def _validate_filters(filters: QueryFilters) -> None:
    numeric = (
        filters.tc_min,
        filters.tc_max,
        filters.pressure_min,
        filters.pressure_max,
        filters.feasibility_score_min,
    )
    if any(value is not None and not isinstance(value, (int, float)) for value in numeric):
        raise TypeError("Numeric query filters must be int or float")
    textual = (filters.name, filters.synthesis_method, filters.material_class)
    if any(value is not None and not isinstance(value, str) for value in textual):
        raise TypeError("Text query filters must be strings")


def _matches(record: Mapping[str, Any], filters: QueryFilters) -> bool:
    name = str(record.get("name") or record.get("formula") or "")
    tc = _number(record.get("Tc", record.get("tc")))
    pressure = _number(record.get("pressure"))
    feasibility = _number(record.get("feasibility_score"))
    synthesis = str(record.get("synthesis_method") or "")
    material_class = str(record.get("material_class") or "")
    return (
        (filters.name is None or name.casefold() == filters.name.casefold())
        and (filters.tc_min is None or (tc is not None and tc >= filters.tc_min))
        and (filters.tc_max is None or (tc is not None and tc <= filters.tc_max))
        and (
            filters.pressure_min is None
            or (pressure is not None and pressure >= filters.pressure_min)
        )
        and (
            filters.pressure_max is None
            or (pressure is not None and pressure <= filters.pressure_max)
        )
        and (
            filters.feasibility_score_min is None
            or (feasibility is not None and feasibility >= filters.feasibility_score_min)
        )
        and (
            filters.synthesis_method is None
            or filters.synthesis_method.casefold() in synthesis.casefold()
        )
        and (
            filters.material_class is None
            or filters.material_class.casefold() == material_class.casefold()
        )
    )


def _number(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
