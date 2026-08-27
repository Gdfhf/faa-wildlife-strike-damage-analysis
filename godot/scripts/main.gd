extends Control

@onready var aircraft: ColorRect = $Aircraft
@onready var wildlife: ColorRect = $Wildlife
@onready var impact_effect: ColorRect = $ImpactEffect
@onready var trial_info: Label = $TrialInfo
@onready var outcome_label: Label = $OutcomePanel/OutcomeLabel

const TRIAL_PATH := "res://data/latest_trial.json"

var visual_trial: Dictionary = {}
var sampled_context: Dictionary = {}


func _ready() -> void:
	impact_effect.visible = false

	if load_trial():
		prepare_scene()
		await play_trial_animation()


func load_trial() -> bool:
	if not FileAccess.file_exists(TRIAL_PATH):
		trial_info.text = "Trial JSON not found."
		return false

	var file := FileAccess.open(
		TRIAL_PATH,
		FileAccess.READ
	)

	if file == null:
		trial_info.text = "Could not open trial JSON."
		return false

	var json_text := file.get_as_text()
	var parsed = JSON.parse_string(json_text)

	if parsed == null:
		trial_info.text = "Could not parse trial JSON."
		return false

	visual_trial = parsed.get(
		"visual_trial",
		{}
	)

	sampled_context = visual_trial.get(
		"sampled_context",
		{}
	)

	update_trial_info()

	return true


func update_trial_info() -> void:
	var airport = sampled_context.get(
		"AIRPORT_ID",
        "Unknown"
	)

	var phase = sampled_context.get(
		"PHASE_OF_FLIGHT",
        "Unknown"
	)

	var wildlife_type = sampled_context.get(
		"WILDLIFE_TYPE",
        "Unknown"
	)

	var size = sampled_context.get(
		"SIZE",
        "Unknown"
	)

	var num_struck = sampled_context.get(
		"NUM_STRUCK",
        "Unknown"
	)

	var time_of_day = sampled_context.get(
		"TIME_OF_DAY",
        "Unknown"
	)

	var damage_probability = float(
		visual_trial.get(
			"damage_probability",
			0.0
		)
	)

	trial_info.text = (
        "Airport: %s\n"
		+ "Phase: %s\n"
		+ "Wildlife: %s\n"
		+ "Size: %s\n"
		+ "Number struck: %s\n"
		+ "Time of day: %s\n"
		+ "Damage probability: %.2f%%"
	) % [
		airport,
		phase,
		wildlife_type,
		size,
		num_struck,
		time_of_day,
		damage_probability * 100.0,
	]


func prepare_scene() -> void:
	outcome_label.text = "Preparing simulated trial..."

	impact_effect.visible = false

	# Put the impact square roughly at the aircraft's
	# front/upper section for now.
	impact_effect.position = (
		aircraft.position
		+ Vector2(
			aircraft.size.x * 0.75,
			aircraft.size.y * 0.15
		)
	)

	# Start wildlife above/right of the aircraft.
	wildlife.position = (
		aircraft.position
		+ Vector2(
			320,
			-180
		)
	)


func play_trial_animation() -> void:
	outcome_label.text = "Trial in progress..."

	# Short delay before movement begins.
	await get_tree().create_timer(0.75).timeout

	var target_position = (
		impact_effect.position
		+ Vector2(5, 5)
	)

	var tween := create_tween()

	tween.set_trans(
		Tween.TRANS_QUAD
	)

	tween.set_ease(
		Tween.EASE_IN
	)

	tween.tween_property(
		wildlife,
		"position",
		target_position,
		1.5
	)

	await tween.finished

	await show_impact()

	show_outcome()


func show_impact() -> void:
	wildlife.visible = false
	impact_effect.visible = true

	outcome_label.text = "Wildlife strike realized..."

	await get_tree().create_timer(0.35).timeout

	impact_effect.visible = false


func show_outcome() -> void:
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
		if bool(component_outcomes[component]):
			damaged_components.append(
				format_component_name(component)
			)

	if damaged_components.size() > 0:
		result_text += "\nComponents:\n"

		for component in damaged_components:
			result_text += "- %s\n" % component

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
		.replace("_damage", "")
		.replace("_", " ")
		.capitalize()
	)
