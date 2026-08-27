extends ColorRect

@onready var outcome_label: Label = $OutcomeLabel


func show_pending() -> void:
	outcome_label.text = "Preparing simulated trial..."


func show_in_progress() -> void:
	outcome_label.text = "Trial in progress..."


func show_impact() -> void:
	outcome_label.text = "Wildlife strike realized..."


func show_outcome(
	visual_trial: Dictionary
) -> void:
	var damaged = bool(
		visual_trial.get(
			"damaged",
			false
		)
	)

	if not damaged:
		outcome_label.text = (
			"NO REPORTED DAMAGE\n\n"
			+ "This random Monte Carlo trial "
			+ "did not realize aircraft damage."
		)

		return

	var result_text = (
		"DAMAGE REALIZED\n\n"
	)

	var severe_value = visual_trial.get(
		"severe",
		null
	)

	if severe_value != null:
		var severity_probability = float(
			visual_trial.get(
				"severity_probability",
				0.0
			)
		)

		var severity_label = (
			"Severe"
			if bool(severe_value)
			else "Non-severe"
		)

		result_text += (
			"Severity: %s\n"
			+ "Severity probability: %.2f%%\n"
		) % [
			severity_label,
			severity_probability * 100.0,
		]

	var component_outcomes: Dictionary = (
		visual_trial.get(
			"component_outcomes",
			{}
		)
	)

	var damaged_components: Array[String] = []

	for component in component_outcomes:
		if bool(
			component_outcomes[
				component
			]
		):
			damaged_components.append(
				format_component_name(
					str(component)
				)
			)

	if damaged_components.size() > 0:
		result_text += "\nComponents:\n"

		for component in damaged_components:
			result_text += (
				"- %s\n"
				% component
			)

	else:
		result_text += (
			"\nNo retained component model "
			+ "realized damage in this trial."
		)

	outcome_label.text = result_text


func format_component_name(
	component: String
) -> String:
	return (
		component
		.replace(
			"_damage",
			""
		)
		.replace(
			"_",
			" "
		)
		.capitalize()
	)
