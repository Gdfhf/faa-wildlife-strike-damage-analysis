class_name TrialLoader
extends RefCounted


static func get_trial_path() -> String:
	if OS.has_feature("editor"):
		return "res://data/latest_trial.json"

	var executable_dir := OS.get_executable_path().get_base_dir()

	return executable_dir.path_join(
		"../data/latest_trial.json"
	).simplify_path()


static func load_trial() -> Dictionary:
	var trial_path := get_trial_path()

	if not FileAccess.file_exists(trial_path):
		push_error(
			"Trial JSON not found: %s" % trial_path
		)
		return {}

	var file := FileAccess.open(
		trial_path,
		FileAccess.READ
	)

	if file == null:
		push_error("Could not open trial JSON.")
		return {}

	var parsed = JSON.parse_string(
		file.get_as_text()
	)

	if parsed == null:
		push_error("Could not parse trial JSON.")
		return {}

	if not parsed is Dictionary:
		push_error(
			"Trial JSON root must be a Dictionary."
		)
		return {}

	return parsed