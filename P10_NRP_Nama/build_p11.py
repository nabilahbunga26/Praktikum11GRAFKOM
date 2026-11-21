import csv
import math
import os
import time

import bpy
from mathutils import Vector


ROOT = os.path.dirname(os.path.abspath(__file__))
BLEND_FILE = os.path.join(ROOT, "P11_Kelompok_Sekolah_Kampus.blend")
RENDER_DIR = os.path.join(ROOT, "renders")
HDRI_FILE = os.path.join(ROOT, "environment", "studio_small_08_1k.hdr")
METRICS_FILE = os.path.join(RENDER_DIR, "render_metrics.csv")

os.makedirs(RENDER_DIR, exist_ok=True)
scene = bpy.context.scene

generated_names = (
    "Hero_Camera",
    "DOF_Focus_School",
    "Key_Light",
    "Fill_Light",
    "Rim_Light",
    "TEST_Point",
    "TEST_Sun",
    "TEST_Spot",
    "TEST_Area",
    "Detail_Camera",
)
for obj in list(bpy.data.objects):
    if any(obj.name == name or obj.name.startswith(f"{name}.") for name in generated_names):
        bpy.data.objects.remove(obj, do_unlink=True)

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.view_settings.view_transform = "AgX"
scene.render.film_transparent = False


def aim_at(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


def set_camera(camera, location, target, lens):
    camera.location = location
    aim_at(camera, target)
    camera.data.lens = lens


def create_area_light(name, location, target, energy, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.shape = "DISK"
    data.energy = energy
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    aim_at(obj, target)
    return obj


def create_world():
    world = bpy.data.worlds.get("P11_Studio_HDRI_World")
    if world is None:
        world = bpy.data.worlds.new("P11_Studio_HDRI_World")
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()
    links = world.node_tree.links

    coordinates = nodes.new("ShaderNodeTexCoord")
    coordinates.location = (-900, 0)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-680, 0)
    environment = nodes.new("ShaderNodeTexEnvironment")
    environment.location = (-430, 0)
    environment.image = bpy.data.images.load(HDRI_FILE, check_existing=True)
    environment.image.pack()
    background = nodes.new("ShaderNodeBackground")
    background.location = (-180, 0)
    background.inputs["Strength"].default_value = 0.28
    camera_background = nodes.new("ShaderNodeBackground")
    camera_background.location = (-180, -220)
    camera_background.inputs["Color"].default_value = (0.30, 0.33, 0.37, 1)
    camera_background.inputs["Strength"].default_value = 1.0
    light_path = nodes.new("ShaderNodeLightPath")
    light_path.location = (40, -280)
    mix = nodes.new("ShaderNodeMixShader")
    mix.location = (280, 0)
    output = nodes.new("ShaderNodeOutputWorld")
    output.location = (500, 0)

    links.new(coordinates.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], environment.inputs["Vector"])
    links.new(environment.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], mix.inputs[1])
    links.new(camera_background.outputs["Background"], mix.inputs[2])
    links.new(light_path.outputs["Is Camera Ray"], mix.inputs["Fac"])
    links.new(mix.outputs["Shader"], output.inputs["Surface"])
    world["hdri_rotation_z"] = 0.0
    scene.world = world
    return world, mapping


def set_world_strength(value):
    background = next(
        node for node in scene.world.node_tree.nodes
        if node.type == "BACKGROUND" and node.inputs["Color"].is_linked
    )
    background.inputs["Strength"].default_value = value


world, hdri_mapping = create_world()

hero_camera = scene.camera
if hero_camera is None:
    hero_camera_data = bpy.data.cameras.new("Hero_Camera")
    hero_camera = bpy.data.objects.new("Hero_Camera", hero_camera_data)
    scene.collection.objects.link(hero_camera)
hero_camera.name = "Hero_Camera"
scene.camera = hero_camera
hero_target = Vector((0.0, 1.0, -1.0))
hero_location = Vector((2.74, -81.19, 28.45))
set_camera(hero_camera, hero_location, hero_target, 50.0)
hero_camera.data.dof.use_dof = False

focus = bpy.data.objects.new("DOF_Focus_School", None)
scene.collection.objects.link(focus)
focus.location = (0.0, -0.5, 5.0)

key = create_area_light(
    "Key_Light",
    (-22.0, -18.0, 28.0),
    (0.0, -1.0, 3.5),
    22000,
    15.0,
    (1.0, 0.90, 0.78),
)
fill = create_area_light(
    "Fill_Light",
    (20.0, -7.0, 20.0),
    (0.0, -1.0, 3.5),
    8500,
    18.0,
    (0.72, 0.84, 1.0),
)
rim = create_area_light(
    "Rim_Light",
    (-1.0, 20.0, 24.0),
    (0.0, -1.0, 4.0),
    14500,
    12.0,
    (1.0, 0.84, 0.68),
)

study_point_data = bpy.data.lights.new("TEST_Point", "POINT")
study_point_data.energy = 2200
study_point_data.shadow_soft_size = 0.35
study_point = bpy.data.objects.new("TEST_Point", study_point_data)
scene.collection.objects.link(study_point)
study_point.location = (-10.0, -11.0, 12.0)

study_sun_data = bpy.data.lights.new("TEST_Sun", "SUN")
study_sun_data.energy = 2.0
study_sun_data.angle = math.radians(8.0)
study_sun = bpy.data.objects.new("TEST_Sun", study_sun_data)
scene.collection.objects.link(study_sun)
study_sun.location = (-10.0, -10.0, 15.0)
aim_at(study_sun, (0.0, 0.0, 2.0))

study_spot_data = bpy.data.lights.new("TEST_Spot", "SPOT")
study_spot_data.energy = 4000
study_spot_data.color = (1.0, 0.82, 0.62)
study_spot_data.spot_size = math.radians(60.0)
study_spot_data.spot_blend = 0.25
study_spot = bpy.data.objects.new("TEST_Spot", study_spot_data)
scene.collection.objects.link(study_spot)
study_spot.location = (-2.0, -16.0, 16.0)
aim_at(study_spot, (0.0, 0.0, 3.0))

study_area_data = bpy.data.lights.new("TEST_Area", "AREA")
study_area_data.shape = "DISK"
study_area_data.energy = 18000
study_area_data.size = 10.0
study_area = bpy.data.objects.new("TEST_Area", study_area_data)
scene.collection.objects.link(study_area)
study_area.location = (-18.0, -15.0, 26.0)
aim_at(study_area, (0.0, 0.0, 3.0))

lights = [
    obj for obj in scene.objects
    if obj.type == "LIGHT" and obj not in (key, fill, rim, study_point, study_sun, study_spot, study_area)
]
for light in lights:
    light.hide_render = True


def hide_all_lights():
    for light in (key, fill, rim, study_point, study_sun, study_spot, study_area):
        light.hide_render = True


def enable_three_point(key_energy=22000, fill_energy=8500, rim_energy=14500):
    hide_all_lights()
    key.hide_render = False
    fill.hide_render = False
    rim.hide_render = False
    key.data.energy = key_energy
    fill.data.energy = fill_energy
    rim.data.energy = rim_energy


def set_engine(engine, samples=24, denoise=True):
    if engine == "CYCLES":
        scene.render.engine = "CYCLES"
        scene.cycles.samples = samples
        scene.cycles.use_denoising = denoise
    else:
        scene.render.engine = "BLENDER_EEVEE"


records = []


def render_case(name, engine="BLENDER_EEVEE", samples=24, denoise=True, resolution=(640, 360)):
    set_engine(engine, samples, denoise)
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.filepath = os.path.join(RENDER_DIR, f"{name}.png")
    started = time.perf_counter()
    bpy.ops.render.render(write_still=True)
    elapsed = time.perf_counter() - started
    records.append(
        {
            "file": f"{name}.png",
            "engine": scene.render.engine,
            "samples": samples if engine == "CYCLES" else "",
            "denoising": denoise if engine == "CYCLES" else "",
            "resolution": f"{scene.render.resolution_x}x{scene.render.resolution_y}",
            "render_seconds": round(elapsed, 2),
        }
    )


def render_light_study(name, light):
    hide_all_lights()
    light.hide_render = False
    set_world_strength(0.18)
    render_case(name)


set_camera(hero_camera, hero_location, hero_target, 50.0)
render_light_study("light_point", study_point)
study_point_data.shadow_soft_size = 0.08
render_light_study("point_radius_small", study_point)
study_point_data.shadow_soft_size = 2.0
render_light_study("point_radius_large", study_point)

study_sun_data.angle = math.radians(1.0)
render_light_study("light_sun", study_sun)
render_light_study("sun_angle_small", study_sun)
study_sun_data.angle = math.radians(30.0)
render_light_study("sun_angle_large", study_sun)

study_spot_data.spot_blend = 0.05
render_light_study("light_spot", study_spot)
render_light_study("spot_blend_low", study_spot)
study_spot_data.spot_blend = 0.85
render_light_study("spot_blend_high", study_spot)

study_area_data.size = 2.0
render_light_study("light_area", study_area)
render_light_study("area_size_small", study_area)
study_area_data.size = 18.0
render_light_study("area_size_large", study_area)

enable_three_point()
set_world_strength(0.28)
render_case("three_point")
fill.data.energy = key.data.energy * 0.95
render_case("key_fill_strong")
fill.data.energy = key.data.energy * 0.48
render_case("key_fill_balanced")
fill.data.energy = key.data.energy * 0.18
render_case("key_fill_dramatic")
fill.data.energy = 8500
rim.hide_render = True
render_case("rim_off")
rim.hide_render = False
render_case("rim_on")

set_camera(hero_camera, hero_location, hero_target, 50.0)
render_case("composition_center")
set_camera(hero_camera, hero_location, (4.0, 1.0, 3.5), 50.0)
render_case("composition_rule_of_thirds")

set_camera(hero_camera, (0.0, -82.0, 14.0), (0.0, 0.0, 4.0), 50.0)
render_case("angle_eye_level")
set_camera(hero_camera, (0.0, -62.0, 7.0), (0.0, 0.0, 4.0), 50.0)
render_case("angle_low")
set_camera(hero_camera, (0.0, -72.0, 38.0), (0.0, 0.0, 4.0), 50.0)
render_case("angle_high")

school_target = Vector((0.0, -0.5, 5.0))
camera_direction = Vector((0.0, -1.0, 0.34)).normalized()
for focal_length in (24.0, 50.0, 85.0):
    distance = 62.0 * focal_length / 50.0
    set_camera(
        hero_camera,
        school_target + camera_direction * distance,
        school_target,
        focal_length,
    )
    render_case(f"focal_{int(focal_length)}")

set_camera(hero_camera, hero_location, hero_target, 50.0)
hero_camera.data.dof.use_dof = False
render_case("dof_off")
hero_camera.data.dof.use_dof = True
hero_camera.data.dof.focus_object = focus
hero_camera.data.dof.aperture_fstop = 3.5
render_case("dof_on")
hero_camera.data.dof.use_dof = False

hdri_mapping.inputs["Rotation"].default_value[2] = 0.0
world["hdri_rotation_z"] = 0.0
set_world_strength(0.5)
enable_three_point(14000, 5000, 10000)
render_case("hdri_studio")
hdri_mapping.inputs["Rotation"].default_value[2] = math.radians(90)
world["hdri_rotation_z"] = math.radians(90)
render_case("hdri_rotation_90")
hdri_mapping.inputs["Rotation"].default_value[2] = 0.0
world["hdri_rotation_z"] = 0.0

enable_three_point()
set_world_strength(0.28)
set_camera(hero_camera, hero_location, hero_target, 50.0)
render_case("render_eevee", "BLENDER_EEVEE", resolution=(1280, 720))
render_case("render_cycles", "CYCLES", samples=32, resolution=(1280, 720))
for sample_count in (8, 24, 64):
    render_case(
        f"sampling_{sample_count:02d}",
        "CYCLES",
        samples=sample_count,
        denoise=False,
        resolution=(640, 360),
    )
render_case("denoise_off", "CYCLES", samples=16, denoise=False)
render_case("denoise_on", "CYCLES", samples=16, denoise=True)

enable_three_point(26000, 2200, 15500)
render_case("challenge_dramatic")
enable_three_point(18000, 11000, 8000)
key.data.size = 24.0
fill.data.size = 24.0
rim.data.size = 20.0
render_case("challenge_soft_studio")
key.data.size = 15.0
fill.data.size = 18.0
rim.data.size = 12.0

detail_camera_data = bpy.data.cameras.new("Detail_Camera")
detail_camera = bpy.data.objects.new("Detail_Camera", detail_camera_data)
scene.collection.objects.link(detail_camera)
detail_camera.location = (15.0, -34.0, 10.0)
aim_at(detail_camera, (10.5, -18.5, 1.3))
detail_camera_data.lens = 85.0
detail_camera_data.dof.use_dof = True
detail_camera_data.dof.focus_object = bpy.data.objects.get("SchoolBus")
detail_camera_data.dof.aperture_fstop = 5.6
scene.camera = detail_camera
render_case("detail_camera")
scene.camera = hero_camera

enable_three_point()
set_world_strength(0.28)
set_camera(hero_camera, hero_location, hero_target, 50.0)
hero_camera.data.dof.use_dof = False
scene.render.resolution_x = 1440
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.filepath = os.path.join(RENDER_DIR, "hero_final.png")
scene.render.engine = "CYCLES"
scene.cycles.samples = 64
scene.cycles.use_denoising = True
hero_camera.data.dof.use_dof = True
hero_camera.data.dof.focus_object = focus
hero_camera.data.dof.aperture_fstop = 11.0
started = time.perf_counter()
bpy.ops.render.render(write_still=True)
elapsed = time.perf_counter() - started
records.append(
    {
        "file": "hero_final.png",
        "engine": scene.render.engine,
        "samples": scene.cycles.samples,
        "denoising": scene.cycles.use_denoising,
        "resolution": f"{scene.render.resolution_x}x{scene.render.resolution_y}",
        "render_seconds": round(elapsed, 2),
    }
)

with open(METRICS_FILE, "w", newline="", encoding="utf-8") as metrics_file:
    writer = csv.DictWriter(
        metrics_file,
        fieldnames=("file", "engine", "samples", "denoising", "resolution", "render_seconds"),
    )
    writer.writeheader()
    writer.writerows(records)

bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
print(f"P11 complete: {len(records)} renders; metrics saved to {METRICS_FILE}")
