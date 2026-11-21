import json
import math
import os
import shutil
import time

import bpy
import bmesh
from mathutils import Vector


ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(ROOT)
TEXTURE_DIR = os.path.join(ROOT, "textures")
SCHOOL_TEXTURE_DIR = os.path.join(TEXTURE_DIR, "School_Building")
SCREENSHOT_DIR = os.path.join(ROOT, "screenshots")
BLEND_OUTPUT = os.path.join(ROOT, "P10_Kelompok_Sekolah_UV_PBR.blend")
UV_DATA_OUTPUT = os.path.join(ROOT, "uv_layout_data.json")
SOURCE_TEXTURE_DIR = os.path.join(PROJECT_ROOT, "textures")
SOURCE_BLEND = os.path.join(PROJECT_ROOT, "P10_Kelompok_Sekolah_Kampus.blend")
SOURCE_CRATE = os.path.join(
    PROJECT_ROOT, "assets", "Wooden_Crate_01", "wooden_crate_01_2k.blend"
)
SOURCE_SCREENSHOTS = os.path.join(PROJECT_ROOT, "screenshots")
PACKAGED_ASSET_DIR = os.path.join(ROOT, "assets", "Wooden_Crate_01")

os.makedirs(SCHOOL_TEXTURE_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

if not os.path.isfile(SOURCE_BLEND):
    raise FileNotFoundError(f"Required source scene was not found: {SOURCE_BLEND}")

for texture_group in ("School_Bus", "School_Students", "Wooden_Crate_01"):
    source_group = os.path.join(SOURCE_TEXTURE_DIR, texture_group)
    if os.path.isdir(source_group):
        shutil.copytree(
            source_group,
            os.path.join(TEXTURE_DIR, texture_group),
            dirs_exist_ok=True,
        )
legacy_duplicate_map = os.path.join(TEXTURE_DIR, "School_BaseColor.png")
if os.path.isfile(legacy_duplicate_map):
    os.remove(legacy_duplicate_map)
if os.path.isfile(SOURCE_CRATE):
    os.makedirs(PACKAGED_ASSET_DIR, exist_ok=True)
    shutil.copy2(SOURCE_CRATE, PACKAGED_ASSET_DIR)
for source_name, packaged_name in (
    ("PBR_Wooden_Crate_Comparison.png", "11_wooden_crate_pbr_comparison.png"),
    ("PBR_Students_Before_After.png", "12_students_pbr_before_after.png"),
    ("Final_Campus_Render.png", "13_campus_final_render.png"),
):
    source_path = os.path.join(SOURCE_SCREENSHOTS, source_name)
    if os.path.isfile(source_path):
        shutil.copy2(source_path, os.path.join(SCREENSHOT_DIR, packaged_name))

building = bpy.data.objects.get("SCH_Building")
if building is None or building.type != "MESH":
    raise RuntimeError("The source scene must contain the SCH_Building mesh.")

mesh = building.data
production_uv = mesh.uv_layers.get("UVMap")
if production_uv is None:
    raise RuntimeError("SCH_Building is missing its production UVMap.")
production_uv_name = production_uv.name

material = bpy.data.materials.get("MAT_School_Building")
if material is None or not material.use_nodes:
    raise RuntimeError("MAT_School_Building with a node graph is required.")

expected_maps = {
    "BaseColor (sRGB)": ("School_BaseColor.png", "sRGB"),
    "Roughness (Non-Color)": ("School_Roughness.png", "Non-Color"),
    "Metallic (Non-Color)": ("School_Metallic.png", "Non-Color"),
    "Normal OpenGL (Non-Color)": ("School_Normal.png", "Non-Color"),
    "Emission Mask (sRGB)": ("School_Emission.png", "sRGB"),
}
for node_name, (filename, color_space) in expected_maps.items():
    node = material.node_tree.nodes.get(node_name)
    if node is None or node.type != "TEX_IMAGE" or node.image is None or not node.image.has_data:
        if node is None or node.type != "TEX_IMAGE" or node.image is None:
            raise RuntimeError(f"Required image texture node is missing: {node_name}")
    node.image.colorspace_settings.name = color_space
    destination = os.path.join(SCHOOL_TEXTURE_DIR, filename)
    if node.image.packed_file is not None:
        with open(destination, "wb") as texture_file:
            texture_file.write(node.image.packed_file.data)
    elif node.image.has_data:
        node.image.filepath_raw = destination
        node.image.file_format = "PNG"
        node.image.save()
    else:
        raise RuntimeError(f"Required image texture has no pixel buffer or packed data: {node_name}")

uv_node = material.node_tree.nodes.get("UV Map")
if uv_node is None or uv_node.type != "UVMAP":
    raise RuntimeError("The school PBR material must use an explicit UV Map node.")
uv_node.uv_map = "UVMap"

links = {
    (link.from_node.name, link.from_socket.name, link.to_node.name, link.to_socket.name)
    for link in material.node_tree.links
}
required_links = {
    ("BaseColor (sRGB)", "Color", "Principled BSDF", "Base Color"),
    ("Roughness (Non-Color)", "Color", "Principled BSDF", "Roughness"),
    ("Metallic (Non-Color)", "Color", "Principled BSDF", "Metallic"),
    ("Normal OpenGL (Non-Color)", "Color", "Normal Map", "Color"),
    ("Normal Map", "Normal", "Principled BSDF", "Normal"),
    ("Emission Mask (sRGB)", "Color", "Principled BSDF", "Emission Color"),
}
missing_links = required_links - links
if missing_links:
    raise RuntimeError(f"School PBR node links are incomplete: {sorted(missing_links)}")

mesh_bm = bmesh.new()
mesh_bm.from_mesh(mesh)
mesh_bm.normal_update()
topology = {
    "vertices": len(mesh_bm.verts),
    "edges": len(mesh_bm.edges),
    "faces": len(mesh_bm.faces),
    "ngons": sum(len(face.verts) > 4 for face in mesh_bm.faces),
    "boundary_edges": sum(edge.is_boundary for edge in mesh_bm.edges),
}
doubles = bmesh.ops.find_doubles(mesh_bm, verts=list(mesh_bm.verts), dist=0.00001)
topology["coincident_vertices_within_0_00001m"] = len(doubles.get("targetmap", {}))
mesh_bm.free()

if topology["ngons"]:
    raise RuntimeError(f"Unexpected n-gons in school asset: {topology['ngons']}")

original_layer_names = [layer.name for layer in mesh.uv_layers]
if mesh.uv_layers.get("P10_Manual_Unwrap"):
    mesh.uv_layers.remove(mesh.uv_layers["P10_Manual_Unwrap"])

seam_bm = bmesh.new()
seam_bm.from_mesh(mesh)
seam_bm.normal_update()
seam_angle = math.radians(45.0)
for edge in seam_bm.edges:
    if edge.is_boundary:
        edge.seam = True
    elif len(edge.link_faces) == 2 and edge.calc_face_angle(0.0) >= seam_angle:
        edge.seam = True
seam_edges = [
    [edge.verts[0].index, edge.verts[1].index]
    for edge in seam_bm.edges
    if edge.seam
]
seam_bm.to_mesh(mesh)
seam_bm.free()
mesh.update()

study_uv = mesh.uv_layers.new(name="P10_Manual_Unwrap")
mesh.uv_layers.active_index = mesh.uv_layers.find(study_uv.name)
bpy.ops.object.select_all(action="DESELECT")
bpy.context.view_layer.objects.active = building
building.select_set(True)
if building.mode != "OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
manual_started = time.perf_counter()
bpy.ops.uv.unwrap(method="CONFORMAL", margin=0.0)
bpy.ops.object.mode_set(mode="OBJECT")
initial_uv = [
    [[mesh.loops[index].vertex_index,
      float(mesh.uv_layers.active.data[index].uv.x),
      float(mesh.uv_layers.active.data[index].uv.y)]
     for index in range(poly.loop_start, poly.loop_start + poly.loop_total)]
    for poly in mesh.polygons
]
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.average_islands_scale()
bpy.ops.uv.pack_islands(rotate=True, margin=0.006)
bpy.ops.object.mode_set(mode="OBJECT")
manual_seconds = time.perf_counter() - manual_started
final_uv = [
    [[mesh.loops[index].vertex_index,
      float(mesh.uv_layers.active.data[index].uv.x),
      float(mesh.uv_layers.active.data[index].uv.y)]
     for index in range(poly.loop_start, poly.loop_start + poly.loop_total)]
    for poly in mesh.polygons
]

# Restore the UV map used by the existing school texture atlas.
mesh.uv_layers.active_index = mesh.uv_layers.find(production_uv_name)
mesh.uv_layers.active_render_index = mesh.uv_layers.find(production_uv_name)
building["p10_uv_study_layer"] = "P10_Manual_Unwrap"
building["p10_uv_production_layer"] = "UVMap"
building["p10_seam_rule"] = "Boundary edges and hard edges >= 45 degrees"

uv_payload = {
    "object": building.name,
    "topology": topology,
    "seam_edge_count": len(seam_edges),
    "seam_edges": seam_edges,
    "initial_uv": initial_uv,
    "final_uv": final_uv,
    "production_uv_layer": "UVMap",
    "study_uv_layer": "P10_Manual_Unwrap",
}
with open(UV_DATA_OUTPUT, "w", encoding="utf-8") as uv_file:
    json.dump(uv_payload, uv_file)


def aim_at(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


def count_uv_islands(polygons):
    parents = list(range(len(polygons)))

    def find(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(first, second):
        first_root = find(first)
        second_root = find(second)
        if first_root != second_root:
            parents[second_root] = first_root

    edge_faces = {}
    for face_index, polygon in enumerate(polygons):
        for index, start in enumerate(polygon):
            end = polygon[(index + 1) % len(polygon)]
            key = tuple(sorted((start[0], end[0])))
            edge_faces.setdefault(key, []).append(
                (face_index, {start[0]: start[1:], end[0]: end[1:]})
            )

    for connected_faces in edge_faces.values():
        if len(connected_faces) != 2:
            continue
        (first, first_uv), (second, second_uv) = connected_faces
        shared_vertices = first_uv.keys() & second_uv.keys()
        if len(shared_vertices) == 2 and all(
            math.dist(first_uv[vertex], second_uv[vertex]) < 1e-6
            for vertex in shared_vertices
        ):
            union(first, second)
    return len({find(index) for index in range(len(polygons))})


def make_simple_material(name, color, metallic=0.0, roughness=0.55):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


def ensure_uv_mapping_for_image_textures(material):
    if not material.use_nodes:
        return

    nodes = material.node_tree.nodes
    links = material.node_tree.links
    image_nodes = [node for node in nodes if node.type == "TEX_IMAGE" and node.image]
    if not image_nodes:
        return

    tex_coord = next((node for node in nodes if node.type == "TEX_COORD"), None)

    grouped_nodes = {}
    for image_node in image_nodes:
        vector_input = image_node.inputs["Vector"]
        incoming = next(
            (link for link in links if link.to_node == image_node and link.to_socket == vector_input),
            None,
        )
        if incoming and incoming.from_node.type == "MAPPING":
            continue

        if incoming:
            source_node = incoming.from_node
            source_socket = incoming.from_socket
        else:
            if tex_coord is None:
                tex_coord = nodes.new("ShaderNodeTexCoord")
                tex_coord.label = "UV Coordinates"
            source_node = tex_coord
            source_socket = tex_coord.outputs["UV"]
        key = (source_node.name, source_socket.identifier)
        grouped_nodes.setdefault(key, (source_node, source_socket, []))[2].append(image_node)
        if incoming:
            links.remove(incoming)

    for source_node, source_socket, targets in grouped_nodes.values():
        mapping = nodes.new("ShaderNodeMapping")
        mapping.label = "UV Mapping (Identity)"
        mapping.location = (
            min(node.location.x for node in targets) - 280,
            max(node.location.y for node in targets),
        )
        links.new(source_socket, mapping.inputs["Vector"])
        for image_node in targets:
            links.new(mapping.outputs["Vector"], image_node.inputs["Vector"])


def create_study_render(name, material_override=None, show_seams=False, stretch_checker=False):
    scene = bpy.context.scene
    corners = [building.matrix_world @ Vector(corner) for corner in building.bound_box]
    center = sum(corners, Vector()) / len(corners)
    distance = max(building.dimensions.x, building.dimensions.y, building.dimensions.z) * 2.8

    hidden_states = {obj.name: obj.hide_render for obj in scene.objects}
    old_camera = scene.camera
    old_world = scene.world
    old_engine = scene.render.engine
    old_resolution = (
        scene.render.resolution_x,
        scene.render.resolution_y,
        scene.render.resolution_percentage,
    )
    old_filepath = scene.render.filepath
    old_samples = scene.cycles.samples
    old_denoising = scene.cycles.use_denoising

    study = building.copy()
    study.data = building.data.copy()
    study.name = "P10_UV_Study_Building"
    scene.collection.objects.link(study)
    study.hide_render = False
    if stretch_checker:
        study_uv = study.data.uv_layers.get("P10_Manual_Unwrap")
        if study_uv is None:
            raise RuntimeError("The study mesh is missing P10_Manual_Unwrap.")
        for loop_uv in study_uv.data:
            loop_uv.uv.x = 0.5 + (loop_uv.uv.x - 0.5) * 1.8
    if material_override is not None:
        study.data.materials.clear()
        study.data.materials.append(material_override)

    camera_data = bpy.data.cameras.new(f"{name}_Camera")
    camera = bpy.data.objects.new(f"{name}_Camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = center + Vector((distance * 0.56, -distance, distance * 0.48))
    aim_at(camera, center)
    camera_data.lens = 50
    scene.camera = camera

    light_objects = []
    for index, (offset, power, size, color) in enumerate((
        ((-distance * 0.45, -distance * 0.55, distance * 0.6), 28000, 13.0, (1.0, 0.88, 0.74)),
        ((distance * 0.5, -distance * 0.25, distance * 0.35), 12000, 17.0, (0.73, 0.84, 1.0)),
        ((0.0, distance * 0.35, distance * 0.5), 17000, 11.0, (1.0, 0.95, 0.86)),
    )):
        light_data = bpy.data.lights.new(f"{name}_Light_{index}", "AREA")
        light_data.energy = power
        light_data.shape = "DISK"
        light_data.size = size
        light_data.color = color
        light_obj = bpy.data.objects.new(light_data.name, light_data)
        scene.collection.objects.link(light_obj)
        light_obj.location = center + Vector(offset)
        aim_at(light_obj, center)
        light_objects.append(light_obj)

    seam_obj = None
    if show_seams:
        curve = bpy.data.curves.new(f"{name}_Seams", "CURVE")
        curve.dimensions = "3D"
        curve.bevel_depth = 0.025
        curve.bevel_resolution = 2
        for first, second in seam_edges:
            spline = curve.splines.new("POLY")
            spline.points.add(1)
            for point, index in zip(spline.points, (first, second)):
                world_point = study.matrix_world @ mesh.vertices[index].co
                point.co = (*world_point, 1.0)
        seam_obj = bpy.data.objects.new(curve.name, curve)
        scene.collection.objects.link(seam_obj)
        seam_obj.data.materials.append(make_simple_material(
            f"{name}_Seam_Red", (0.95, 0.035, 0.02), roughness=0.4
        ))

    for obj in scene.objects:
        obj.hide_render = obj not in (study, camera, *light_objects, seam_obj)
    if seam_obj is not None:
        seam_obj.hide_render = False
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 20
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    temporary_world = bpy.data.worlds.new(f"{name}_World")
    scene.world = temporary_world
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.23, 0.27, 0.32, 1)
    background.inputs["Strength"].default_value = 0.55
    bpy.ops.render.render(write_still=True)

    scene.world = old_world
    scene.camera = old_camera
    scene.render.engine = old_engine
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = old_resolution
    scene.render.filepath = old_filepath
    scene.cycles.samples = old_samples
    scene.cycles.use_denoising = old_denoising
    study_mesh = study.data
    for obj in list(scene.objects):
        if obj in light_objects or obj == camera or obj == study or obj == seam_obj:
            bpy.data.objects.remove(obj, do_unlink=True)
    if study_mesh.users == 0:
        bpy.data.meshes.remove(study_mesh)
    if temporary_world.users == 0:
        bpy.data.worlds.remove(temporary_world)
    for obj in scene.objects:
        obj.hide_render = hidden_states.get(obj.name, False)


clay = make_simple_material("P10_UV_Study_Clay", (0.34, 0.38, 0.43))
create_study_render("01_model_before_uv", clay)

checker = bpy.data.materials.new("P10_UV_Checker_Test")
checker.use_nodes = True
checker_nodes = checker.node_tree.nodes
checker_nodes.clear()
checker_links = checker.node_tree.links
checker_uv = checker_nodes.new("ShaderNodeUVMap")
checker_uv.uv_map = "P10_Manual_Unwrap"
checker_texture = checker_nodes.new("ShaderNodeTexChecker")
checker_texture.inputs["Scale"].default_value = 12.0
checker_shader = checker_nodes.new("ShaderNodeBsdfPrincipled")
checker_output = checker_nodes.new("ShaderNodeOutputMaterial")
checker_links.new(checker_uv.outputs["UV"], checker_texture.inputs["Vector"])
checker_links.new(checker_texture.outputs["Color"], checker_shader.inputs["Base Color"])
checker_links.new(checker_shader.outputs["BSDF"], checker_output.inputs["Surface"])
create_study_render("04_checker_test", checker)
create_study_render("14_checker_stretched", checker, stretch_checker=True)
create_study_render("02_marked_seams", clay, show_seams=True)
create_study_render("10_final_material", material)

def parameter_variant(name, socket_name, value):
    variant = material.copy()
    variant.name = name
    shader = variant.node_tree.nodes["Principled BSDF"]
    socket = shader.inputs[socket_name]
    for link in list(socket.links):
        variant.node_tree.links.remove(link)
    socket.default_value = value
    return variant


solid_base = parameter_variant(
    "P10_BaseColor_Solid_Test", "Base Color", (0.82, 0.48, 0.18, 1.0)
)
create_study_render("15_basecolor_solid", solid_base)

roughness_low = parameter_variant("P10_Roughness_0_1_Test", "Roughness", 0.1)
roughness_high = parameter_variant("P10_Roughness_0_9_Test", "Roughness", 0.9)
create_study_render("16_roughness_0_1", roughness_low)
create_study_render("17_roughness_0_9", roughness_high)

metallic_zero = parameter_variant("P10_Metallic_0_Test", "Metallic", 0.0)
metallic_one = parameter_variant("P10_Metallic_1_Test", "Metallic", 1.0)
create_study_render("18_metallic_0", metallic_zero)
create_study_render("19_metallic_1", metallic_one)

normal_test = material.copy()
normal_test.name = "P10_NormalMap_Strength_Test"
normal_node = normal_test.node_tree.nodes["Normal Map"]
normal_node.inputs["Strength"].default_value = 0.0
create_study_render("08_normal_off", normal_test)
normal_node.inputs["Strength"].default_value = 0.8
create_study_render("09_normal_on", normal_test)
normal_node.inputs["Strength"].default_value = 0.2
create_study_render("20_normal_strength_low", normal_test)
normal_node.inputs["Strength"].default_value = 1.5
create_study_render("21_normal_strength_high", normal_test)

roughness_image = material.node_tree.nodes["Roughness (Non-Color)"].image
original_roughness_space = roughness_image.colorspace_settings.name
roughness_image.colorspace_settings.name = "sRGB"
create_study_render("22_roughness_srgb_test", material)
roughness_image.colorspace_settings.name = "Non-Color"
create_study_render("23_roughness_noncolor_test", material)
roughness_image.colorspace_settings.name = original_roughness_space

emission_low = material.copy()
emission_low.name = "P10_Emission_Low_Test"
emission_low.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.2
emission_high = material.copy()
emission_high.name = "P10_Emission_High_Test"
emission_high.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 5.0
create_study_render("24_emission_low", emission_low)
create_study_render("25_emission_high", emission_high)

# Generate a second manually defined seam strategy and Smart UV on temporary copies.
alternate_study = building.copy()
alternate_study.data = building.data.copy()
alternate_study.name = "P10_AlternateSeams_Comparison"
bpy.context.scene.collection.objects.link(alternate_study)
alternate_mesh = alternate_study.data
alternate_bm = bmesh.new()
alternate_bm.from_mesh(alternate_mesh)
for edge in alternate_bm.edges:
    edge.seam = edge.is_boundary
alternate_bm.to_mesh(alternate_mesh)
alternate_bm.free()
alternate_layer = alternate_mesh.uv_layers.new(name="P10_BoundaryOnly")
alternate_mesh.uv_layers.active_index = alternate_mesh.uv_layers.find(alternate_layer.name)
bpy.ops.object.select_all(action="DESELECT")
alternate_study.select_set(True)
bpy.context.view_layer.objects.active = alternate_study
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
alternate_started = time.perf_counter()
bpy.ops.uv.unwrap(method="CONFORMAL", margin=0.0)
bpy.ops.uv.average_islands_scale()
bpy.ops.uv.pack_islands(rotate=True, margin=0.006)
bpy.ops.object.mode_set(mode="OBJECT")
alternate_seconds = time.perf_counter() - alternate_started
alternate_layer = alternate_mesh.uv_layers.get("P10_BoundaryOnly")
alternate_uv = [
    [[alternate_mesh.loops[index].vertex_index,
      float(alternate_layer.data[index].uv.x),
      float(alternate_layer.data[index].uv.y)]
     for index in range(poly.loop_start, poly.loop_start + poly.loop_total)]
    for poly in alternate_mesh.polygons
]
alternate_seam_count = sum(edge.use_seam for edge in alternate_mesh.edges)
alternate_island_count = count_uv_islands(alternate_uv)
bpy.data.objects.remove(alternate_study, do_unlink=True)
if alternate_mesh.users == 0:
    bpy.data.meshes.remove(alternate_mesh)

smart_study = building.copy()
smart_study.data = building.data.copy()
smart_study.name = "P10_SmartUV_Comparison"
bpy.context.scene.collection.objects.link(smart_study)
smart_study.data.uv_layers.active_index = smart_study.data.uv_layers.find("UVMap")
bpy.ops.object.select_all(action="DESELECT")
smart_study.select_set(True)
bpy.context.view_layer.objects.active = smart_study
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
smart_started = time.perf_counter()
bpy.ops.uv.smart_project(island_margin=0.006)
bpy.ops.object.mode_set(mode="OBJECT")
smart_seconds = time.perf_counter() - smart_started
smart_uv = smart_study.data.uv_layers.active
smart_uv_polygons = [
    [[smart_study.data.loops[index].vertex_index,
      float(smart_uv.data[index].uv.x),
      float(smart_uv.data[index].uv.y)]
     for index in range(poly.loop_start, poly.loop_start + poly.loop_total)]
    for poly in smart_study.data.polygons
]
smart_island_count = count_uv_islands(smart_uv_polygons)
smart_mesh = smart_study.data
bpy.data.objects.remove(smart_study, do_unlink=True)
if smart_mesh.users == 0:
    bpy.data.meshes.remove(smart_mesh)

# Export seam strategy and Smart UV comparison data for the documented evidence sheet.
uv_payload["smart_uv"] = smart_uv_polygons
uv_payload["alternate_uv"] = alternate_uv
uv_payload["alternate_seam_count"] = alternate_seam_count
uv_payload["alternate_island_count"] = alternate_island_count
uv_payload["smart_uv_component_count"] = smart_island_count
uv_payload["manual_uv_component_count"] = count_uv_islands(final_uv)
uv_payload["manual_uv_seconds"] = round(manual_seconds, 4)
uv_payload["alternate_uv_seconds"] = round(alternate_seconds, 4)
uv_payload["smart_uv_seconds"] = round(smart_seconds, 4)
with open(UV_DATA_OUTPUT, "w", encoding="utf-8") as uv_file:
    json.dump(uv_payload, uv_file)

for temporary_material in (
    clay,
    checker,
    solid_base,
    roughness_low,
    roughness_high,
    metallic_zero,
    metallic_one,
    normal_test,
    emission_low,
    emission_high,
):
    if temporary_material.users == 0:
        bpy.data.materials.remove(temporary_material)

for material in bpy.data.materials:
    ensure_uv_mapping_for_image_textures(material)

# Restore explicit production UV. The source scene already has all file images packed.
mesh.uv_layers.active_index = mesh.uv_layers.find(production_uv_name)
mesh.uv_layers.active_render_index = mesh.uv_layers.find(production_uv_name)
unpacked_images = [
    image.name for image in bpy.data.images
    if image.source == "FILE" and image.packed_file is None
]
if unpacked_images:
    raise RuntimeError(f"Unpacked image resources remain in the delivery scene: {unpacked_images}")
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUTPUT)

print(
    "P10 UV/PBR package prepared:",
    f"topology={topology}",
    f"marked_seams={len(seam_edges)}",
    f"uv_layers={[layer.name for layer in mesh.uv_layers]}",
    f"blend={BLEND_OUTPUT}",
)
