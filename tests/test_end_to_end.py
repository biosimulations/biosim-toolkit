"""Instance archives made by process-bigraph-lang's `sedml translate` (tests/fixtures/<model>.<solver>.omex), run the
way compose-api's runner (pbest 0.6.3) runs an archive: extracted, member names in the document made absolute, a core
with pbsim-common's standard types, `Composite(core=core, config=document)`, `run(...)`. The generic COPASI and
Tellurium steps solve; this package's steps write the reports and plots. The fixtures' output directory is the
placeholder `OUTPUT_DIR`."""

import csv
import json
import os
import zipfile
from pathlib import Path

import pytest
from pbsim_common import standard_types
from process_bigraph import Composite, allocate_core

FIXTURES = Path(__file__).parent / "fixtures"


def run_archive(archive: Path, work: Path) -> Path:
    extracted, output = work / "input", work / "output"
    extracted.mkdir(parents=True)
    output.mkdir()
    with zipfile.ZipFile(archive) as z:
        z.extractall(extracted)
    (pbg,) = [p for p in extracted.iterdir() if p.suffix == ".pbg"]
    text = pbg.read_text()
    for other in os.listdir(extracted):  # as pbest does
        if not other.endswith(".pbg"):
            text = text.replace(other, str(extracted / other))
    text = text.replace("OUTPUT_DIR", str(output))
    core = allocate_core()
    for name, schema in standard_types.items():
        core.register_type(name, schema)
    composite = Composite(core=core, config=json.loads(text))
    composite.run(1.0)
    return output


def read_report(path: Path) -> dict[str, list[float]]:
    rows = list(csv.reader(path.open()))
    header, body = rows[0], rows[1:]
    return {label: [float(r[i]) for r in body] for i, label in enumerate(header)}


@pytest.mark.parametrize("solver", ["copasi", "tellurium"])
def test_ciliberto_writes_its_report_and_plots(solver: str, tmp_path: Path) -> None:
    output = run_archive(FIXTURES / f"Ciliberto2003.{solver}.omex", tmp_path)
    report = read_report(output / "reports" / "simulation_1" / "report.csv")
    assert len(report) == 21 and "Total Swe1" in report
    assert len(report["Time (min)"]) == 201 and report["Time (min)"][-1] == pytest.approx(140.0)
    swe1t = report["Total Swe1"]
    parts = ["Swe1", "Modified Swe1", "Phosphorylated Swe1", "Phosphorylated, modified Swe1"]
    assert swe1t[100] == pytest.approx(sum(report[p][100] for p in parts))
    plots = sorted(p.name for p in (output / "plots" / "simulation_1").iterdir())
    assert plots == [f"Figure_3{x}.plotly.json" for x in "abcd"]
    figure = json.loads((output / "plots" / "simulation_1" / "Figure_3a.plotly.json").read_text())
    assert [t["name"] for t in figure["data"]] == ["Sic1", "SBF", "Clb2", "Cln"] and len(figure["data"][0]["x"]) == 201


@pytest.mark.parametrize("solver", ["copasi", "tellurium"])
def test_the_repressilator_reports_species_and_constants(solver: str, tmp_path: Path) -> None:
    output = run_archive(FIXTURES / f"BIOMD0000000012.{solver}.omex", tmp_path)
    report = read_report(output / "reports" / "BIOMD0000000012_url" / "autogen_report_for_task1.csv")
    assert {"Time", "PX", "PY", "PZ", "X", "Y", "Z", "cell"} <= set(report)
    assert "Reaction1" not in report  # reaction rates: not returned by the generic solvers (X404)
    assert len(report["PX"]) == 1001


def score(a: list[float], b: list[float], rtol: float = 1e-4, atol_min: float = 1e-3, scale: float = 1e-5) -> float:
    """The platform's closeness score: below 1 is close."""
    atol = max(atol_min, max(abs(x) for x in a) * scale, max(abs(x) for x in b) * scale)
    return max(abs(x - y) / (atol + rtol * abs(y)) for x, y in zip(a, b, strict=True))


def test_copasi_and_tellurium_agree_on_ciliberto(tmp_path: Path) -> None:
    reports = {
        s: read_report(run_archive(FIXTURES / f"Ciliberto2003.{s}.omex", tmp_path / s) / "reports" / "simulation_1" /
                       "report.csv")
        for s in ("copasi", "tellurium")
    }  # fmt: skip
    scores = {label: score(reports["copasi"][label], reports["tellurium"][label]) for label in reports["copasi"]}
    far = {label: s for label, s in scores.items() if s >= 1}
    assert not far, f"COPASI and Tellurium disagree: {far}"
