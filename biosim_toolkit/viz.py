"""Plotly figures (JSON) from named series."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from typing import Any

Series = list[float]

PLOTLY_MEDIA_TYPE = "application/vnd.plotly.v1+json"


def line_figure(
    series: Mapping[str, Series],
    curves: Sequence[Mapping[str, str]],
    title: str,
    *,
    log_x: bool = False,
    log_y: bool = False,
    meta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Curves (`name`, `x`, `y`: series names) as line traces; a curve naming a missing series is left out."""
    traces = [
        {"type": "scatter", "mode": "lines", "name": c["name"], "x": series[c["x"]], "y": series[c["y"]]}
        for c in curves
        if c["x"] in series and c["y"] in series
    ]
    layout: dict[str, Any] = {"title": {"text": title}}
    if log_x:
        layout["xaxis"] = {"type": "log"}
    if log_y:
        layout["yaxis"] = {"type": "log"}
    return {"data": traces, "layout": layout, "meta": dict(meta or {})}


def line3d_figure(
    series: Mapping[str, Series],
    curves: Sequence[Mapping[str, str]],
    title: str,
    *,
    log: Mapping[str, bool] | None = None,
    meta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Curves in three dimensions (`name`, `x`, `y`, `z`)."""
    traces = [
        {
            "type": "scatter3d",
            "mode": "lines",
            "name": c["name"],
            "x": series[c["x"]],
            "y": series[c["y"]],
            "z": series[c["z"]],
        }
        for c in curves
        if all(c[a] in series for a in ("x", "y", "z"))
    ]
    scene = {f"{a}axis": {"type": "log"} for a, on in (log or {}).items() if on}
    layout: dict[str, Any] = {"title": {"text": title}, **({"scene": scene} if scene else {})}
    return {"data": traces, "layout": layout, "meta": dict(meta or {})}


def write_figure(figure: Mapping[str, Any], path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(figure, f)
    return path
