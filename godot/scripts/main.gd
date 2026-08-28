extends Control

@onready var aircraft_controller: Control = $Aircraft
@onready var wildlife_controller: Control = $WildlifeGroup
@onready var environment: Control = $Environment
@onready var outcome_controller: Control = $OutcomePanel

@onready var ground: ColorRect = $Environment/Ground
@onready var impact_effect: Polygon2D = $ImpactEffect
@onready var trial_info: Label = $TrialInfoPanel/TrialInfo
@onready var weather_label: Label = $WeatherPanel/WeatherLabel
@onready var play_button: Button = $PlayButton
@onready var exit_button: Button = $ExitButton

@onready var engine_audio: AudioStreamPlayer = $EngineAudio
@onready var rain_audio: AudioStreamPlayer = $RainAudio
@onready var impact_audio: AudioStreamPlayer = $ImpactAudio
@onready var snow_audio: AudioStreamPlayer = $SnowAudio
@onready var button_audio: AudioStreamPlayer = $ButtonAudio

const ENGINE_NORMAL_DB := -5.0
const ENGINE_DUCKED_DB := -14.0

const RAIN_NORMAL_DB := -3.0
const RAIN_DUCKED_DB := -18.0

const SNOW_NORMAL_DB := 0.0
const SNOW_DUCKED_DB := -12.0

const IMPACT_AUDIO_START := 0.5
const IMPACT_DUCK_TIME := 3.0
const IMPACT_AUDIO_CUTOFF := 12.0

const IMPACT_NORMAL_DB := -3.0
const IMPACT_FADED_DB := -20.0

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
	configure_impact_shape()

	if not load_trial():
		return

	DisplayServer.window_set_mode(
		DisplayServer.WINDOW_MODE_FULLSCREEN
	)

	update_trial_info()
	prepare_scene()
	configure_weather_audio(
		sampled_context
	)

	play_button.text = "Play Trial"
	play_button.visible = true
	play_button.disabled = false
	exit_button.visible = true
	exit_button.disabled = false

	if not play_button.pressed.is_connected(
		_on_play_button_pressed
	):
		play_button.pressed.connect(
			_on_play_button_pressed
		)
	
	if not exit_button.pressed.is_connected(
		_on_exit_button_pressed
	):
		exit_button.pressed.connect(
			_on_exit_button_pressed
		)

func _on_play_button_pressed() -> void:
	button_audio.stop()
	button_audio.play()

	play_button.visible = false
	play_button.disabled = true
	exit_button.visible = false
	exit_button.disabled = true

	stop_trial_audio()
	prepare_scene()

	engine_audio.play(
		225.0
	)

	await get_tree().create_timer(
		0.5
	).timeout

	await play_trial_animation()

	await get_tree().create_timer(
		3.5
	).timeout

	engine_audio.stop()

	await get_tree().create_timer(
		1.0
	).timeout

	play_button.text = "Replay Trial"
	play_button.visible = true
	play_button.disabled = false
	exit_button.visible = true
	exit_button.disabled = false

func _on_exit_button_pressed() -> void:
	button_audio.stop()
	button_audio.play()

	await get_tree().create_timer(
		0.08
	).timeout

	get_tree().quit()

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
	
	play_impact_audio()

	await get_tree().create_timer(
		0.35
	).timeout

	impact_effect.visible = false

func configure_impact_shape() -> void:
	impact_effect.polygon = PackedVector2Array([
		Vector2(0, -38),
		Vector2(9, -18),
		Vector2(28, -28),
		Vector2(18, -8),
		Vector2(38, 0),
		Vector2(18, 8),
		Vector2(28, 28),
		Vector2(9, 18),
		Vector2(0, 38),
		Vector2(-9, 18),
		Vector2(-28, 28),
		Vector2(-18, 8),
		Vector2(-38, 0),
		Vector2(-18, -8),
		Vector2(-28, -28),
		Vector2(-9, -18),
	])

func stop_trial_audio() -> void:
	engine_audio.stop()
	impact_audio.stop()

func duck_background_audio() -> void:
	engine_audio.volume_db = ENGINE_DUCKED_DB
	rain_audio.volume_db = RAIN_DUCKED_DB
	snow_audio.volume_db = SNOW_DUCKED_DB


func restore_background_audio() -> void:
	if engine_audio.playing:
		engine_audio.volume_db = ENGINE_NORMAL_DB

	if rain_audio.playing:
		rain_audio.volume_db = RAIN_NORMAL_DB

	if snow_audio.playing:
		snow_audio.volume_db = SNOW_NORMAL_DB

func configure_weather_audio(
	sampled_context: Dictionary
) -> void:
	rain_audio.stop()
	snow_audio.stop()

	var precipitation = str(
		sampled_context.get(
			"PRECIPITATION",
			"Not reported"
		)
	).to_lower()

	if "rain" in precipitation:
		rain_audio.play()

	if "snow" in precipitation:
		snow_audio.play()

func play_impact_audio() -> void:
	impact_audio.stop()

	impact_audio.volume_db = IMPACT_NORMAL_DB

	# Skip the leading section so the audible hit aligns
	# closely with the visual impact burst.
	impact_audio.play(
		IMPACT_AUDIO_START
	)

	duck_background_audio()

	# After the initial hit, bring engine/weather back
	# while fading the long impact reverb into the background.
	get_tree().create_timer(
		IMPACT_DUCK_TIME
	).timeout.connect(
		_restore_audio_after_impact
	)

	# Stop the otherwise ~60-second source after its useful
	# impact/reverb section.
	get_tree().create_timer(
		IMPACT_AUDIO_CUTOFF
	).timeout.connect(
		_stop_impact_audio
	)

func _restore_audio_after_impact() -> void:
	restore_background_audio()

	if impact_audio.playing:
		var tween := create_tween()

		tween.tween_property(
			impact_audio,
			"volume_db",
			IMPACT_FADED_DB,
			1.5
		)


func _stop_impact_audio() -> void:
	if impact_audio.playing:
		impact_audio.stop()

	impact_audio.volume_db = IMPACT_NORMAL_DB
