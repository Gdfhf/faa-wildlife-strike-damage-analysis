class_name TrialLoader
extends RefCounted


static func get_trial_path() -> String:
	if OS.has_feature("web"):
		return "res://data/latest_trial.json"

	if OS.has_feature("editor"):
		return "res://data/latest_trial.json"

	var executable_dir := OS.get_executable_path().get_base_dir()

	return executable_dir.path_join(
		"../data/latest_trial.json"
	).simplify_path()


static func load_trial() -> Dictionary:
	# On Web, first try to load a trial passed through the URL.
	if OS.has_feature("web"):
		var web_trial := _load_trial_from_url()

		if not web_trial.is_empty():
			return web_trial

	# Otherwise fall back to the normal JSON-file workflow.
	return _load_trial_from_file()


static func _load_trial_from_url() -> Dictionary:
	var encoded = JavaScriptBridge.eval(
		"""
		(() => {
			const params = new URLSearchParams(window.location.search);
			return params.get("trial") || "";
		})()
		""",
		true
	)

	if encoded == null:
		return {}

	var encoded_text := str(encoded)

	if encoded_text.is_empty():
		return {}

	# Convert URL-safe Base64 back to standard Base64.
	encoded_text = encoded_text.replace("-", "+")
	encoded_text = encoded_text.replace("_", "/")

	while encoded_text.length() % 4 != 0:
		encoded_text += "="

	var raw := Marshalls.base64_to_raw(
		encoded_text
	)

	if raw.is_empty():
		push_error(
			"Could not decode trial URL payload."
		)
		return {}

	var json_text := raw.get_string_from_utf8()

	var parsed = JSON.parse_string(
		json_text
	)

	if parsed == null:
		push_error(
			"Could not parse trial URL JSON."
		)
		return {}

	if not parsed is Dictionary:
		push_error(
			"Trial URL payload must contain a Dictionary."
		)
		return {}

	print("Loaded trial from Web URL.")

	return parsed


static func _load_trial_from_file() -> Dictionary:
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
		push_error(
			"Could not open trial JSON."
		)
		return {}

	var parsed = JSON.parse_string(
		file.get_as_text()
	)

	if parsed == null:
		push_error(
			"Could not parse trial JSON."
		)
		return {}

	if not parsed is Dictionary:
		push_error(
			"Trial JSON root must be a Dictionary."
		)
		return {}

	return parsed