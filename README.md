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
- communicate historical, model, and simulation results through an interactive Streamlit dashboard.

An optional Godot visualization layer may be explored only if time remains. Scientific and predictive logic remains in Python.

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

The current dashboard contains six user-facing analytical pages:

1. **Project Overview**  
   Headline dataset KPIs and major historical patterns.

2. **Historical Wildlife Strike Explorer**  
   Interactive filtering of historical reported strikes, damage rates, operational factors, wildlife, severity, and component patterns.

3. **Damage Risk & Model Insights**  
   Locked final-model performance, confusion-matrix evidence, generalization diagnostics, SHAP/permutation explainability, and downstream model status.

4. **Monte Carlo What-If Simulation**  
   Guided scenario construction with cascading historically supported inputs, historical-support validation, empirical donor sampling, aircraft-damage simulation, and conditional severity/component outcomes.

5. **Scenario Comparison**  
   Side-by-side comparison of two supported scenarios using the same Monte Carlo trial count and random seed, emphasizing percentage-point differences.

6. **How to Read This Dashboard**  
   User-friendly guidance explaining historical statistics, model probabilities, Monte Carlo estimates, conditional outcomes, support limitations, and common interpretation mistakes.

### Important simulation behavior

Required scenario context includes:

- airport or FAA region;
- aircraft class;
- aircraft mass group;
- season;
- phase of flight.

The dashboard narrows these selections using the historical support population so users are guided toward combinations that actually exist in the reference data.

Optional fields may be specified manually or left as **Historical sampling**. When left unspecified, compatible whole historical donor rows are sampled so jointly observed relationships among optional variables are preserved.

The operational default is **10,000 Monte Carlo trials** with a reproducible random seed.

## Repository Structure

```text
faa-wildlife-strike-damage-analysis/
│
├── dashboard/
│   ├── app.py                         # Main Streamlit entry point
│   ├── app/
│   │   └── pages/
│   │       ├── 01_Project_Overview.py
│   │       ├── 02_Historical_Data.py
│   │       ├── 03_Damage_Risk.py
│   │       ├── 04_Monte_Carlo_Simulation.py
│   │       ├── 05_Scenario_Comparison.py
│   │       └── 06_How_to_Read_the_Dashboard.py
│   └── components/                    # Shared presentation helpers
│
├── data/
│   ├── raw/                           # Raw source data (not tracked by Git)
│   ├── processed/                     # Large processed research data ignored;
│   └── dashboard/                     # lightweight dashboard artifacts allowed
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
│   └── utils/                         # Centralized project paths
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
The shortcut script, which currently only works on Windows is the following. It will also install the needed dependencies inside `requirements.txt`.
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
- logs, caches, virtual environments, and local secrets.

Exceptions are made for the small runtime artifacts and final trained-model files required to reproduce the current Streamlit dashboard.

This separation keeps the repository practical while allowing teammates to run the operational application without rebuilding the full analytical workflow.

## Current Project Status

The analytical notebooks are effectively complete through Notebook 10.

The dashboard is now **functionally feature-complete for its first implementation pass**:

- reusable data/model loaders are operational;
- the compact automated simulation tests pass;
- historical dashboard artifacts are validated;
- the Overview page is functional;
- the Historical Explorer is functional;
- the Model Insights page is functional;
- the Monte Carlo simulator is functional;
- cascading supported scenario inputs are operational;
- conditional severity and component simulation is operational;
- Scenario Comparison is functional;
- the user-facing interpretation guide is functional.

Remaining work is primarily:

- presentation and UX refinement, especially the Model Insights page;
- visual consistency across pages;
- selected chart improvements;
- final fresh-environment/reproducibility checks;
- final demonstration and documentation polish.

## Interpretation Notes

Three different result types appear in the dashboard:

- **Historical statistic** — observed among historical reported records satisfying dashboard filters.
- **Model estimate** — calibrated conditional probability produced by a fitted model.
- **Monte Carlo estimate** — simulated consequence outcome after integrating over compatible historical context and stochastic draws.

These quantities should not be treated as interchangeable.

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

## License

The code developed in this repository is available under the MIT License.

The FAA wildlife-strike data are obtained from an external public data source and are not covered by this repository's MIT License.
