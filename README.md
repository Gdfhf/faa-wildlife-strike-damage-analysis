# FAA Wildlife Strike Damage Analysis

**Explainable Scenario-Based Simulation of Aircraft Damage Consequences Among Reported Wildlife Strikes Using FAA Data**

This repository contains the analytical and software-development components of a Master of Data Analytics capstone project investigating aircraft damage consequences among reported wildlife strikes.

The project uses data from the Federal Aviation Administration (FAA) National Wildlife Strike Database to examine relationships between aircraft, wildlife, flight, temporal, and geographic characteristics and reported aircraft damage.

The analysis is conditional on a wildlife strike having already occurred. The project does **not** estimate the probability that an ordinary flight will experience a wildlife strike.

## Project Objectives

The project aims to:

- analyze historical factors associated with aircraft damage among reported wildlife strikes;
- develop and evaluate machine-learning models that estimate conditional aircraft-damage probabilities;
- assess model generalizability across future reporting periods and airports excluded from model training;
- calibrate and interpret predictive models;
- use scenario-based Monte Carlo simulation to represent and compare probabilistic consequence outcomes;
- communicate analytical results through an interactive Streamlit interface;
- optionally develop a simplified Godot-based visualization layer where feasible.

Secondary analyses may examine damage severity and affected aircraft components where sufficient data are available.

## Data Source

The project uses the **FAA National Wildlife Strike Database**, accessed through the U.S. Department of Transportation open-data platform.

The working dataset contains approximately 348,000 reported wildlife-strike incidents and more than 100 variables related to:

- aircraft characteristics;
- wildlife characteristics;
- flight conditions;
- temporal information;
- geographic information;
- environmental conditions;
- reported damage and consequences.

The raw dataset is not stored in this repository. Instructions for obtaining the source data will be documented here as the project develops.

## Analytical Approach

The project follows an analytics lifecycle based on CRISP-DM and is expected to include:

1. Data understanding and quality assessment
2. Data cleaning and preprocessing
3. Exploratory and statistical analysis
4. Predictive modelling
5. Probability calibration and model explainability
6. Chronological and airport-held-out validation
7. Scenario-based Monte Carlo simulation
8. Interactive results communication

The primary predictive task is binary classification of whether aircraft damage was reported following a wildlife strike.

Logistic regression will serve as an interpretable baseline, with candidate machine-learning approaches expected to include Random Forest and gradient-boosting methods.

## Repository Structure

```text
faa-wildlife-strike-damage-analysis/
│
├── data/
│   ├── raw/              # Original datasets (not tracked by Git)
│   └── processed/        # Cleaned or transformed datasets (not tracked by Git)
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_statistics.ipynb
│   ├── 04_modeling.ipynb
│   └── 05_validation_simulation.ipynb
│
├── src/                  # Reusable Python modules
│
├── docs/                 # Technical project documentation
│
├── simulation/           # Monte Carlo simulation components
│
├── dashboard/            # Streamlit application
│
└── godot/                # Optional Godot visualization project
```
The repository structure may evolve as the project progresses.

## Current Project Status
The project is currently in the data understanding and preparation stage.

Initial work focuses on:

- validating dataset dimensions and temporal coverage;
- reviewing the available variables and their definitions;
- assessing missingness and data quality;
- identifying duplicate or inconsistent records;
- defining primary and secondary analytical targets;
- identifying potential target leakage;
- developing a data dictionary and feature-eligibility framework.
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

Model outputs are conditional, probabilistic estimates and should not be interpreted as predictions that a specific flight will experience a wildlife strike or as physical simulations of aircraft-wildlife impacts.

The project is not intended to replace FAA guidance, aircraft inspections, wildlife-management practices, or professional aviation safety and operational decision-making.

## License

The code developed in this repository is available under the MIT License.

The FAA wildlife-strike data are obtained from an external public data source and are not covered by this repository's MIT License.