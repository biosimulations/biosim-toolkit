"""The adapters' work as plain functions: data generators, the report CSV, the Plotly figure."""

import csv
import json
from pathlib import Path

from pbsim_sedml.adapters import data_generators, plotly_figure, write_plot, write_report

RESULT = {"time": [0.0, 1.0, 2.0, 3.0], "columns": ["A", "B"], "values": [[1, 10], [2, 20], [3, 30], [4, 40]]}


def test_data_generators_are_linear_combinations_after_the_output_start() -> None:
    data = data_generators(
        RESULT,
        {
            "t": [{"variable": "time", "coefficient": 1.0}],
            "a": [{"variable": "A", "coefficient": 1.0}],
            "mix": [{"variable": "A", "coefficient": 0.5}, {"variable": "B", "coefficient": -0.25}],
            "k": [{"variable": "k", "coefficient": 2.0}],
            "rate": [{"variable": "R1", "coefficient": 1.0}],  # not in the result: left out
        },
        constants={"k": 3.0},
        skip=1,
    )
    assert data == {"t": [1.0, 2.0, 3.0], "a": [2.0, 3.0, 4.0], "mix": [-4.0, -6.0, -8.0], "k": [6.0, 6.0, 6.0]}


def test_a_report_is_a_csv_of_its_data_sets(tmp_path: Path) -> None:
    data = {"t": [0.0, 1.0], "a": [1.0, 2.0]}
    report = {
        "file": "reports/sim/r1.csv",
        "name": "r1",
        "data_sets": [
            {"label": "Time (min)", "data_generator": "t"},
            {"label": "A", "data_generator": "a"},
            {"label": "missing", "data_generator": "zzz"},
        ],
    }
    path = Path(write_report(data, report, str(tmp_path)))
    assert path == tmp_path / "reports" / "sim" / "r1.csv"
    assert list(csv.reader(path.open())) == [["Time (min)", "A"], ["0.0", "1.0"], ["1.0", "2.0"]]


def test_a_plot_is_a_plotly_figure_with_its_data(tmp_path: Path) -> None:
    data = {"t": [0.0, 1.0], "a": [1.0, 2.0]}
    plot = {
        "file": "plots/sim/p.plotly.json",
        "name": "Figure 1",
        "kind": "plot2D",
        "curves": [{"name": "A", "x": "t", "y": "a"}, {"name": "gone", "x": "t", "y": "zzz"}],
        "surfaces": [],
        "log_x": False,
        "log_y": True,
        "log_z": False,
    }
    figure = plotly_figure(data, plot, "p")
    assert figure["data"] == [{"type": "scatter", "mode": "lines", "name": "A", "x": [0.0, 1.0], "y": [1.0, 2.0]}]
    assert figure["layout"] == {"title": {"text": "Figure 1"}, "yaxis": {"type": "log"}}
    path = Path(write_plot(figure, plot, str(tmp_path)))
    assert json.loads(path.read_text())["meta"] == {"sedml_plot": "p"}
