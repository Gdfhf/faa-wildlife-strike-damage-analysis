# Model Artifacts

This directory stores serialized machine-learning pipelines created by the
wildlife-strike damage modelling workflow.

The saved files contain both the fitted preprocessing steps and the fitted
classifier. This is important because later notebooks must apply the same
imputation, category encoding, feature ordering, scaling, and model settings
used during training.

## Directory structure

### `candidates/`

Contains the uncalibrated candidate pipelines produced by
`05_damage_modelling_consolidated.ipynb`.

Candidate models may include:

- logistic regression;
- Random Forest;
- XGBoost;
- extended-geographic feature variants;
- airport-aware feature variants.

These files are retained so Notebook 06 can compare calibration methods and
validation designs without repeating the full tuning process.

The candidate artifacts are intermediate outputs. They are not the final
project model and should not be used directly by the simulation or user
interface.

Some candidate files, especially Random Forest pipelines, may be too large for
ordinary GitHub tracking. Large intermediate artifacts may therefore remain
local, be shared separately, or be managed with Git LFS.

### `final/`

Reserved for the canonical fitted-and-calibrated pipeline selected after
Notebook 06.

Only a model that passes the required calibration, chronological validation,
airport-held-out validation, and support checks should be placed here.

Downstream components should load the canonical artifact from this directory,
including:

- explainability analysis;
- Monte Carlo simulation;
- the Streamlit application;
- any secondary interface such as Godot.

## Reproducibility

Serialized Python models may depend on the package versions used when they were
created. The project environment should therefore preserve compatible versions
of at least:

- Python;
- pandas;
- NumPy;
- scikit-learn;
- XGBoost;
- joblib.

Model artifacts should not replace the notebooks, selected hyperparameters,
metrics, feature manifests, or validation outputs. Those files provide the
evidence needed to reproduce and audit the modelling decisions.

## Current status

Notebook 05 produces uncalibrated candidate models in `models/candidates/`.

Notebook 06 will determine which candidate, calibration method, and validation
configuration are acceptable. It will then save one canonical calibrated
pipeline in `models/final/`.