"""What the adapter steps do, as plain functions (tested without a composite)."""

from __future__ import annotations

import csv
import json
import logging
import math
import os
from collections.abc import Mapping, Sequence
from typing import Any

logger = logging.getLogger(__name__)

#: A time course as the generic solvers return it: the times, the column names, and one row of values per time.
NUMERIC_RESULT = {"time": "list[float]", "columns": "list[string]", "values": "list[list[float]]"}

Series = list[float]


def data_generators(
    result: Mapping[str, Any],
    generators: Mapping[str, Sequence[Mapping[str, Any]]],
    constants: Mapping[str, float],
    skip: int = 0,
) -> dict[str, Series]:
    time = [float(t) for t in result["time"]]
    columns = list(result["columns"])
    values = result["values"]
    series: dict[str, Series] = {"time": time}
    for i, name in enumerate(columns):
        series[name] = [float(row[i]) for row in values]
    out: dict[str, Series] = {}
    for gen_id, terms in generators.items():
        total = [0.0] * len(time)
        missing = []
        for term in terms:
            variable, coefficient = term["variable"], float(term.get("coefficient", 1.0))
            if variable in series:
                column = series[variable]
                total = [a + coefficient * b for a, b in zip(total, column, strict=True)]
            elif variable in constants:
                total = [a + coefficient * float(constants[variable]) for a in total]
            else:
                missing.append(variable)
        if missing:
            logger.warning("data generator %s left out: the result has no %s", gen_id, ", ".join(missing))
            continue
        out[gen_id] = total[skip:]
    return out


def write_report(data: Mapping[str, Series], report: Mapping[str, Any], output_dir: str) -> str:
    sets = [d for d in report["data_sets"] if d["data_generator"] in data]
    path = os.path.join(output_dir, report["file"])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows = max((len(data[d["data_generator"]]) for d in sets), default=0)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([d["label"] for d in sets])
        for i in range(rows):
            writer.writerow([_cell(data[d["data_generator"]], i) for d in sets])
    return path


def plotly_figure(data: Mapping[str, Series], plot: Mapping[str, Any], plot_id: str = "") -> dict[str, Any]:
    traces: list[dict[str, Any]] = []
    for curve in plot.get("curves") or []:
        if curve["x"] in data and curve["y"] in data:
            traces.append({"type": "scatter", "mode": "lines", "name": curve["name"],
                           "x": data[curve["x"]], "y": data[curve["y"]]})  # fmt: skip
    for surface in plot.get("surfaces") or []:
        if all(surface[a] in data for a in ("x", "y", "z")):
            traces.append({"type": "scatter3d", "mode": "lines", "name": surface["name"],
                           "x": data[surface["x"]], "y": data[surface["y"]], "z": data[surface["z"]]})  # fmt: skip
    layout: dict[str, Any] = {"title": {"text": plot.get("name") or plot_id}}
    for axis in ("x", "y", "z"):
        if plot.get(f"log_{axis}"):
            layout.setdefault("scene" if plot.get("kind") == "plot3D" else f"{axis}axis", {})
            target = (
                layout["scene"].setdefault(f"{axis}axis", {}) if plot.get("kind") == "plot3D" else layout[f"{axis}axis"]
            )
            target["type"] = "log"
    return {"data": traces, "layout": layout, "meta": {"sedml_plot": plot_id}}


def write_plot(figure: Mapping[str, Any], plot: Mapping[str, Any], output_dir: str) -> str:
    path = os.path.join(output_dir, plot["file"])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(figure, f)
    return path


def _cell(column: Series, i: int) -> str:
    if i >= len(column):
        return ""
    value = column[i]
    return "" if value is None or (isinstance(value, float) and math.isnan(value)) else repr(float(value))
