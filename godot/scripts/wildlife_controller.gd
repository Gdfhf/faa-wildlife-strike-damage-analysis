extends Control

@onready var wildlife: Control = $Wildlife
@onready var wildlife_placeholder: ColorRect = (
	$Wildlife/Placeholder
)

var wildlife_nodes: Array[Control] = []


func configure_wildlife(
	sampled_context: Dictionary,
	aircraft: Control
) -> void:
	clear_generated_wildlife()

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

	var bird_size = get_wildlife_size(
		size_category
	)

	var bird_count = get_wildlife_count(
		num_struck
	)

	wildlife.size = bird_size
	wildlife_placeholder.size = bird_size

	wildlife.position = (
		aircraft.position
		+ get_wildlife_start_offset(
			phase
		)
	)

	wildlife.visible = true

	wildlife_nodes.append(
		wildlife
	)

	for i in range(
		1,
		bird_count
	):
		var bird = wildlife.duplicate() as Control

		add_child(
			bird
		)

		bird.size = bird_size

		bird.position = (
			wildlife.position
			+ get_flock_offset(i)
		)

		wildlife_nodes.append(
			bird
		)


func clear_generated_wildlife() -> void:
	for bird in wildlife_nodes:
		if bird != wildlife and is_instance_valid(bird):
			bird.queue_free()

	wildlife_nodes.clear()


func get_wildlife_start_offset(
	phase: String
) -> Vector2:
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


func hide_wildlife() -> void:
	for bird in wildlife_nodes:
		if is_instance_valid(bird):
			bird.visible = false
