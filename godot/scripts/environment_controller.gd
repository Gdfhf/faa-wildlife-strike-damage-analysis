extends Control

@onready var background: ColorRect = $Background
@onready var ground: ColorRect = $Ground

@onready var clouds_layer: Control = $WeatherEffects/CloudsLayer
@onready var precipitation_layer: Control = $WeatherEffects/PrecipitationLayer
@onready var fog_overlay: ColorRect = $WeatherEffects/FogOverlay


func configure_environment(
	sampled_context: Dictionary
) -> void:
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


func configure_phase_of_flight(
	sampled_context: Dictionary,
	aircraft: Control
) -> void:
	var phase = str(
		sampled_context.get(
			"PHASE_OF_FLIGHT",
			"Unknown"
		)
	)

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
			aircraft.position = Vector2(
				500,
				270
			)

		"En Route":
			aircraft.position = Vector2(
				350,
				260
			)

		_:
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
		},
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

	for _i in range(45):
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
	while is_inside_tree():
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

	for _i in range(35):
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
	while is_inside_tree():
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
