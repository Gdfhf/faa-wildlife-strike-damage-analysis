# Model Artifacts

This directory stores serialized machine-learning pipelines and probability systems created by the wildlife-strike modelling workflow.

Artifacts are organized according to the notebook that creates them and their role as either intermediate candidates or approved final models. Preserving the fitted preprocessing state is important because later notebooks must apply the same imputation, category encoding, feature ordering, scaling, calibration, and model settings used during training.

Depending on the modelling stage, saved artifacts may also contain calibration objects, thresholds, feature manifests, target definitions, support warnings, and decision-gate metadata.

## Directory structure

Model artifacts are grouped by the notebook that creates them.

```text
models/
├── candidates/
│   ├── 05_damage_modelling/
│   ├── 07_severity_modelling/
│   └── 08_component_modelling/
│
└── final/
    ├── 06_calibration_validation/
    ├── 07_severity_modelling/
    └── 08_component_modelling/
```

Future notebooks should preserve the same convention: candidate artifacts belong under `models/candidates/<notebook_stage>/`, while approved final artifacts belong under `models/final/<notebook_stage>/` for the notebook that creates them.

## Candidate artifacts

### `candidates/05_damage_modelling/`

Contains the tuned but uncalibrated binary aircraft-damage candidate pipelines produced by Notebook 05.

The candidate set includes combinations of:

- Logistic Regression;
- Random Forest;
- XGBoost;
- airport-aware features;
- extended-geographic features.

These candidates are consumed by Notebook 06, where calibration, chronological validation, airport-held-out validation, and final model selection are performed.

They are intermediate modelling artifacts and must not be treated as the canonical project model.

### `candidates/07_severity_modelling/`

Contains candidate models produced during the secondary severity-modelling experiment.

The primary severity experiment evaluates the multiclass severity outcome among damaged incidents. Notebook 07 subsequently applies its decision gate and may simplify the severity formulation when the original multiclass target is not sufficiently reliable.

These files document the modelling experiment and are not used directly by the simulation unless explicitly promoted through the Notebook 07 decision gate.

### `candidates/08_component_modelling/`

Contains the tuned best-estimator pipelines from Notebook 08.

Notebook 08 treats aircraft-component damage as a multilabel problem and fits separate binary models for component targets that pass the feasibility gate. Candidate artifacts correspond to combinations of component target, model family, and feature set.

These are uncalibrated intermediate artifacts. Only component models that pass the complete Notebook 08 validation and decision gate may be used downstream.

### Future candidate directories

If later notebooks create additional candidate models, they should use a notebook-specific subdirectory following the same naming pattern. Candidate files are generated intermediate outputs and may be ignored by Git when they are large, provided that the notebooks, selected hyperparameters, metrics, manifests, and decision outputs required to reproduce them remain version-controlled.

## Final artifacts

### `final/06_calibration_validation/`

Contains the canonical fitted-and-calibrated binary aircraft-damage probability pipeline selected by Notebook 06:

`final_calibrated_pipeline.joblib`

This is the primary predictive artifact for the project and estimates reported aircraft-damage probability conditional on a reported wildlife strike.

Downstream explainability, Monte Carlo simulation, and interfaces should load this canonical artifact rather than independently fitting or selecting another binary-damage model.

### `final/07_severity_modelling/`

Reserved for the approved secondary severity probability system produced by Notebook 07.

The original multiclass severity formulation is subject to an explicit decision gate. The currently retained downstream formulation is the simplified known-severity binary model only if it satisfies the notebook's validation criteria.

Severity remains a secondary project component and must not be used in the simulation unless it passes this gate.

### `final/08_component_modelling/`

Contains only component probability systems that pass the Notebook 08 decision gate.

The retained component outcomes are:

- engine damage;
- wing/rotor damage;
- forward cockpit damage;
- landing-gear damage;
- propeller damage, with an explicit lower-support warning.

Fuselage, tail, and lights damage remain descriptive-only outcomes, while the heterogeneous `DAM_OTHER` field is excluded from predictive simulation.

Component probabilities are conditional on aircraft damage having occurred. Because separate component models are fitted independently, their probabilities must not be interpreted as a complete model of dependence or physical damage propagation among aircraft components.

### Future final directories

Future modelling notebooks should save approved final artifacts only after their own validation and decision gates are complete. Final artifacts should be placed under `models/final/<notebook_stage>/` and should be documented with enough metadata for downstream notebooks to identify:

- the target or analytical purpose;
- the population condition;
- the exact feature set;
- the fitted preprocessing and estimator;
- calibration information where applicable;
- thresholds used only for reporting or classification summaries;
- training, validation, and final-test periods;
- support or uncertainty warnings;
- the notebook decision that authorized downstream use.

A later notebook should consume an upstream final artifact rather than redefine, retrain, or silently replace it unless the methodology explicitly requires a new modelling stage.

## Reproducibility

Serialized Python models may depend on the package versions used when they were created. The project environment should therefore preserve compatible versions of at least:

- Python;
- pandas;
- NumPy;
- scikit-learn;
- XGBoost;
- joblib.

Model artifacts should not replace the notebooks, selected hyperparameters, metrics, feature manifests, validation outputs, calibration results, or decision tables. Those files provide the evidence needed to reproduce and audit the modelling decisions.

Large model artifacts, particularly Random Forest pipelines, may exceed normal GitHub size limits. Intermediate candidates may therefore remain local, be shared separately, or be managed with Git LFS. Final artifacts should be tracked only when their size and deployment needs make ordinary Git storage appropriate.

## Downstream use

The current modelling chain is:

```text
Notebook 05
binary damage candidate tuning
        ↓
models/candidates/05_damage_modelling/
        ↓
Notebook 06
calibration + validation + canonical binary model selection
        ↓
models/final/06_calibration_validation/
        ↓
Notebook 07
secondary severity decision gate
        ↓
models/final/07_severity_modelling/
        ↓
Notebook 08
secondary component decision gates
        ↓
models/final/08_component_modelling/
        ↓
future explainability, simulation, and interface notebooks
```

Future notebooks should treat the model directories as a source-of-truth handoff rather than as a general storage location for arbitrary fitted objects.

## Current status

Notebook 05 produces six tuned, uncalibrated binary-damage candidate pipelines in:

`models/candidates/05_damage_modelling/`

Notebook 06 consumes those candidates, performs calibration and generalizability analysis, and exports the canonical binary-damage probability system to:

`models/final/06_calibration_validation/final_calibrated_pipeline.joblib`

Notebook 07 evaluates severity among damaged incidents. The original multiclass formulation is retained as modelling evidence, while the simplified known-severity binary formulation is the only severity system eligible for downstream use after passing its decision gate.

Notebook 08 evaluates aircraft-component damage as a multilabel problem. It stores tuned intermediate candidates in:

`models/candidates/08_component_modelling/`

and exports only decision-gate-approved component probability systems to:

`models/final/08_component_modelling/`

Generated `.joblib` artifacts may be ignored by Git by default because some models, particularly Random Forest pipelines, can be hundreds of megabytes. The canonical Notebook 06 model and any other final artifacts required for deployment may be explicitly permitted by `.gitignore` or managed through Git LFS when appropriate.
