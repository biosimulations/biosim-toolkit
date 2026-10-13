"""Tables written for people and other tools: CSV with a header."""

from __future__ import annotations

import csv
import math
import os
from collections.abc import Sequence

Series = list[float]


def write_csv(path: str, columns: Sequence[tuple[str, Series]]) -> str:
    """`columns` (header, values) as a CSV at `path` (its directories made); shorter columns end in empty cells."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    rows = max((len(values) for _, values in columns), default=0)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([header for header, _ in columns])
        for i in range(rows):
            writer.writerow([_cell(values, i) for _, values in columns])
    return path


def read_csv(path: str) -> dict[str, Series]:
    """A CSV written by `write_csv` as columns by header (empty cells dropped)."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    return {h: [float(r[i]) for r in body if i < len(r) and r[i] != ""] for i, h in enumerate(header)}


def _cell(values: Series, i: int) -> str:
    if i >= len(values):
        return ""
    value = values[i]
    return "" if value is None or (isinstance(value, float) and math.isnan(value)) else repr(float(value))


__all__ = ["read_csv", "write_csv"]
