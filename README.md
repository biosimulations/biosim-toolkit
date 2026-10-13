# pbsim-sedml

SED-ML adapter steps for [process-bigraph](https://github.com/vivarium-collective/process-bigraph): the parts of a
SED-ML task that do not depend on the simulator, written once.

process-bigraph-lang's `sedml translate` turns each task of a SED-ML file (a BioModels entry, a biosimulations.org
project, an upload) into a composite: a generic time-course solver (pbsim-common's COPASI or Tellurium step, or any
step with the same face) followed by

| Step | Does |
| --- | --- |
| `pbsim_sedml.DataGenerators` | the solver's `numeric_result` as the SED-ML data generators (linear combinations of result columns, time and model constants), the points before the output start dropped |
| `pbsim_sedml.Report` | one CSV per SED-ML report, its header the data sets' labels |
| `pbsim_sedml.Plots` | one Plotly figure (JSON, with data) per SED-ML plot |

compose-api runs the same task once per solver and compares the reports (compose-api `docs/plan-sedml.md`, decision
D11).

## Development

```bash
uv sync                # process-bigraph 1.0.5, bigraph-schema 1.0.14, pbsim-common, COPASI and Tellurium for the tests
uv run pytest
```

The end-to-end tests run committed instance archives (made by process-bigraph-lang's `sedml translate`) the way
compose-api's runner (pbest) does: a core with pbsim-common's types, `Composite(...)`, `run(...)`.
