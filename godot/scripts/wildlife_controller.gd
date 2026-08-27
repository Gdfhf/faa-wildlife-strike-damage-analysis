extends Control

@onready var wildlife: Control = $Wildlife
@onready var wildlife_placeholder: ColorRect = (
	$Wildlife/Placeholder
)

var wildlife_nodes: Array[Control] = []
var movement_mode: String = "generic"


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
	wildlife_placeholder.size = wildlife_size

	wildlife.position = get_wildlife_start_position(
		aircraft,
		phase,
		ground_y
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
	ground_y: float
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
				ground_y - wildlife.size.y
			)

		_:
			# Generic/unknown wildlife uses a schematic right-side approach.
			# This avoids inventing a specific flight or ground trajectory.
			return Vector2(
				aircraft.position.x + 320,
				aircraft.position.y - 80
			)


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


func get_group_offset(
	index: int,
	mode: String
) -> Vector2:
	if mode == "ground":
		var ground_offsets = [
			Vector2(35, 0),
			Vector2(70, 0),
			Vector2(105, 0),
			Vector2(140, 0),
			Vector2(175, 0),
			Vector2(210, 0),
			Vector2(245, 0),
			Vector2(280, 0),
			Vector2(315, 0),
		]

		return ground_offsets[
			(index - 1) % ground_offsets.size()
		]

	var airborne_offsets = [
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
