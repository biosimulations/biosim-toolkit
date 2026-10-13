# biosim-toolkit

Trusted utilities for [process-bigraph](https://github.com/vivarium-collective/process-bigraph) simulations, collected
in one package: the steps and functions that do not depend on any one simulator, reviewed and tested once.

| Area | Module | What |
| --- | --- | --- |
| SED-ML adapters | `biosim_toolkit.sedml` | `DataGenerators`, `Report`, `Plots`: the solver-agnostic parts of a SED-ML task |
| Data | `biosim_toolkit.data` | time courses as named series; linear combinations |
| Reports | `biosim_toolkit.reports` | CSV tables |
| Visualization | `biosim_toolkit.viz` | Plotly figures (JSON) |

Model adapters and format adapters join as their own subpackages.

Steps are registered by process-bigraph's discovery under their defining module: `local:biosim_toolkit.sedml.Report`.

## SED-ML

process-bigraph-lang's `sedml translate` turns each task of a SED-ML file (a BioModels entry, a biosimulations.org
project, an upload) into a composite: a generic time-course solver (pbsim-common's COPASI or Tellurium step, or any
step with the same face), then `DataGenerators` (the solver's result as the SED-ML data generators, the points before
the output start dropped), `Report` (a CSV per SED-ML report) and `Plots` (a Plotly figure per SED-ML plot).
compose-api runs a task once per solver and compares the reports (compose-api `docs/plan-sedml.md`).

## Development

```bash
uv sync                               # process-bigraph 1.0.5, bigraph-schema 1.0.14, pbsim-common, COPASI, Tellurium
uv pip install --reinstall --no-deps .  # discovery reads installed metadata, which an editable install hides
uv run --no-sync pytest
```

The end-to-end tests run instance archives made by process-bigraph-lang's `sedml translate`
(`tests/fixtures/<model>.<solver>.omex`) the way compose-api's runner (pbest) does: a core with pbsim-common's types,
`Composite(...)`, `run(...)`.

Releases: a GitHub release publishes the wheel to PyPI by trusted publishing (`.github/workflows/release.yml`).
