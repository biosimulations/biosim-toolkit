"""SED-ML adapter steps: the solver-agnostic parts of a SED-ML task.

process-bigraph-lang's `sedml translate` turns each task of a SED-ML file into a composite of a generic time-course
solver (pbsim-common's COPASI or Tellurium step, or any step with the same face) and these steps:

- `DataGenerators`: the solver's `numeric_result` as the SED-ML data generators (linear combinations of result
  columns, time and model constants), the points before the output start dropped;
- `Report`: one CSV per SED-ML report, its header the data sets' labels;
- `Plots`: one Plotly figure (JSON, with data) per SED-ML plot.

They are defined in this module because process-bigraph's discovery registers a class under its defining module:
these are `local:biosim_toolkit.sedml.DataGenerators` and so on, the addresses process-bigraph-lang writes.
`numeric_result` is registered by the runner (pbest registers pbsim-common's standard types).
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any, ClassVar

from process_bigraph import Step

from biosim_toolkit.data import linear_combinations, series_of
from biosim_toolkit.reports import write_csv
from biosim_toolkit.viz import line3d_figure, line_figure, write_figure

#: The data generators' values by id; overwritten whole (bigraph-schema 1.0's map apply keeps only existing keys).
DATA = "overwrite[map[string,list[float]]]"


class DataGenerators(Step):
    """`generators` maps each SED-ML data generator to its terms (`variable`, `coefficient`); a variable is `time`, a
    result column (an SBML id), or a key of `constants` (constant parameters and compartments). `skip` drops that
    many leading points (those before the SED-ML output start)."""

    config_schema: ClassVar[dict[str, str]] = {"generators": "map", "constants": "map[float]", "skip": "integer"}

    def inputs(self) -> dict[str, str]:
        return {"result": "numeric_result"}

    def outputs(self) -> dict[str, str]:
        return {"data": DATA}

    def update(self, state: Mapping[str, Any], interval: Any = None) -> dict[str, Any]:
        return {"data": data_generators(state["result"], self.config["generators"],
                                        self.config.get("constants") or {}, int(self.config.get("skip") or 0))}  # fmt: skip


class Report(Step):
    """`reports` maps each SED-ML report to `file` (relative to `output_dir`), `name` and `data_sets` (`label`,
    `data_generator`); each is written as a CSV whose header is the labels."""

    config_schema: ClassVar[dict[str, str]] = {"output_dir": "string", "reports": "map"}

    def inputs(self) -> dict[str, str]:
        return {"data": DATA}

    def outputs(self) -> dict[str, str]:
        return {}

    def update(self, state: Mapping[str, Any], interval: Any = None) -> dict[str, Any]:
        for report in (self.config.get("reports") or {}).values():
            write_report(state["data"], report, self.config["output_dir"])
        return {}


class Plots(Step):
    """`plots` maps each SED-ML plot to `file` (relative to `output_dir`), `name`, `kind` (`plot2D`, `plot3D`),
    `curves` (`name`, `x`, `y`: data generators), `surfaces` (`name`, `x`, `y`, `z`) and log axes; each is written
    as a Plotly figure with its data."""

    config_schema: ClassVar[dict[str, str]] = {"output_dir": "string", "plots": "map"}

    def inputs(self) -> dict[str, str]:
        return {"data": DATA}

    def outputs(self) -> dict[str, str]:
        return {}

    def update(self, state: Mapping[str, Any], interval: Any = None) -> dict[str, Any]:
        for plot_id, plot in (self.config.get("plots") or {}).items():
            write_figure(
                plot_figure(state["data"], plot, plot_id), os.path.join(self.config["output_dir"], plot["file"])
            )
        return {}


def data_generators(
    result: Mapping[str, Any], generators: Mapping[str, Any], constants: Mapping[str, float], skip: int = 0
) -> dict[str, list[float]]:
    return linear_combinations(series_of(result), generators, constants, skip)


def write_report(data: Mapping[str, list[float]], report: Mapping[str, Any], output_dir: str) -> str:
    columns = [(d["label"], data[d["data_generator"]]) for d in report["data_sets"] if d["data_generator"] in data]
    return write_csv(os.path.join(output_dir, report["file"]), columns)


def plot_figure(data: Mapping[str, list[float]], plot: Mapping[str, Any], plot_id: str = "") -> dict[str, Any]:
    title, meta = plot.get("name") or plot_id, {"sedml_plot": plot_id}
    if plot.get("kind") == "plot3D":
        log = {a: bool(plot.get(f"log_{a}")) for a in ("x", "y", "z")}
        return line3d_figure(data, plot.get("surfaces") or [], title, log=log, meta=meta)
    return line_figure(
        data, plot.get("curves") or [], title, log_x=bool(plot.get("log_x")), log_y=bool(plot.get("log_y")), meta=meta
    )


__all__ = ["DATA", "DataGenerators", "Plots", "Report", "data_generators", "plot_figure", "write_report"]
