extends Control

@onready var placeholder: ColorRect = $Placeholder
@onready var damage_marker: Panel = (
	$DamageEffects/DamageMarker
)
@onready var visual: TextureRect = $Visual

var aircraft_visual_type: String = "generic"

var aircraft_mass_group: String = "Unknown"

var damage_marker_tween: Tween

const AIRPLANE_LIGHT = preload(
	"res://assets/aircraft/airplane/light.png"
)

const AIRPLANE_MEDIUM = preload(
	"res://assets/aircraft/airplane/medium.png"
)

const AIRPLANE_HEAVY = preload(
	"res://assets/aircraft/airplane/heavy.png"
)

const BALLOON = preload(
	"res://assets/aircraft/balloon/balloon.png"
)

const DIRIGIBLE = preload(
	"res://assets/aircraft/dirigible/blimp.png"
)

const GENERIC = preload(
	"res://assets/aircraft/generic/generic.png"
)

const GLIDER = preload(
	"res://assets/aircraft/glider/glider.png"
)

const HELICOPTER = preload(
	"res://assets/aircraft/helicopter/helicopter.png"
)

const GYROPLANE = preload(
	# No free asset was available for gyroplane
	"res://assets/aircraft/helicopter/helicopter.png"
)

const ULTRALIGHT = preload(
	"res://assets/aircraft/ultralight/ultralight.png"
)

func apply_aircraft_visual(
	mass_group: String,
	aircraft_width = 480,
	aircraft_height = 200
) -> void:

	var flip_horizontal := true

	match aircraft_visual_type:
		"airplane":
			match mass_group:
				"Light":
					visual.texture = AIRPLANE_LIGHT
					flip_horizontal = true

				"Medium":
					visual.texture = AIRPLANE_MEDIUM
					flip_horizontal = true

				"Heavy":
					visual.texture = AIRPLANE_HEAVY
					flip_horizontal = true

				"Unknown":
					visual.texture = AIRPLANE_MEDIUM
					flip_horizontal = true

				_:
					visual.texture = AIRPLANE_MEDIUM
					flip_horizontal = true

		"helicopter":
			visual.texture = HELICOPTER
			flip_horizontal = true

		"glider":
			visual.texture = GLIDER
			flip_horizontal = false

		"balloon":
			visual.texture = BALLOON
			flip_horizontal = false

		"dirigible":
			visual.texture = DIRIGIBLE
			flip_horizontal = false

		"gyroplane":
			visual.texture = GYROPLANE
			flip_horizontal = true

		"ultralight":
			visual.texture = ULTRALIGHT
			flip_horizontal = true

		"other", "unknown":
			visual.texture = GENERIC
			flip_horizontal = true

	var aircraft_size := Vector2(
		aircraft_width,
		aircraft_height
	)

	# Keep the Aircraft container and texture box aligned.
	size = aircraft_size
	visual.size = aircraft_size
	visual.position = Vector2.ZERO

	# Flip around the CENTER of the visual instead of the top-left.
	visual.pivot_offset = (
		visual.size / 2.0
	)

	# Always reset the complete scale first.
	visual.scale = Vector2(
		1.0,
		1.0
	)

	if flip_horizontal:
		visual.scale.x = -1.0

func configure_aircraft(
	sampled_context: Dictionary
) -> void:
	var ac_class = str(
		sampled_context.get(
			"AC_CLASS",
			"Z"
		)
	)

	var mass_group = str(
		sampled_context.get(
			"AC_MASS_GROUP",
			"Unknown"
		)
	)

	aircraft_mass_group = mass_group

	aircraft_visual_type = get_aircraft_visual_type(
		ac_class
	)

	apply_aircraft_visual(
		mass_group
	)

	damage_marker.visible = false

func show_damage_state(
	visual_trial: Dictionary
) -> void:
	var damaged = bool(
		visual_trial.get(
			"damaged",
			false
		)
	)

	if not damaged:
		stop_damage_marker_effect()
		return

	damage_marker.visible = true
	damage_marker.position = Vector2(
		size.x * 0.5 - damage_marker.size.x * 0.5,
		size.y * 0.5 - damage_marker.size.y * 0.5
	)
	start_damage_marker_effect()

func stop_damage_marker_effect() -> void:
	if damage_marker_tween:
		damage_marker_tween.kill()
		damage_marker_tween = null

	damage_marker.visible = false
	damage_marker.scale = Vector2.ONE
	damage_marker.modulate.a = 1.0

func start_damage_marker_effect() -> void:
	if damage_marker_tween:
		damage_marker_tween.kill()

	damage_marker.scale = Vector2.ONE
	damage_marker.modulate.a = 1.0

	damage_marker.pivot_offset = (
		damage_marker.size / 2.0
	)

	damage_marker_tween = create_tween()

	damage_marker_tween.set_loops()

	damage_marker_tween.tween_property(
		damage_marker,
		"scale",
		Vector2(1.35, 1.35),
		0.6
	)

	damage_marker_tween.parallel().tween_property(
		damage_marker,
		"modulate:a",
		0.45,
		0.6
	)

	damage_marker_tween.tween_property(
		damage_marker,
		"scale",
		Vector2.ONE,
		0.6
	)

	damage_marker_tween.parallel().tween_property(
		damage_marker,
		"modulate:a",
		1.0,
		0.6
	)

func get_aircraft_visual_type(
	ac_class: String
) -> String:
	match ac_class:
		"A":
			return "airplane"

		"B":
			return "helicopter"

		"C":
			return "glider"

		"D":
			return "balloon"

		"F":
			return "dirigible"

		"I":
			return "gyroplane"

		"J":
			return "ultralight"

		"Y":
			return "other"

		"Z":
			return "unknown"

		_:
			return "unknown"


func apply_placeholder_presentation() -> void:
	# Placeholder-only presentation.
	# When real assets are added later, this function can be replaced
	# by sprite/texture selection without changing Main.

	match aircraft_visual_type:
		"airplane":
			size = Vector2(
				180,
				50
			)

			placeholder.size = size

		"helicopter":
			size = Vector2(
				120,
				70
			)

			placeholder.size = size

		_:
			size = Vector2(
				140,
				55
			)

			placeholder.size = size

func get_ground_contact_offset() -> float:
	match aircraft_visual_type:
		"airplane":
			match aircraft_mass_group:
				"Light":
					return 25.0

				"Medium":
					return 25.0

				"Heavy":
					return 35.0

				_:
					return 25.0

		"helicopter":
			return 25.0
			
		"gyroplane":
			return 25.0

		"glider":
			return 60.0

		"balloon":
			return 8.0
		
		"dirigible":
			return 35.0

		"ultralight":
			return 25.0

		_:
			return 0.0

func get_impact_position() -> Vector2:
	return (
		position
		+ Vector2(
			size.x * 0.5,
			size.y * 0.5
		)
	)
