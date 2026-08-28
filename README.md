# FAA Wildlife Strike Damage Analysis

**Explainable Scenario-Based Simulation of Aircraft Damage Consequences Among Reported Wildlife Strikes Using FAA Data**

This repository contains the analytical and software components of a Master of Data Analytics capstone project investigating aircraft-damage consequences among reported wildlife strikes.

The project uses data from the Federal Aviation Administration (FAA) National Wildlife Strike Database to examine relationships between aircraft, wildlife, flight, temporal, geographic, and environmental characteristics and reported aircraft damage.

> **Scope:** the analysis is conditional on a wildlife strike having already occurred. The project does **not** estimate the probability that an ordinary flight will experience a wildlife strike, and it is not a collision-physics simulator.

## Project Objectives

The project aims to:

- analyze historical factors associated with aircraft damage among reported wildlife strikes;
- develop and evaluate machine-learning models that estimate conditional aircraft-damage probabilities;
- assess model generalizability across future reporting periods and airports excluded from model training;
- calibrate and interpret predictive models;
- model conditional damage severity and affected aircraft components where supported by the data;
- use scenario-based Monte Carlo simulation to represent probabilistic consequence outcomes;
- compare historically supported what-if scenarios under common simulation settings;
- communicate historical, model, and simulation results through an interactive Streamlit dashboard;
- provide an optional Godot-based 2D visualization of already-realized Monte Carlo trials.

The Godot layer is a secondary illustrative interface only. Scientific, predictive, sampling, severity, and component-outcome logic remains in Python. Godot does not independently rerun the models or perform a physical collision simulation.

## Data Source

The project uses the **FAA National Wildlife Strike Database**, accessed through the U.S. Department of Transportation open-data platform.

The raw FAA source data and the large canonical processed analytical CSV are **not stored in Git**.

The canonical analytical dataset used by the completed notebook workflow contains:

- 319,107 reported wildlife-strike records;
- an analytical period of 1990–2024;
- aircraft, wildlife, operational, temporal, geographic, environmental, damage, severity, and component information.

For dashboard use, the project generates much smaller runtime artifacts so Streamlit does not need to load the approximately 300 MB analytical CSV on every run.

### Dashboard runtime artifacts

The following lightweight artifacts are intentionally suitable for Git distribution because the dashboard depends on them at runtime:

- `historical_explorer.parquet` — historical dashboard data for 1990–2024;
- `simulation_donor_pool.parquet` — empirical Monte Carlo donor population restricted to 1990–2021;
- `scenario_support.parquet` — historical support reference restricted to 1990–2021;
- `overview_summary.json` — lightweight overview KPI summary.

Together, the Parquet runtime artifacts are approximately 12 MB.

The exact locations of these artifacts are centralized through `src/utils/paths.py`, and dashboard pages access them through `src/data/loaders.py`.

## Analytical Approach

The completed analytical workflow follows a CRISP-DM-style progression:

1. Data understanding and quality assessment
2. Data preparation and feature governance
3. Descriptive and inferential analysis
4. Binary aircraft-damage modelling
5. Model selection and hyperparameter tuning
6. Probability calibration and locked temporal validation
7. Conditional damage-severity modelling
8. Conditional component-damage modelling
9. Explainability and generalization analysis
10. Scenario-based Monte Carlo simulation and comparison

The primary predictive task estimates:

$$
P(reported\ aircraft\ damage\ |\ reported\ wildlife\ strike\ scenario)
$$

The final operational simulation uses calibrated probabilities rather than converting every model output to a binary class label.

## Streamlit Dashboard

The Streamlit application is the operational integration layer of the project. It reuses saved analytical artifacts and trained models instead of retraining models or recomputing expensive explainability analyses during normal dashboard use.

The application now uses an explicit **Home / landing page** plus six numbered analytical pages:

1. **Project Overview**  
   Headline dataset KPIs, major historical patterns, model-system overview, and the project analytical workflow.

2. **Historical Data**  
   Interactive filtering of historical reported strikes, damage rates, operational factors, wildlife, severity, and component patterns.

3. **Damage Risk & Model Insights**  
   Locked final-model performance, confusion-matrix evidence, temporal/geographic generalization diagnostics, SHAP/permutation explainability, airport dependence, and downstream model status.

4. **Monte Carlo Simulation**  
   Guided scenario construction with cascading historically supported required inputs, optional historical sampling or explicit overrides, historical-support diagnostics, aircraft-damage simulation, and conditional severity/component outcomes.

5. **Scenario Comparison**  
   Controlled A/B comparison under a shared scenario context. Users select one comparison variable when possible, both scenarios use the same Monte Carlo trial count and random seed, and percentage-point differences are emphasized over relative percentage changes.

6. **How to Read the Dashboard**  
   User-facing guidance explaining historical statistics, modeled probabilities, Monte Carlo outcomes, support limitations, counterfactual overrides, conditional outcomes, uncertainty, and common interpretation mistakes.

The **Home** page provides direct internal links to the recommended analytical and simulation pages and mirrors the numbered sidebar navigation.


### Optional Godot single-trial visualizer

Page 04 includes two optional visualization actions after a Monte Carlo simulation has completed:

- **Visualize Random Trial** — displays a randomly retained realization from the current simulation run.
- **Visualize High-Impact Trial** — displays an intentionally selected consequential realized case from the same run. Selection prioritizes realized severe damage and then the number of realized damaged components.

Both visualizations consume a trial that has already been realized by the Python simulation engine. The Godot application does **not** rerun the model, resample the outcome, or simulate aircraft-wildlife collision physics.

The visualization represents scenario context such as aircraft class, aircraft mass group, wildlife type/size, phase of flight, time of day, sky condition, precipitation, realized damage, severity, and modeled component outcomes using a schematic 2D scene with audio/visual effects.

#### Standalone Windows build

The visualizer is exported as a **Windows x86_64 standalone executable**. A user does not need to install the Godot editor to run the compiled visualizer.

Because the compiled executable is approximately 145 MB, it is **not stored in normal Git history**. The precompiled build is distributed through the project's [GitHub Releases](https://github.com/Gdhf/faa-wildlife-strike-damage-analysis/releases/tag/v1.0.0).

To enable the visualization buttons in a cloned repository:

1. Download [`CapstoneAirstrikeVisualizer.exe`](https://github.com/Gdhf/faa-wildlife-strike-damage-analysis/releases/download/v1.0.0/CapstoneAirstrikeVisualizer.exe).
2. Place the executable at:

   ```text
   godot/builds/CapstoneAirstrikeVisualizer.exe
   ```

3. Run the Streamlit dashboard normally.
4. On Page 04, run a supported Monte Carlo scenario.
5. Select **Visualize Random Trial** or **Visualize High-Impact Trial**.

When a visualization button is selected, Streamlit writes the selected realized trial to:

```text
godot/data/latest_trial.json
```

The standalone Godot executable reads that external JSON file at runtime and displays the current trial.

If the executable is not present, Page 04 leaves the analytical dashboard fully functional, shows installation guidance, and disables the two visualization buttons rather than failing at launch.

The precompiled visualizer currently targets Windows x86_64. The Godot source project and export preset remain in the repository so the visualization can be inspected, reproduced, or exported for another supported platform if required.

### Important simulation behavior

Required scenario context includes:

- airport or FAA region;
- aircraft class;
- aircraft mass group;
- season;
- phase of flight.

The dashboard narrows these selections using the historical support population so users are guided toward combinations that actually exist in the reference data.

Two support concepts are intentionally distinguished:

- **Required-context support** determines whether a simulation is allowed to run. If the required combination has no exact support in the 1990–2021 simulation reference population, the simulation is blocked.
- **Full specified-context support** is checked when optional values are explicitly overridden. It measures whether the complete combination of required and specified optional values was observed in the historical donor data.

If required-context support exists but full specified-context support is zero, the simulation may still run as a **counterfactual override**, but the dashboard explicitly warns that the estimate extends beyond an exactly observed historical combination and should be interpreted with greater caution.

Optional fields may be specified manually or left as **Historical sampling**. When left unspecified, compatible whole historical donor rows are sampled so jointly observed relationships among optional variables are preserved.

`NUM_STRUCK` is treated as an ordered categorical variable in the operational system rather than as an arbitrary exact integer. Historical categories include values such as:

- `1`
- `2–10`
- `11–100`
- `More than 100`

The operational default is **10,000 Monte Carlo trials** with a reproducible random seed.

## Repository Structure

```text
faa-wildlife-strike-damage-analysis/
│
├── dashboard/
│   ├── app.py                         # Streamlit entry point and explicit navigation/router
│   ├── app/
│   │   ├── Home.py                    # Dashboard landing/navigation page
│   │   └── pages/
│   │       ├── 01_Project_Overview.py
│   │       ├── 02_Historical_Data.py
│   │       ├── 03_Damage_Risk.py
│   │       ├── 04_Monte_Carlo_Simulation.py
│   │       ├── 05_Scenario_Comparison.py
│   │       └── 06_How_to_Read_the_Dashboard.py
│   └── components/                    # Shared layout, metric, chart, and theme helpers
│
├── data/
│   ├── raw/                           # Raw source data (not tracked by Git)
│   ├── processed/                     # Large processed research data ignored
│   └── dashboard/                     # Lightweight dashboard artifacts allowed
│
├── godot/
│   ├── assets/                        # Aircraft, wildlife, environment, effect, and audio assets
│   ├── builds/                        # Local standalone exports (compiled binary ignored by Git)
│   ├── data/
│   │   └── latest_trial.json          # Runtime payload written by Streamlit
│   ├── scenes/                        # Godot scenes
│   ├── scripts/                       # Visualization controllers and trial loader
│   ├── ATTRIBUTION.md                 # Third-party asset/audio attribution
│   ├── export_presets.cfg             # Reproducible Godot export configuration
│   └── project.godot                  # Godot project definition
│
├── models/
│   ├── candidates/                    # Candidate binaries generally ignored
│   └── final/                         # Required final model artifacts allow-listed
│
├── docs/                              # Documentation for audits, decision-making and official sources
├── notebooks/                         # Research notebooks 01–10
├── outputs/                           # Saved validation / explainability outputs
├── simulation/                        # Exported scenario/result files
├── src/
│   ├── data/                          # Dashboard artifact builders/loaders
│   ├── models/                        # Saved-model loading compatibility
│   ├── simulation/                    # Scenario, support, donor, prediction, engine logic
│   └── utils/                         # Centralized project paths and reusable display-label utilities
│
├── scripts/
│   ├── run_dashboard.bat              # Script to start up the dashboard
│   ├── refresh_requirements.bat       # Update required libraries to the environment
│   ├── run_tests.bat                  # Runs the tests inside tests folder
│   └── setup_windows.bat              # Environment set-up for Windows
│ 
├── tests/
│   └── test_simulation.py             # Compact permanent simulation test suite
│
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the repository

Clone or pull the repository and open a terminal in the repository root.

### 2. Create and activate a Python 3.12 environment

The project is developed for **Python 3.12.x**. The reference notebook environment used Python 3.12.9.

Example with `venv`:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

The shortcut script, which currently only works on Windows, is the following. It will also install the needed dependencies inside `requirements.txt`.

```bash
setup_windows.bat
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The dashboard uses Parquet runtime artifacts, so a Parquet engine is included in `requirements.txt`.

## Running the Dashboard

Run Streamlit **from the repository root** so the `src` package and repository-relative artifact paths resolve correctly.

Recommended command:

```bash
python -m streamlit run dashboard/app.py
```

If the repository includes the Windows launcher, the equivalent shortcut is:

```text
run_dashboard.bat
```

Streamlit will print a local address, normally similar to:

```text
http://localhost:8501
```

Open that address in a web browser if it does not open automatically.

### What must be present for the dashboard to run?

Git intentionally excludes the raw FAA dataset, the large processed analytical CSV, candidate model binaries, caches, and other generated research data.

A teammate who only wants to **run the dashboard** should not need the large raw/canonical dataset as long as the branch contains:

- the lightweight dashboard Parquet/JSON artifacts;
- the allow-listed final damage model;
- the final severity model;
- the five retained component model artifacts;
- the saved Notebook 06/09 output files consumed by the model-insight page;
- the Python source under `src/`;
- the Streamlit files under `dashboard/`.

The optional Godot single-trial visualization additionally requires the standalone Windows executable at:

```text
godot/builds/CapstoneAirstrikeVisualizer.exe
```

If that file is absent, the dashboard still runs normally; Page 04 disables only the visualization buttons and provides instructions for obtaining the build from GitHub Releases.

If the lightweight dashboard artifacts are missing, regenerate them from the canonical analytical dataset with:

```bash
python src/data/build_dashboard_artifacts.py
```

That regeneration step requires the canonical processed dataset at the location expected by `src/utils/paths.py`.

## Testing

A compact automated test suite validates the highest-value operational simulation constraints.

Run:

```bash
pytest
```

or, on Windows when the launcher is present:

```text
run_tests.bat
```

The permanent tests cover areas such as:

- structural scenario validation;
- zero-support handling;
- exclusion of the 2022–2024 held-out period from simulation donors;
- preservation of required scenario values during donor sampling;
- probability bounds;
- random-seed reproducibility;
- conditional severity/component count constraints;
- valid aggregate simulation rates.

## Git / Data Policy

The repository intentionally does **not** track:

- raw FAA datasets;
- the large canonical processed CSV;
- general Parquet/Feather/Pickle artifacts;
- candidate model binaries;
- Godot-generated cache/import data;
- compiled Godot builds such as `godot/builds/CapstoneAirstrikeVisualizer.exe`;
- logs, caches, virtual environments, and local secrets.

Exceptions are made for the small runtime artifacts and final trained-model files required to reproduce the current Streamlit dashboard.

The Godot source project, assets, scripts, attribution, and `export_presets.cfg` are version controlled for reproducibility. The much larger precompiled Windows executable is distributed separately through GitHub Releases rather than normal Git history.

This separation keeps the repository practical while allowing teammates to reproduce the analytical application and optionally install the precompiled visualization without installing Godot.

## Current Project Status

The analytical notebooks are effectively complete through Notebook 10.

The Streamlit dashboard is now **functionally and visually complete for the capstone implementation scope**:

- reusable data/model loaders are operational;
- the compact automated simulation tests pass;
- historical dashboard artifacts are validated;
- explicit numbered navigation and the Home landing page are operational;
- the Overview page has been visually and structurally redesigned;
- the Historical Data page is responsive and uses interactive Plotly charts;
- the Damage Risk & Model Insights page is visually consolidated and artifact-driven;
- the Monte Carlo simulator is operational with cascading required-context support;
- optional historical sampling and explicit counterfactual overrides are supported;
- required-context and full specified-context support are distinguished;
- human-readable airport, aircraft, engine, and state/location labels are integrated;
- `NUM_STRUCK` is handled consistently as an ordered categorical field;
- conditional severity and component simulation is operational;
- Scenario Comparison uses a controlled shared-context A/B design;
- optional comparison values are constrained to historically observed values under the selected shared context;
- the user-facing interpretation guide reflects the final simulation and comparison behavior;
- responsive desktop/mobile presentation has been checked during development;
- shared layout, chart, metric, and theme helpers are in use across the dashboard.

The optional Godot visualization is also implemented and integrated:

- Page 04 can export either a randomly retained trial or an intentionally selected high-impact realized trial;
- the visualization consumes the Python-generated `latest_trial.json` payload rather than reproducing analytical logic in Godot;
- aircraft, wildlife, weather, damage, outcome, and audio presentation are implemented;
- the Windows x86_64 standalone build has been exported and tested independently;
- the exported application reads the external runtime JSON so newly generated Streamlit trials are reflected without rebuilding the executable;
- Page 04 detects whether the standalone executable is installed and gracefully disables the visualization actions when it is absent;
- the standalone Windows build is distributed through the project's GitHub Releases rather than normal Git history.

Remaining work is primarily:

- final regression and fresh-environment QA;
- final documentation and attribution synchronization;
- Streamlit Community Cloud deployment, if retained in the final delivery plan;
- presentation/demo preparation.

## Interpretation Notes

Three different result types appear in the dashboard:

- **Historical statistic** — observed among historical reported records satisfying dashboard filters.
- **Model estimate** — calibrated conditional probability produced by a fitted model.
- **Monte Carlo estimate** — simulated consequence outcome after integrating over compatible historical context and stochastic draws.

These quantities should not be treated as interchangeable.

For simulation support:

- **required-context support** determines whether the scenario may run;
- **full specified-context support** describes whether explicitly selected optional values were observed together with that required context;
- a counterfactual optional override may therefore have zero full specified-context support even when the required scenario remains eligible for simulation.

For Scenario Comparison, modeled probability and **percentage-point differences** are the primary comparison quantities. Relative percentage change is secondary context, and realized Monte Carlo rates contain random simulation noise.

More Monte Carlo trials reduce random simulation noise, but they do **not** remove model uncertainty, reporting bias, sparse historical support, or future distribution shift.

## Team

Master of Data Analytics Capstone Project  
University of Niagara Falls Canada  
Summer 2026

### Team Members

- David Enrique Garcia Olvera
- Kenan Kilic
- Hai Yen Nguyen
- Minh Phuong Nhan

## Disclaimer

This project is an academic analytical investigation based on historical reported wildlife-strike data.

Model and simulation outputs are conditional, probabilistic estimates. They should not be interpreted as predictions that a specific flight will experience a wildlife strike, as physical simulations of aircraft-wildlife impacts, or as operational aviation safety thresholds.

The project is not intended to replace FAA guidance, aircraft inspections, wildlife-management practices, or professional aviation safety and operational decision-making.

The Godot visualization is schematic and illustrative. Visual/audio effects communicate the already-realized Python trial and should not be interpreted as a physical reconstruction of a wildlife strike or as an engineering damage simulation.

## License

The code developed in this repository is available under the MIT License.

The FAA wildlife-strike data are obtained from an external public data source and are not covered by this repository's MIT License.
