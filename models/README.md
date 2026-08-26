# Model Artifacts

This directory stores serialized machine-learning pipelines and probability systems created by the FAA wildlife-strike modelling workflow.

Artifacts are organized according to the notebook that created them and their role as either intermediate candidates or approved final systems. Preserving the fitted preprocessing state is essential because downstream notebooks and the Streamlit dashboard must apply the same imputation, category encoding, feature ordering, calibration, and estimator configuration used during training.

Saved model systems may include or depend on:

- fitted preprocessing pipelines;
- fitted estimators;
- probability-calibration objects;
- feature manifests;
- target definitions;
- analytical thresholds used for evaluation;
- decision-gate metadata;
- support and interpretation warnings.

The final model directories act as the deployment handoff from the modelling notebooks to explainability, simulation, and the dashboard.

## Directory Structure

```text
models/
├── candidates/
│   ├── 05_damage_modelling/
│   ├── 07_severity_modelling/
│   └── 08_component_modelling/
│
└── final/
    ├── 06_calibration_validation/
    │   └── final_calibrated_pipeline.joblib
    │
    ├── 07_severity_modelling/
    │   └── final_known_severity_probability_system.joblib
    │
    └── 08_component_modelling/
        ├── engine_damage_component_probability_system.joblib
        ├── forward_cockpit_damage_component_probability_system.joblib
        ├── landing_gear_damage_component_probability_system.joblib
        ├── propeller_damage_component_probability_system.joblib
        └── wing_rotor_damage_component_probability_system.joblib
```

Candidate artifacts belong under:

```text
models/candidates/<notebook_stage>/
```

Approved downstream artifacts belong under:

```text
models/final/<notebook_stage>/
```

The model directory should remain a source-of-truth handoff for fitted predictive systems rather than a general storage location for arbitrary temporary objects.

---

## Candidate Artifacts

### `candidates/05_damage_modelling/`

Contains the tuned but uncalibrated binary aircraft-damage candidate pipelines produced by Notebook 05.

The candidate set includes combinations of:

- Logistic Regression;
- Random Forest;
- XGBoost;
- airport-aware feature sets;
- extended-geographic feature sets.

Notebook 06 consumes these candidates and performs:

- probability calibration;
- chronological validation;
- locked 2022–2024 final testing;
- unseen-airport generalization checks;
- support-tier analysis;
- final model selection.

These candidate artifacts are intermediate modelling outputs and must not be treated as the canonical project damage model.

### `candidates/07_severity_modelling/`

Contains candidate systems evaluated during the Notebook 07 severity-modelling stage.

Notebook 07 first investigates the original multiclass severity formulation among damaged incidents. Because the multiclass formulation did not provide the desired downstream reliability, the notebook applies its documented decision gate and retains a simplified known-severity binary formulation for operational use.

Candidate files remain modelling evidence. They are not loaded by the Streamlit application unless they have been explicitly promoted into the corresponding final-model directory.

### `candidates/08_component_modelling/`

Contains tuned intermediate component-damage models from Notebook 08.

Aircraft-component damage is treated as a multilabel problem. Separate binary probability systems are fitted for component targets that pass feasibility checks.

Candidate artifacts correspond to combinations of:

- component target;
- model family;
- feature set;
- hyperparameter configuration.

Only component targets that pass Notebook 08's complete validation and downstream-use decision gate are exported to `models/final/08_component_modelling/`.

### Candidate Git Policy

Candidate `.joblib` files are generated intermediate artifacts and may be very large. They are ignored by Git by default.

The repository should still preserve enough information to reproduce them through:

- notebooks;
- selected hyperparameters;
- metric tables;
- validation outputs;
- feature manifests;
- decision-gate outputs;
- notebook-specific `.gitkeep` files where needed.

---

## Final Artifacts

### `final/06_calibration_validation/`

Contains the canonical fitted-and-calibrated binary aircraft-damage probability pipeline selected by Notebook 06:

```text
final_calibrated_pipeline.joblib
```

This is the project's primary predictive artifact.

It estimates:

```text
P(reported aircraft damage | reported wildlife-strike scenario)
```

The selected system is the final calibrated probability pipeline established after model selection, calibration, chronological validation, and generalization checks.

Downstream notebooks and applications should load this final artifact rather than independently refitting or selecting another primary damage model.

It is consumed by:

- Notebook 09 explainability;
- Notebook 10 Monte Carlo simulation;
- `src/models/loaders.py`;
- `src/simulation/prediction.py`;
- the Streamlit What-If Simulation page;
- the Streamlit Scenario Comparison page.

The Monte Carlo simulation uses the model's continuous calibrated probability directly. The locked classification threshold is retained for analytical reporting and confusion-matrix evaluation, not as the simulation's decision rule.

---

### `final/07_severity_modelling/`

Contains the approved downstream severity probability system:

```text
final_known_severity_probability_system.joblib
```

The retained operational severity formulation is the simplified **known-severity binary system** produced by Notebook 07 after its decision gate.

Severity remains conditional on aircraft damage and usable severity information. It must not be interpreted as an unconditional probability across all wildlife-strike reports.

This artifact is consumed by the simulation prediction service after a simulated aircraft-damage outcome occurs.

---

### `final/08_component_modelling/`

Contains the component probability systems approved by Notebook 08 for downstream simulation:

```text
engine_damage_component_probability_system.joblib
forward_cockpit_damage_component_probability_system.joblib
landing_gear_damage_component_probability_system.joblib
propeller_damage_component_probability_system.joblib
wing_rotor_damage_component_probability_system.joblib
```

The retained component outcomes are:

- engine damage;
- forward-cockpit damage;
- landing-gear damage;
- propeller damage;
- wing/rotor damage.

The propeller system carries a lower-support warning relative to the stronger retained component targets.

Other component outcomes such as fuselage, tail, and lights remain descriptive-only where their predictive evidence did not justify operational use. The heterogeneous `DAM_OTHER` field is excluded from predictive simulation.

Component probabilities are:

```text
P(component damage | aircraft damage, scenario context)
```

They are modeled separately and are **not mutually exclusive**. A single damaging strike may affect multiple aircraft components, so component probabilities or simulated component frequencies are not expected to sum to 100%.

### Serialization Compatibility

Some Notebook 08 component artifacts were originally serialized with a notebook-local `BinaryProbabilityCalibrator` reference under `__main__`.

The current loader in:

```text
src/models/loaders.py
```

registers the required serialization compatibility before loading these artifacts so they can be deserialized correctly in Streamlit and other non-notebook execution contexts.

The component models were not retrained to resolve this issue; compatibility is handled by the loader.

---

## Runtime Model Loading

The dashboard and simulation layer should not load model files directly from individual Streamlit pages.

Model loading is centralized in:

```text
src/models/loaders.py
```

The important public loaders are:

```text
load_damage_model()
load_severity_model()
load_component_model(component)
load_all_component_models()
```

The simulation layer then uses:

```text
src/simulation/prediction.py
```

where `PredictionService()` loads the approved final systems internally.

The expected construction pattern is:

```python
prediction_service = PredictionService()
```

The service exposes probability predictions for:

- primary aircraft damage;
- severity conditional on damage;
- retained component outcomes conditional on damage.

This keeps Streamlit as a presentation/controller layer rather than duplicating model-loading or inference logic.

---

## Downstream Modelling Chain

The completed predictive chain is:

```text
Notebook 05
binary aircraft-damage candidate tuning
        ↓
models/candidates/05_damage_modelling/
        ↓
Notebook 06
calibration + chronological validation + canonical model selection
        ↓
models/final/06_calibration_validation/
        ↓
Notebook 07
severity modelling + decision gate
        ↓
models/final/07_severity_modelling/
        ↓
Notebook 08
component modelling + decision gates
        ↓
models/final/08_component_modelling/
        ↓
Notebook 09
explainability + geographic/generalization interpretation
        ↓
Notebook 10
Monte Carlo simulation + scenario comparison
        ↓
src/ reusable simulation services
        ↓
Streamlit dashboard
```

Notebook 09 does not create a replacement predictive model. It explains and audits the approved systems.

Notebook 10 also does not retrain the models. It operationalizes the saved final probability systems through historical donor sampling and Monte Carlo outcome generation.

---

## Streamlit Use

The current Streamlit application consumes the final model artifacts through reusable Python services.

### Page 03 — Damage Risk & Model Insights

Uses saved Notebook 06 and Notebook 09 outputs to present:

- final model performance;
- calibration and probability metrics;
- confusion-matrix evidence;
- unseen-airport/generalization analysis;
- grouped SHAP;
- permutation importance;
- directional explainability;
- airport-dependence diagnostics.

It does not retrain models or recompute expensive explainability analyses during normal dashboard use.

### Page 04 — Monte Carlo What-If Simulation

Uses the final damage, severity, and component systems through `PredictionService` and `SimulationEngine`.

The workflow is:

```text
supported Scenario
        ↓
historically compatible donor sampling
        ↓
final probability systems
        ↓
Monte Carlo outcome draws
        ↓
damage / severity / component results
```

### Page 05 — Scenario Comparison

Runs two supported scenarios under the same number of Monte Carlo trials and shared random seed.

The comparison emphasizes:

- Scenario A probability;
- Scenario B probability;
- absolute percentage-point difference;
- supplementary relative change;
- historical-support counts.

---

## Reproducibility

Serialized Python models can depend on the package versions used when they were created.

The repository therefore maintains compatible versions through the root:

```text
requirements.txt
```

Important model-runtime dependencies include:

- Python 3.12.x;
- pandas;
- NumPy;
- scikit-learn;
- XGBoost;
- joblib;
- SHAP for explainability workflows.

The reference notebook environment used Python 3.12.9.

Model binaries do not replace the analytical evidence used to justify them. The notebooks and `outputs/` directories remain the record of:

- hyperparameter selection;
- validation metrics;
- calibration results;
- threshold analysis;
- confusion matrices;
- feature manifests;
- generalization checks;
- explainability outputs;
- decision gates;
- methodological interpretation.

---

## Git Policy

The root `.gitignore` ignores `.joblib` files by default because candidate models and some fitted pipelines can be large.

Candidate model binaries remain ignored.

The final artifacts required by the current operational dashboard are explicitly allowed in Git:

```text
models/final/06_calibration_validation/final_calibrated_pipeline.joblib

models/final/07_severity_modelling/final_known_severity_probability_system.joblib

models/final/08_component_modelling/engine_damage_component_probability_system.joblib
models/final/08_component_modelling/forward_cockpit_damage_component_probability_system.joblib
models/final/08_component_modelling/landing_gear_damage_component_probability_system.joblib
models/final/08_component_modelling/propeller_damage_component_probability_system.joblib
models/final/08_component_modelling/wing_rotor_damage_component_probability_system.joblib
```

These files are deployment dependencies for the current Streamlit simulation.

If any required final artifact later exceeds normal GitHub limits, Git LFS or another explicit artifact-distribution mechanism should be used rather than silently removing the model from the reproducible application workflow.

---

## Current Status

The model-development workflow is complete through Notebook 10.

### Primary damage system

Notebook 05 produced six tuned, uncalibrated binary aircraft-damage candidate pipelines.

Notebook 06 selected, calibrated, and validated the canonical binary-damage probability system and exported:

```text
models/final/06_calibration_validation/final_calibrated_pipeline.joblib
```

This is the primary predictive system used throughout the remainder of the project.

### Severity system

Notebook 07 completed the severity experiment and decision gate.

The approved downstream artifact is:

```text
models/final/07_severity_modelling/final_known_severity_probability_system.joblib
```

### Component systems

Notebook 08 completed component modelling and exported five approved probability systems:

- engine;
- forward cockpit;
- landing gear;
- propeller;
- wing/rotor.

These are the only component probability systems currently used by the operational simulation.

### Explainability

Notebook 09 explains and audits the final probability systems. Its outputs are stored under `outputs/09_explainability/` rather than in the model directory because they are analytical evidence rather than replacement model artifacts.

### Simulation and dashboard

Notebook 10 established the Monte Carlo methodology.

That behavior has since been operationalized under `src/simulation/` and connected to the Streamlit dashboard.

The current dashboard successfully loads the saved final models and uses them for:

- historically supported what-if simulation;
- conditional severity outcomes;
- conditional component outcomes;
- controlled scenario comparison.

No model retraining is required during normal dashboard execution.

---

## Interpretation Boundary

The existence of a final model artifact means that the model passed the project's documented downstream-use decision process. It does not imply that the model is a causal aviation model or a universal operational safety system.

The primary output remains conditional on a reported wildlife strike. Severity and component systems are further conditional downstream quantities.

All model outputs should therefore be interpreted together with:

- historical support;
- model validation evidence;
- reporting limitations;
- geographic generalization limits;
- distribution-shift risk;
- the project disclaimer and formal notebook/report limitations.
