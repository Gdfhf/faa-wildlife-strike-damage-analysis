# Contributing Guidelines

This repository is used collaboratively by the capstone project team. To keep the workflow simple and avoid merge conflicts, especially when working with Jupyter notebooks, please follow the guidelines below.

## Current Git Workflow

For the current stage of the project, all work will be completed directly on the `main` branch.

This workflow may change later when the project moves into software-development components such as the Streamlit dashboard, simulation system, or Godot visualization. Branching and pull-request practices for those components will be decided by the team when needed.

## Before Starting Work

Before making changes:

1. Open GitHub Desktop.
2. Fetch and pull the latest changes from `main`.
3. Check with the team to confirm that no one else is currently working on the notebook or file you plan to edit.

Always pull the latest version before moving to a different notebook or starting new work.

## Jupyter Notebook Collaboration

To reduce merge conflicts:

- Only one team member should edit a specific Jupyter notebook at a time.
- Before starting work on a notebook, confirm that no other team member is currently editing it.
- Other team members may work at the same time as long as they are working on different notebooks or files.
- After completing a meaningful section of work, save, commit, and push the changes so the latest version is available to the rest of the team.

## Commits

Each commit must include a clear title that describes the work completed.

Examples of good commit messages:

- `Add initial dataset structure analysis`
- `Add missingness analysis`
- `Document damage target variables`
- `Update feature eligibility table`
- `Add duplicate record checks`

Avoid vague commit messages such as:

- `Update`
- `Changes`
- `Stuff`
- `Final`
- `Fix`

Commits should represent a meaningful and understandable change to the project. If there was more work done, it should be reflected in the commit description.

## Pulling and Pushing

A recommended workflow is:

1. Pull the latest changes.
2. Confirm the file you plan to edit is available.
3. Complete your assigned work.
4. Save your changes.
5. Commit with a descriptive message.
6. Push the commit to `main`.

If GitHub reports a conflict, do not overwrite or discard another team member's work without first discussing it with the team.

## Future Development

The current workflow is intended to remain simple during data understanding, data preparation, exploratory analysis, and early modelling.

As the project progresses into components such as:

- Streamlit dashboard development;
- Monte Carlo simulation development;
- reusable Python modules;
- Godot visualization;

the team may introduce feature branches and pull requests.

The workflow for these later stages will be decided collaboratively based on the needs of the project.