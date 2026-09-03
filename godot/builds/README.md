# Godot Visualizer Builds

This directory is reserved for local standalone Godot exports.

## Windows standalone build

The compiled Windows visualizer is distributed through the project's GitHub Releases and is **not stored in normal Git history**.

Download the Windows x86_64 executable:

https://github.com/Gdfhf/faa-wildlife-strike-damage-analysis/releases/download/v1.0.0/CapstoneAirstrikeVisualizer.exe

Release page:

https://github.com/Gdfhf/faa-wildlife-strike-damage-analysis/releases/tag/v1.0.0

Place the downloaded executable at:

```text
godot/builds/CapstoneAirstrikeVisualizer.exe
```

When the executable is present, Page 04 of the Streamlit dashboard automatically uses the local standalone visualizer. The selected already-realized Monte Carlo trial is written to:

```text
godot/data/latest_trial.json
```

and the Windows application reads that payload at launch.

## Web visualizer

The browser build is maintained separately from this local-build directory.

The tracked Web export is located at:

```text
simulation/web_visualizer/
```

and is deployed through GitHub Pages using the repository's GitHub Actions workflow.

Hosted visualizer:

https://gdfhf.github.io/faa-wildlife-strike-damage-analysis/

When the local Windows executable is not available, Page 04 automatically builds a browser-safe URL containing the selected retained trial and opens the hosted Web visualizer instead.

The Godot Web application decodes that supplied payload and visualizes the same already-realized Python trial. It does not rerun the predictive models, resample the Monte Carlo outcome, or perform collision-physics simulation.

## Runtime behavior

```text
Local Windows environment
    -> CapstoneAirstrikeVisualizer.exe exists
    -> write godot/data/latest_trial.json
    -> launch standalone Godot application

Hosted / no local executable
    -> encode retained trial into URL
    -> open GitHub Pages visualizer
    -> Godot Web decodes and displays the supplied trial
```

The analytical dashboard remains functional regardless of whether the Windows executable is installed.
