extends Control

@onready var background: ColorRect = $Background
@onready var aircraft: ColorRect = $Aircraft
@onready var wildlife: ColorRect = $Wildlife
@onready var impact_effect: ColorRect = $ImpactEffect
@onready var trial_info: Label = $TrialInfo
@onready var outcome_label: Label = $OutcomePanel/OutcomeLabel
@onready var ground: ColorRect = $Ground
@onready var weather_label: Label = $WeatherLabel
@onready var clouds_layer: Control = $WeatherEffects/CloudsLayer
@onready var precipitation_layer: Control = $WeatherEffects/PrecipitationLayer
@onready var fog_overlay: ColorRect = $WeatherEffects/FogOverlay

const TRIAL_PATH := "res://data/latest_trial.json"

var visual_trial: Dictionary = {}
var sampled_context: Dictionary = {}

var wildlife_nodes: Array[ColorRect] = []


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

	@warning_ignore("shadowed_variable_base_class")
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

	configure_environment()
	configure_phase_of_flight()
	
	impact_effect.position = (
		aircraft.position
		+ Vector2(
			aircraft.size.x * 0.75,
			aircraft.size.y * 0.15
		)
	)

	configure_wildlife()

func configure_phase_of_flight() -> void:
	var phase = str(
		sampled_context.get(
			"PHASE_OF_FLIGHT",
            "Unknown"
		)
	)

	# Default presentation.
	ground.visible = false

	match phase:

		"Take-off Run":
			ground.visible = true

			aircraft.position = Vector2(
				120,
				ground.position.y - aircraft.size.y
			)

		"Landing Roll":
			ground.visible = true

			aircraft.position = Vector2(
				320,
				ground.position.y - aircraft.size.y
			)

		"Taxi":
			ground.visible = true

			aircraft.position = Vector2(
				180,
				ground.position.y - aircraft.size.y
			)

		"Climb":
			ground.visible = true

			aircraft.position = Vector2(
				220,
				ground.position.y - 180
			)

		"Approach":
			ground.visible = true

			aircraft.position = Vector2(
				520,
				ground.position.y - 220
			)

		"Descent":
			ground.visible = false

			aircraft.position = Vector2(
				500,
				270
			)

		"En Route":
			ground.visible = false

			aircraft.position = Vector2(
				350,
				260
			)

		_:
			ground.visible = false

			aircraft.position = Vector2(
				300,
				300
			)

func configure_time_of_day(
	time_of_day: String
) -> void:

	match time_of_day.to_lower():

		"day":
			background.color = Color(
				0.49,
				0.78,
				0.90
			)

		"dawn":
			background.color = Color(
				0.92,
				0.62,
				0.48
			)

		"dusk":
			background.color = Color(
				0.45,
				0.36,
				0.62
			)

		"night":
			background.color = Color(
				0.05,
				0.09,
				0.18
			)

		_:
			background.color = Color(
				0.49,
				0.78,
				0.90
			)

func clear_weather_effects() -> void:
	for child in clouds_layer.get_children():
		child.queue_free()

	for child in precipitation_layer.get_children():
		child.queue_free()

	fog_overlay.visible = false

func create_cloud(
	position: Vector2,
	scale_factor: float = 1.0
) -> void:

	var cloud := Control.new()

	cloud.position = position

	clouds_layer.add_child(
		cloud
	)

	var pieces = [
		{
			"position": Vector2(0, 18),
			"size": Vector2(90, 32)
		},
		{
			"position": Vector2(20, 0),
			"size": Vector2(50, 45)
		},
		{
			"position": Vector2(50, 8),
			"size": Vector2(55, 38)
		}
	]

	for piece_data in pieces:
		var piece := ColorRect.new()

		piece.position = (
			piece_data["position"]
			* scale_factor
		)

		piece.size = (
			piece_data["size"]
			* scale_factor
		)

		piece.color = Color(
			0.88,
			0.90,
			0.92,
			0.90
		)

		cloud.add_child(
			piece
		)

func configure_clouds(
	sky: String
) -> void:

	match sky.to_lower():

		"clear":
			pass

		"some cloud", "some clouds":

			create_cloud(
				Vector2(400, 70),
				0.8
			)

			create_cloud(
				Vector2(750, 120),
				1.0
			)

			create_cloud(
				Vector2(950, 55),
				0.7
			)

		"overcast":

			create_cloud(
				Vector2(280, 30),
				1.1
			)

			create_cloud(
				Vector2(440, 65),
				1.2
			)

			create_cloud(
				Vector2(600, 20),
				1.0
			)

			create_cloud(
				Vector2(730, 75),
				1.3
			)

			create_cloud(
				Vector2(900, 35),
				1.1
			)

			create_cloud(
				Vector2(1030, 90),
				0.9
			)

		"not reported", "unknown":
			pass

func create_rain() -> void:
	var rng := RandomNumberGenerator.new()

	rng.seed = 12345

	for i in range(45):
		var drop := ColorRect.new()

		drop.size = Vector2(
			2,
			16
		)

		drop.position = Vector2(
			rng.randf_range(
				250,
				size.x
			),
			rng.randf_range(
				0,
				size.y
			)
		)

		drop.rotation = deg_to_rad(
			12
		)

		drop.color = Color(
			0.65,
			0.80,
			0.95,
			0.75
		)

		precipitation_layer.add_child(
			drop
		)

func animate_rain() -> void:
	while true:
		await get_tree().process_frame

		for drop in precipitation_layer.get_children():
			drop.position += Vector2(
				-1.5,
				8.0
			)

			if drop.position.y > size.y:
				drop.position.y = -20

func create_snow() -> void:
	var rng := RandomNumberGenerator.new()

	rng.seed = 54321

	for i in range(35):
		var flake := ColorRect.new()

		var flake_size = rng.randf_range(
			3,
			7
		)

		flake.size = Vector2(
			flake_size,
			flake_size
		)

		flake.position = Vector2(
			rng.randf_range(
				250,
				size.x
			),
			rng.randf_range(
				0,
				size.y
			)
		)

		flake.color = Color(
			1.0,
			1.0,
			1.0,
			0.9
		)

		precipitation_layer.add_child(
			flake
		)

func animate_snow() -> void:
	while true:
		await get_tree().process_frame

		for flake in precipitation_layer.get_children():
			flake.position += Vector2(
				sin(
					Time.get_ticks_msec()
					/ 400.0
					+ flake.position.y
				) * 0.4,
				2.0
			)

			if flake.position.y > size.y:
				flake.position.y = -10


func create_fog() -> void:
	fog_overlay.visible = true

	fog_overlay.color = Color(
		0.90,
		0.92,
		0.93,
		0.55
	)

func configure_precipitation(
	precipitation: String
) -> void:

	match precipitation.to_lower():

		"rain":
			create_rain()
			animate_rain()

		"snow":
			create_snow()
			animate_snow()

		"fog":
			create_fog()

		"none", "not reported", "unknown":
			pass
				
func configure_environment() -> void:
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

	clear_weather_effects()

	configure_time_of_day(
		time_of_day
	)

	configure_clouds(
		sky
	)

	configure_precipitation(
		precipitation
	)

	weather_label.text = (
		"%s • %s • %s"
		% [
			time_of_day,
			sky,
			precipitation,
		]
	)

func get_wildlife_start_offset() -> Vector2:
	var phase = str(
		sampled_context.get(
			"PHASE_OF_FLIGHT",
            "Unknown"
		)
	)

	match phase:

		"Take-off Run", "Landing Roll", "Taxi":
			return Vector2(
				320,
				-140
			)

		"Climb":
			return Vector2(
				300,
				-220
			)

		"Approach":
			return Vector2(
				320,
				-180
			)

		"Descent":
			return Vector2(
				320,
				-160
			)

		"En Route":
			return Vector2(
				340,
				-80
			)

		_:
			return Vector2(
				320,
				-150
			)

func configure_wildlife() -> void:
	wildlife_nodes.clear()

	var size_category = str(
		sampled_context.get(
			"SIZE",
            "Unknown"
		)
	)

	var num_struck = str(
		sampled_context.get(
			"NUM_STRUCK",
            "Unknown"
		)
	)

	var bird_size = get_wildlife_size(
		size_category
	)

	var bird_count = get_wildlife_count(
		num_struck
	)

	wildlife.size = bird_size

	wildlife.position = (
		aircraft.position
		+ get_wildlife_start_offset()
	)

	wildlife.visible = true

	wildlife_nodes.append(
		wildlife
	)

	for i in range(1, bird_count):
		var bird = wildlife.duplicate() as ColorRect

		add_child(bird)

		bird.size = bird_size

		bird.position = (
			wildlife.position
			+ get_flock_offset(i)
		)

		wildlife_nodes.append(
			bird
		)


func get_wildlife_size(
	size_category: String
) -> Vector2:

	match size_category.to_lower():
		"small":
			return Vector2(
				18,
				18
			)

		"medium":
			return Vector2(
				30,
				30
			)

		"large":
			return Vector2(
				45,
				45
			)

		_:
			return Vector2(
				25,
				25
			)


func get_wildlife_count(
	num_struck: String
) -> int:

	match num_struck:
		"1":
			return 1

		"2-10", "2–10":
			return 3

		"11-100", "11–100":
			return 6

		"More than 100":
			return 10

		"Not reported":
			return 1

		_:
			return 1


func get_flock_offset(
	index: int
) -> Vector2:

	var offsets = [
		Vector2(35, -20),
		Vector2(50, 15),
		Vector2(75, -35),
		Vector2(90, 5),
		Vector2(110, -15),
		Vector2(125, 25),
		Vector2(145, -30),
		Vector2(160, 10),
		Vector2(180, -5),
	]

	var offset_index = (
		index - 1
	) % offsets.size()

	return offsets[
		offset_index
	]


func play_trial_animation() -> void:
	outcome_label.text = "Trial in progress..."

	await get_tree().create_timer(
		0.75
	).timeout

	var target_position = (
		impact_effect.position
		+ Vector2(5, 5)
	)

	var tween := create_tween()

	tween.set_parallel(true)

	for i in range(
		wildlife_nodes.size()
	):
		var bird = wildlife_nodes[i]

		var target_offset = Vector2(
			i * 8,
			i * 3
		)

		tween.tween_property(
			bird,
			"position",
			target_position + target_offset,
			1.5
		)

	await tween.finished

	await show_impact()

	show_outcome()


func show_impact() -> void:
	for bird in wildlife_nodes:
		bird.visible = false

	impact_effect.visible = true

	outcome_label.text = "Wildlife strike realized..."

	await get_tree().create_timer(
		0.35
	).timeout

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
