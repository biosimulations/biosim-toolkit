"""Time courses as named series, and linear combinations of them."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from typing import Any

logger = logging.getLogger(__name__)

#: A time course as the generic solvers return it: the times, the column names, and one row of values per time.
NUMERIC_RESULT = {"time": "list[float]", "columns": "list[string]", "values": "list[list[float]]"}

Series = list[float]


def series_of(result: Mapping[str, Any]) -> dict[str, Series]:
    """A `numeric_result` as series by name: `time` and one per column."""
    series: dict[str, Series] = {"time": [float(t) for t in result["time"]]}
    for i, name in enumerate(result["columns"]):
        series[name] = [float(row[i]) for row in result["values"]]
    return series


def linear_combinations(
    series: Mapping[str, Series],
    combinations: Mapping[str, Sequence[Mapping[str, Any]]],
    constants: Mapping[str, float] | None = None,
    skip: int = 0,
) -> dict[str, Series]:
    """Each combination's terms (`variable`, `coefficient`) summed over `series` and `constants`, with the first `skip`
    points dropped. A combination naming a variable that is in neither is left out, with a warning."""
    constants = constants or {}
    length = len(next(iter(series.values()), []))
    out: dict[str, Series] = {}
    for name, terms in combinations.items():
        total = [0.0] * length
        missing = []
        for term in terms:
            variable, coefficient = term["variable"], float(term.get("coefficient", 1.0))
            if variable in series:
                total = [a + coefficient * b for a, b in zip(total, series[variable], strict=True)]
            elif variable in constants:
                total = [a + coefficient * float(constants[variable]) for a in total]
            else:
                missing.append(variable)
        if missing:
            logger.warning("%s left out: no %s", name, ", ".join(missing))
            continue
        out[name] = total[skip:]
    return out
