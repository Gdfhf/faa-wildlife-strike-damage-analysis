extends Control

@onready var aircraft_controller: Control = $Aircraft
@onready var wildlife_controller: Control = $WildlifeGroup
@onready var environment: Control = $Environment
@onready var outcome_controller: Control = $OutcomePanel

@onready var ground: ColorRect = $Environment/Ground
@onready var impact_effect: ColorRect = $ImpactEffect
@onready var trial_info: Label = $TrialInfoPanel/TrialInfo
@onready var weather_label: Label = $WeatherPanel/WeatherLabel

var visual_trial: Dictionary = {}
var sampled_context: Dictionary = {}

const AIRCRAFT_CLASS_LABELS := {
	"A": "Airplane",
	"B": "Helicopter",
	"C": "Glider",
	"D": "Balloon",
	"F": "Dirigible",
	"I": "Gyroplane",
	"J": "Ultralight",
	"Y": "Other",
	"Z": "Unknown",
}

func get_aircraft_class_label(
	ac_class: String
) -> String:
	return AIRCRAFT_CLASS_LABELS.get(
		ac_class,
		"Unknown"
	)

func _ready() -> void:
	impact_effect.visible = false

	if not load_trial():
		return

	update_trial_info()
	prepare_scene()

	await play_trial_animation()


func load_trial() -> bool:
	var parsed: Dictionary = TrialLoader.load_trial()

	if parsed.is_empty():
		trial_info.text = "Could not load trial JSON."
		return false

	visual_trial = parsed.get(
		"visual_trial",
		{}
	)

	sampled_context = visual_trial.get(
		"sampled_context",
		{}
	)

	return true


func update_trial_info() -> void:
	var airport = sampled_context.get(
		"AIRPORT_ID",
		"Unknown"
	)

	var ac_class = str(
		sampled_context.get(
			"AC_CLASS",
			"Z"
		)
	)

	var aircraft_label = get_aircraft_class_label(
		ac_class
	)

	var phase = sampled_context.get(
		"PHASE_OF_FLIGHT",
		"Unknown"
	)

	var wildlife_type = sampled_context.get(
		"WILDLIFE_TYPE",
		"Unknown"
	)

	var wildlife_size = sampled_context.get(
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
		+ "Aircraft: %s - %s\n"
		+ "Phase: %s\n"
		+ "Wildlife: %s\n"
		+ "Size: %s\n"
		+ "Number struck: %s\n"
		+ "Time of day: %s\n"
		+ "Damage probability: %.2f%%"
	) % [
		airport,
		ac_class,
		aircraft_label,
		phase,
		wildlife_type,
		wildlife_size,
		num_struck,
		time_of_day,
		damage_probability * 100.0,
	]


func prepare_scene() -> void:
	outcome_controller.show_pending()

	impact_effect.visible = false

	aircraft_controller.configure_aircraft(
		sampled_context
	)

	environment.configure_environment(
		sampled_context
	)

	environment.configure_phase_of_flight(
		sampled_context,
		aircraft_controller
	)

	update_weather_label()

	impact_effect.position = (
		aircraft_controller.get_impact_position()
	)

	wildlife_controller.configure_wildlife(
		sampled_context,
		aircraft_controller,
		ground.position.y
	)


func update_weather_label() -> void:
	var time_of_day = str(
		sampled_context.get(
			"TIME_OF_DAY",
			"Unknown"
		)
	)

	var sky = str(
		sampled_context.get(
			"SKY",
			"Unknown"
		)
	)

	var precipitation = str(
		sampled_context.get(
			"PRECIPITATION",
			"Unknown"
		)
	)

	weather_label.text = (
		"%s • %s • %s"
		% [
			time_of_day,
			sky,
			precipitation,
		]
	)


func play_trial_animation() -> void:
	outcome_controller.show_in_progress()

	await get_tree().create_timer(
		0.75
	).timeout

	var target_position = (
		impact_effect.position
		+ Vector2(5, 5)
	)

	await wildlife_controller.animate_to(
		target_position
	)

	await show_impact()

	aircraft_controller.show_damage_state(
		visual_trial
	)

	outcome_controller.show_outcome(
		visual_trial
	)


func show_impact() -> void:
	wildlife_controller.hide_wildlife()

	impact_effect.visible = true
	outcome_controller.show_impact()

	await get_tree().create_timer(
		0.35
	).timeout

	impact_effect.visible = false
