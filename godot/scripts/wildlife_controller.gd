extends Control

@onready var wildlife: Control = $Wildlife
@onready var visual: TextureRect = $Wildlife/Visual

var wildlife_nodes: Array[Control] = []
var movement_mode: String = "generic"

const LARGE_BIRD = preload(
	"res://assets/wildlife/bird/canadian_goose.png"
)

const MEDIUM_BIRD = preload(
	"res://assets/wildlife/generic/flying swallow.png"
)

const SMALL_BIRD = preload(
	"res://assets/wildlife/generic/flying swallow.png"
)

const GENERIC = preload(
	"res://assets/wildlife/generic/flying swallow.png"
)

const TERRESTRIAL_MAMMAL = preload(
	"res://assets/wildlife/terrestrial/high_res_deer.png"
)

const REPTILE = preload(
	"res://assets/wildlife/reptile/snake.png"
)

const BAT = preload(
	"res://assets/wildlife/bat/bat.png"
)


func configure_wildlife(
	sampled_context: Dictionary,
	aircraft: Control,
	ground_y: float
) -> void:
	clear_generated_wildlife()

	var wildlife_type = str(
		sampled_context.get(
			"WILDLIFE_TYPE",
			"Unknown"
		)
	)

	var ground_contact_offset = (
		get_ground_contact_offset(
			wildlife_type
		)
	)

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

	var phase = str(
		sampled_context.get(
			"PHASE_OF_FLIGHT",
			"Unknown"
		)
	)

	movement_mode = get_wildlife_movement_mode(
		wildlife_type
	)

	var wildlife_size = get_wildlife_size(
		size_category
	)

	var wildlife_count = get_wildlife_count(
		num_struck
	)

	wildlife.size = wildlife_size

	apply_wildlife_visual(
		wildlife_type,
		size_category,
		wildlife_size
	)

	wildlife.position = get_wildlife_start_position(
		aircraft,
		phase,
		ground_y,
		ground_contact_offset
	)

	wildlife.visible = true

	wildlife_nodes.append(
		wildlife
	)

	for i in range(
		1,
		wildlife_count
	):
		var animal = wildlife.duplicate() as Control

		add_child(
			animal
		)

		animal.size = wildlife_size

		animal.position = (
			wildlife.position
			+ get_group_offset(
				i,
				movement_mode
			)
		)

		wildlife_nodes.append(
			animal
		)


func apply_wildlife_visual(
	wildlife_type: String,
	size_category: String,
	wildlife_size: Vector2
) -> void:
	var flip_horizontal := false

	match wildlife_type.to_lower():
		"bird":
			match size_category.to_lower():
				"large":
					visual.texture = LARGE_BIRD

				"medium":
					visual.texture = MEDIUM_BIRD

				"small":
					visual.texture = SMALL_BIRD

				_:
					visual.texture = MEDIUM_BIRD

			# Bird assets face right; wildlife approaches from the right
			# and therefore needs to face left.
			flip_horizontal = true

		"bat":
			visual.texture = BAT

			# The bat asset already faces left.
			flip_horizontal = false

		"terrestrial mammal":
			visual.texture = TERRESTRIAL_MAMMAL
			flip_horizontal = true

		"reptile":
			visual.texture = REPTILE
			flip_horizontal = true

		_:
			visual.texture = GENERIC
			flip_horizontal = true

	visual.position = Vector2.ZERO
	visual.size = wildlife_size

	# Flip around the visual center so orientation changes do not
	# shift the wildlife away from its movement/impact coordinates.
	visual.pivot_offset = (
		visual.size / 2.0
	)

	visual.scale = Vector2(
		1.0,
		1.0
	)

	if flip_horizontal:
		visual.scale.x = -1.0


func get_wildlife_movement_mode(
	wildlife_type: String
) -> String:
	match wildlife_type.to_lower():
		"bird", "bat":
			return "airborne"

		"terrestrial mammal", "reptile":
			return "ground"

		_:
			return "generic"


func get_wildlife_start_position(
	aircraft: Control,
	phase: String,
	ground_y: float,
	ground_contact_offset: float
) -> Vector2:
	match movement_mode:
		"airborne":
			return (
				aircraft.position
				+ get_airborne_start_offset(
					phase
				)
			)

		"ground":
			return Vector2(
				aircraft.position.x + 320,
				ground_y
				- wildlife.size.y
				+ ground_contact_offset
			)

		_:
			# Generic/unknown wildlife uses a schematic right-side approach.
			# This avoids inventing a specific flight or ground trajectory.
			return Vector2(
				aircraft.position.x + 320,
				aircraft.position.y - 80
			)

func get_ground_contact_offset(
	wildlife_type: String
) -> float:
	match wildlife_type.to_lower():
		"terrestrial mammal":
			return 15.0

		"reptile":
			return 20.0

		_:
			return 0.0

func get_airborne_start_offset(
	phase: String
) -> Vector2:
	# Wildlife always enters from the right as a presentation convention.
	# This is not intended to represent observed strike direction.

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


func get_wildlife_size(
	size_category: String
) -> Vector2:
	match size_category.to_lower():
		"small":
			return Vector2(
				42,
				42
			)

		"medium":
			return Vector2(
				62,
				62
			)

		"large":
			return Vector2(
				88,
				88
			)

		_:
			return Vector2(
				52,
				52
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


func get_group_offset(
	index: int,
	mode: String
) -> Vector2:
	if mode == "ground":
		var ground_offsets = [
			Vector2(55, 0),
			Vector2(110, 0),
			Vector2(165, 0),
			Vector2(220, 0),
			Vector2(275, 0),
			Vector2(330, 0),
			Vector2(385, 0),
			Vector2(440, 0),
			Vector2(495, 0),
		]

		return ground_offsets[
			(index - 1) % ground_offsets.size()
		]

	var airborne_offsets = [
		Vector2(55, -30),
		Vector2(75, 25),
		Vector2(110, -50),
		Vector2(135, 10),
		Vector2(165, -25),
		Vector2(190, 35),
		Vector2(220, -45),
		Vector2(245, 15),
		Vector2(275, -10),
	]

	return airborne_offsets[
		(index - 1) % airborne_offsets.size()
	]


func animate_to(
	target_position: Vector2
) -> void:
	var tween := create_tween()

	tween.set_parallel(
		true
	)

	for i in range(
		wildlife_nodes.size()
	):
		var animal = wildlife_nodes[i]

		var target_offset: Vector2

		if movement_mode == "ground":
			target_offset = Vector2(
				i * 10,
				0
			)
		else:
			target_offset = Vector2(
				i * 8,
				i * 3
			)

		tween.tween_property(
			animal,
			"position",
			target_position + target_offset,
			1.5
		)

	await tween.finished


func clear_generated_wildlife() -> void:
	for animal in wildlife_nodes:
		if (
			animal != wildlife
			and is_instance_valid(animal)
		):
			animal.queue_free()

	wildlife_nodes.clear()


func hide_wildlife() -> void:
	for animal in wildlife_nodes:
		if is_instance_valid(animal):
			animal.visible = false
