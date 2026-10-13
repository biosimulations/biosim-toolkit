"""SED-ML adapter steps for process-bigraph.

A SED-ML task translated by process-bigraph-lang (`sedml translate`) is a composite of a generic time-course solver
and three steps from this package:

- `DataGenerators`: the solver's `numeric_result` (time, columns, values) as the SED-ML data generators, each a linear
  combination of result columns, the time and model constants, with the points before the output start dropped;
- `Report`: one CSV per SED-ML report, its columns the data sets' labels;
- `Plots`: one Plotly figure (JSON) per SED-ML plot, with the data.

They are solver-agnostic: any step returning a `numeric_result` feeds them.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from process_bigraph import Step

from pbsim_sedml.adapters import NUMERIC_RESULT, data_generators, plotly_figure, write_plot, write_report

__all__ = ["NUMERIC_RESULT", "DataGenerators", "Plots", "Report"]

# The steps are defined here, not in a submodule: process-bigraph's discovery registers a class under its defining
# module, so these are local:pbsim_sedml.DataGenerators and so on, the addresses process-bigraph-lang writes.
# `numeric_result` is registered by the runner (pbest registers pbsim-common's standard types); registering it here
# as well would collide with that.


class DataGenerators(Step):
    """`generators` maps each SED-ML data generator to its terms (`variable`, `coefficient`); a variable is `time`, a
    result column (an SBML id), or a key of `constants` (constant parameters and compartments). `skip` drops that
    many leading points (those before the SED-ML output start). A generator whose variable is missing from the
    result is left out, with a warning."""

    config_schema: ClassVar[dict[str, str]] = {"generators": "map", "constants": "map[float]", "skip": "integer"}

    def inputs(self) -> dict[str, str]:
        return {"result": "numeric_result"}

    def outputs(self) -> dict[str, str]:
        return {"data": "overwrite[map[string,list[float]]]"}

    def update(self, state: Mapping[str, Any], interval: Any = None) -> dict[str, Any]:
        return {"data": data_generators(state["result"], self.config["generators"], self.config.get("constants") or {},
                                        int(self.config.get("skip") or 0))}  # fmt: skip


class Report(Step):
    """`reports` maps each SED-ML report to `file` (relative to `output_dir`), `name` and `data_sets` (`label`,
    `data_generator`); each is written as a CSV whose header is the labels."""

    config_schema: ClassVar[dict[str, str]] = {"output_dir": "string", "reports": "map"}

    def inputs(self) -> dict[str, str]:
        return {"data": "overwrite[map[string,list[float]]]"}

    def outputs(self) -> dict[str, str]:
        return {}

    def update(self, state: Mapping[str, Any], interval: Any = None) -> dict[str, Any]:
        for report in (self.config.get("reports") or {}).values():
            write_report(state["data"], report, self.config["output_dir"])
        return {}


class Plots(Step):
    """`plots` maps each SED-ML plot to `file` (relative to `output_dir`), `name`, `kind`, `curves` (`name`, `x`, `y`:
    data generators), `surfaces` and log axes; each is written as a Plotly figure with its data."""

    config_schema: ClassVar[dict[str, str]] = {"output_dir": "string", "plots": "map"}

    def inputs(self) -> dict[str, str]:
        return {"data": "overwrite[map[string,list[float]]]"}

    def outputs(self) -> dict[str, str]:
        return {}

    def update(self, state: Mapping[str, Any], interval: Any = None) -> dict[str, Any]:
        for plot_id, plot in (self.config.get("plots") or {}).items():
            write_plot(plotly_figure(state["data"], plot, plot_id), plot, self.config["output_dir"])
        return {}
