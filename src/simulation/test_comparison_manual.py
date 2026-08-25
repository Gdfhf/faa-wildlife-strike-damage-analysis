from src.simulation.scenario import Scenario
from src.simulation.comparison import ScenarioComparator


def main():
    scenario_a = Scenario(
        airport_id="KSMF",
        ac_class="A",
        ac_mass_group="Heavy",
        season="Summer",
        phase_of_flight="Take-off Run",
    )

    scenario_b = Scenario(
        airport_id="KSMF",
        ac_class="A",
        ac_mass_group="Heavy",
        season="Winter",
        phase_of_flight="Take-off Run",
    )

    comparator = ScenarioComparator()

    result = comparator.compare(
        scenario_a=scenario_a,
        scenario_b=scenario_b,
        n_trials=1_000,
        seed=42,
    )

    print("\nDamage probability")
    print(result.damage_probability)

    print("\nSeverity probability")
    print(result.severity_probability)

    print("\nComponent probabilities")

    for component, difference in (
        result.component_probabilities.items()
    ):
        print(component)
        print(difference)


if __name__ == "__main__":
    main()