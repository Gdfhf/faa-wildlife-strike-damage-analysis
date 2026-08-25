from src.simulation.scenario import Scenario
from src.simulation.engine import SimulationEngine


def main():
    scenario = Scenario(
        airport_id="KSMF",
        ac_class="A",
        ac_mass_group="Heavy",
        season="Summer",
        phase_of_flight="Take-off Run",
    )

    engine = SimulationEngine()

    result = engine.run(
        scenario=scenario,
        n_trials=10_000,
        seed=42,
    )

    print("\nSimulation result")
    print("=" * 60)

    print("Trials:", result.n_trials)
    print("Support:", result.support_count)

    print(
        "Mean damage probability:",
        result.mean_damage_probability,
    )

    print(
        "Simulated damage count:",
        result.simulated_damage_count,
    )

    print(
        "Simulated damage rate:",
        result.simulated_damage_rate,
    )

    print(
        "\nSeverity mean probability "
        "given damage:",
        result.severity_probability_mean_damaged,
    )

    print(
        "Simulated severe count:",
        result.simulated_severe_count,
    )

    print(
        "Simulated severe rate "
        "given damage:",
        result.simulated_severe_rate_given_damage,
    )

    print("\nComponents:")

    for component in (
        result.component_counts
    ):
        print(
            component,
            "| mean probability:",
            result.component_probability_means_damaged[
                component
            ],
            "| count:",
            result.component_counts[
                component
            ],
            "| rate given damage:",
            result.component_rates_given_damage[
                component
            ],
        )


if __name__ == "__main__":
    main()