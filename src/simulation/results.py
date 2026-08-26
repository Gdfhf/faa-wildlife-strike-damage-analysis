from dataclasses import asdict

from src.simulation.engine import SimulationResult


def result_to_dict(result: SimulationResult) -> dict:
    """
    Convert a SimulationResult into a plain serializable dictionary.
    """
    return asdict(result)


def result_summary(result: SimulationResult) -> dict:
    """
    Produce dashboard-oriented summary values.
    """
    return {
        "simulation": {
            "trials": result.n_trials,
            "seed": result.seed,
        },

        "support": {
            "historical_records": result.support_count,
            "geography_level": result.geography_level,
        },

        "damage": {
            "mean_probability":
                result.mean_damage_probability,

            "simulated_count":
                result.simulated_damage_count,

            "simulated_rate":
                result.simulated_damage_rate,
        },

        "conditional_outcome": {
            "mean_probability":
                result.severity_probability_mean_damaged,

            "simulated_count":
                result.simulated_severe_count,

            "simulated_rate_given_damage":
                result.simulated_severe_rate_given_damage,
        },

        "components": {
            component: {
                "mean_probability_given_damage":
                    result.component_probability_means_damaged[
                        component
                    ],

                "simulated_count":
                    result.component_counts[
                        component
                    ],

                "simulated_rate_given_damage":
                    result.component_rates_given_damage[
                        component
                    ],
            }
            for component in result.component_counts
        },
    }