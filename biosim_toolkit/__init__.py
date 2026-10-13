"""biosim-toolkit: trusted utilities for process-bigraph simulations, collected in one package.

Areas, each a subpackage or module:

- `biosim_toolkit.sedml`: SED-ML adapter steps (data generators, reports, plots) around a generic time-course solver;
- `biosim_toolkit.data`: time courses as named series, linear combinations;
- `biosim_toolkit.reports`: CSV tables;
- `biosim_toolkit.viz`: Plotly figures.

Model adapters and format adapters join as their own subpackages. Steps are registered by process-bigraph's
discovery under their defining module, e.g. `local:biosim_toolkit.sedml.Report`.
"""

__version__ = "0.1.0"
