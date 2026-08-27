class_name TrialLoader
extends RefCounted

const TRIAL_PATH := "res://data/latest_trial.json"


static func load_trial() -> Dictionary:
	if not FileAccess.file_exists(TRIAL_PATH):
		push_error("Trial JSON not found: %s" % TRIAL_PATH)
		return {}

	var file := FileAccess.open(
		TRIAL_PATH,
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
		push_error("Trial JSON root must be a Dictionary.")
		return {}

	return parsed
