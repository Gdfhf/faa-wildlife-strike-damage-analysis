extends Control

@onready var placeholder: ColorRect = $Placeholder

var aircraft_visual_type: String = "generic"


func configure_aircraft(
	sampled_context: Dictionary
) -> void:
	var ac_class = str(
		sampled_context.get(
			"AC_CLASS",
			"Not reported"
		)
	)

	aircraft_visual_type = get_aircraft_visual_type(
		ac_class
	)

	apply_placeholder_presentation()


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


func get_impact_position() -> Vector2:
	# Schematic impact location used only by the illustrative animation.
	return (
		position
		+ Vector2(
			size.x * 0.75,
			size.y * 0.15
		)
	)
