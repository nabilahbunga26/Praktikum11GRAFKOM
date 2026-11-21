import json
import os
import random

from PIL import Image, ImageDraw, ImageFont


ROOT = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(ROOT, "screenshots")
TEXTURE_DIR = os.path.join(ROOT, "textures", "School_Building")
DATA_FILE = os.path.join(ROOT, "uv_layout_data.json")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

with open(DATA_FILE, encoding="utf-8") as data_file:
    data = json.load(data_file)

WIDTH = 1600
PADDING = 150
TILE = WIDTH - 2 * PADDING


def font(size, bold=False):
    options = [
        r"C:\Windows\Fonts\segoeui.ttf" if not bold else r"C:\Windows\Fonts\seguisb.ttf",
        r"C:\Windows\Fonts\arial.ttf" if not bold else r"C:\Windows\Fonts\arialbd.ttf",
    ]
    for path in options:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def uv_point(uv):
    return (
        round(PADDING + uv[0] * TILE),
        round(PADDING + (1.0 - uv[1]) * TILE),
    )


def draw_uv_layout(key, filename, title, show_seams=True):
    image = Image.new("RGB", (WIDTH, WIDTH), "#101820")
    draw = ImageDraw.Draw(image)
    draw.text((PADDING, 42), title, fill="#F2F5F7", font=font(42, True))
    seam_summary = (
        f"{data['seam_edge_count']} marked seams"
        if show_seams
        else (
            f"{data['alternate_seam_count']} marked seams"
            if key == "alternate_uv"
            else "automatic UV cuts"
        )
    )
    draw.text(
        (PADDING, 96),
        f"SCH_Building | {data['topology']['faces']} faces | "
        f"{seam_summary} | UV 0–1",
        fill="#AEBCC8",
        font=font(23),
    )
    draw.rectangle(
        (PADDING, PADDING, PADDING + TILE, PADDING + TILE),
        fill="#263544",
        outline="#D4DDE4",
        width=4,
    )
    for fraction in (0.25, 0.5, 0.75):
        x = PADDING + round(TILE * fraction)
        y = PADDING + round(TILE * fraction)
        draw.line((x, PADDING, x, PADDING + TILE), fill="#526475", width=1)
        draw.line((PADDING, y, PADDING + TILE, y), fill="#526475", width=1)
    palette = ["#6CA6C1", "#83B692", "#D7A65A", "#AD91C8", "#D98272"]
    random.seed(23)
    for polygon in data[key]:
        points = [uv_point((uv[1], uv[2])) for uv in polygon]
        if len(points) < 3:
            continue
        fill = random.choice(palette)
        draw.polygon(points, fill=fill, outline="#1B2833")
    if show_seams:
        seam_set = {tuple(sorted(edge)) for edge in data["seam_edges"]}
        for polygon in data[key]:
            for index, start in enumerate(polygon):
                end = polygon[(index + 1) % len(polygon)]
                if tuple(sorted((start[0], end[0]))) in seam_set:
                    draw.line(
                        (uv_point((start[1], start[2])), uv_point((end[1], end[2]))),
                        fill="#F54A45",
                        width=3,
                    )
    draw.text(
        (PADDING, PADDING + TILE + 24),
        "Merah = seam | Grid = skala UV | Warna = island"
        if show_seams
        else "Grid = skala UV | Warna = island",
        fill="#F2F5F7",
        font=font(24),
    )
    image.save(os.path.join(SCREENSHOT_DIR, filename), quality=95)


draw_uv_layout("initial_uv", "03_initial_unwrap.png", "Initial Conformal Unwrap")
draw_uv_layout("final_uv", "05_final_uv_layout.png", "Final UV Layout — Average Scale + Pack")
draw_uv_layout(
    "alternate_uv",
    "16_alternate_seam_strategy.png",
    "Alternate Manual Seam Strategy — Open Boundaries Only",
    show_seams=False,
)
draw_uv_layout(
    "smart_uv",
    "17_smart_uv_project.png",
    "Smart UV Project — Automatic Comparison",
    show_seams=False,
)

def create_unwrap_comparison():
    entries = [
        (
            "Boundary-only seams",
            "16_alternate_seam_strategy.png",
            data["alternate_island_count"],
            data["alternate_uv_seconds"],
        ),
        (
            "Hard-edge + boundary seams",
            "05_final_uv_layout.png",
            data["manual_uv_component_count"],
            data["manual_uv_seconds"],
        ),
        (
            "Smart UV Project",
            "17_smart_uv_project.png",
            data["smart_uv_component_count"],
            data["smart_uv_seconds"],
        ),
    ]
    canvas = Image.new("RGB", (1700, 720), "#101820")
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 32), "Unwrap and Seam Strategy Comparison", fill="#F2F5F7", font=font(40, True))
    for index, (label, filename, count, elapsed) in enumerate(entries):
        x = 70 + index * 540
        draw.text(
            (x, 95),
            f"{label}\n{count} UV islands | {elapsed:.3f}s",
            fill="#E8EDF2",
            font=font(21, True),
        )
        source = Image.open(os.path.join(SCREENSHOT_DIR, filename)).convert("RGB")
        source.thumbnail((500, 530), Image.Resampling.LANCZOS)
        canvas.paste(source, (x, 165))
    canvas.save(os.path.join(SCREENSHOT_DIR, "14_unwrap_seam_comparison.png"))


def create_experiment_sheet():
    experiments = [
        ("Base Color: solid → map", ("15_basecolor_solid.png", "10_final_material.png")),
        ("Roughness: 0.1 → 0.9", ("16_roughness_0_1.png", "17_roughness_0_9.png")),
        ("Metallic: 0 → 1", ("18_metallic_0.png", "19_metallic_1.png")),
        ("Normal Map: OFF → ON", ("08_normal_off.png", "09_normal_on.png")),
        ("Normal strength: 0.2 → 1.5", ("20_normal_strength_low.png", "21_normal_strength_high.png")),
        ("Roughness map: sRGB → Non-Color", ("22_roughness_srgb_test.png", "23_roughness_noncolor_test.png")),
        ("Emission strength: 0.2 → 5.0", ("24_emission_low.png", "25_emission_high.png")),
        ("Checker: regular → stretched UV", ("04_checker_test.png", "14_checker_stretched.png")),
    ]
    canvas = Image.new("RGB", (1600, 8 * 380 + 100), "#101820")
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 28), "Required PBR and UV Experiments", fill="#F2F5F7", font=font(40, True))
    for row, (title, files) in enumerate(experiments):
        y = 90 + row * 380
        draw.text((60, y), title, fill="#E8EDF2", font=font(23, True))
        for column, filename in enumerate(files):
            source = Image.open(os.path.join(SCREENSHOT_DIR, filename)).convert("RGB")
            source.thumbnail((700, 330), Image.Resampling.LANCZOS)
            canvas.paste(source, (60 + column * 750, y + 42))
    canvas.save(os.path.join(SCREENSHOT_DIR, "15_required_experiments.png"))


create_unwrap_comparison()
create_experiment_sheet()


def fit_image(image, size):
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    return image


def create_map_sheet():
    entries = [
        ("Base Color · sRGB", "School_BaseColor.png"),
        ("Roughness · Non-Color", "School_Roughness.png"),
        ("Metallic · Non-Color", "School_Metallic.png"),
        ("Normal · Non-Color", "School_Normal.png"),
        ("Emission · sRGB", "School_Emission.png"),
    ]
    canvas = Image.new("RGB", (1600, 850), "#101820")
    draw = ImageDraw.Draw(canvas)
    draw.text((70, 38), "School PBR Texture Maps", fill="#F2F5F7", font=font(42, True))
    cell_w, cell_h = 470, 340
    positions = [(70, 130), (565, 130), (1060, 130), (315, 490), (810, 490)]
    for (label, filename), (x, y) in zip(entries, positions):
        source = Image.open(os.path.join(TEXTURE_DIR, filename))
        preview = fit_image(source, (cell_w, cell_h - 60))
        canvas.paste(preview, (x, y + 48))
        draw.text((x, y), label, fill="#E8EDF2", font=font(24, True))
        draw.text((x, y + cell_h - 6), filename, fill="#AEBCC8", font=font(16))
    canvas.save(os.path.join(SCREENSHOT_DIR, "07_pbr_texture_maps.png"))


def create_node_graph():
    width, height = 1900, 1180
    canvas = Image.new("RGB", (width, height), "#1B2028")
    draw = ImageDraw.Draw(canvas)
    draw.text((70, 42), "MAT_School_Building — PBR Node Graph", fill="#F2F5F7", font=font(42, True))
    draw.text((70, 100), "Verified from the delivered Blender material node links", fill="#AEBCC8", font=font(22))

    boxes = {
        "UV Map\nUVMap": (80, 450, 340, 620, "#36485B"),
        "Base Color\nsRGB": (470, 170, 770, 300, "#785C32"),
        "Roughness\nNon-Color": (470, 350, 770, 480, "#5A626B"),
        "Metallic\nNon-Color": (470, 530, 770, 660, "#5A626B"),
        "Normal\nNon-Color": (470, 710, 770, 840, "#5A626B"),
        "Emission Mask\nsRGB": (470, 900, 770, 1030, "#785C32"),
        "Normal Map\nTangent": (900, 710, 1190, 840, "#596A7C"),
        "Principled BSDF": (1320, 400, 1630, 760, "#45684D"),
        "Material Output": (1690, 500, 1860, 650, "#65527C"),
    }

    def center(name, side="right"):
        x1, y1, x2, y2, _ = boxes[name]
        return (x2 if side == "right" else x1, (y1 + y2) // 2)

    wire_pairs = [
        ("UV Map\nUVMap", "Base Color\nsRGB"),
        ("UV Map\nUVMap", "Roughness\nNon-Color"),
        ("UV Map\nUVMap", "Metallic\nNon-Color"),
        ("UV Map\nUVMap", "Normal\nNon-Color"),
        ("UV Map\nUVMap", "Emission Mask\nsRGB"),
    ]
    for source, target in wire_pairs:
        x1, y1 = center(source)
        x2, y2 = center(target, "left")
        draw.line((x1, y1, x2, y2), fill="#A8B9C9", width=5)

    direct_connections = [
        ("Base Color\nsRGB", "Principled BSDF", 448),
        ("Roughness\nNon-Color", "Principled BSDF", 520),
        ("Metallic\nNon-Color", "Principled BSDF", 585),
        ("Emission Mask\nsRGB", "Principled BSDF", 708),
    ]
    for source, target, target_y in direct_connections:
        x1, y1 = center(source)
        x2, _ = center(target, "left")
        draw.line((x1, y1, x2, target_y), fill="#A8B9C9", width=5)
    x1, y1 = center("Normal\nNon-Color")
    x2, y2 = center("Normal Map\nTangent", "left")
    draw.line((x1, y1, x2, y2), fill="#A8B9C9", width=5)
    x1, y1 = center("Normal Map\nTangent")
    x2, _ = center("Principled BSDF", "left")
    draw.line((x1, y1, x2, 650), fill="#A8B9C9", width=5)
    x1, y1 = center("Principled BSDF")
    x2, y2 = center("Material Output", "left")
    draw.line((x1, y1, x2, y2), fill="#A8B9C9", width=5)

    for label, (x1, y1, x2, y2, color) in boxes.items():
        draw.rounded_rectangle((x1, y1, x2, y2), radius=18, fill=color, outline="#CAD5DF", width=3)
        lines = label.split("\n")
        line_height = 34
        total_height = line_height * len(lines)
        y = (y1 + y2 - total_height) // 2
        for line in lines:
            bounds = draw.textbbox((0, 0), line, font=font(24, True))
            draw.text(((x1 + x2 - (bounds[2] - bounds[0])) // 2, y), line, fill="#FFFFFF", font=font(24, True))
            y += line_height
    draw.text((80, 1090), "All maps use the production UVMap. Normal passes through a Tangent Normal Map node.", fill="#C5D0DA", font=font(22))
    canvas.save(os.path.join(SCREENSHOT_DIR, "06_principled_node_graph.png"))


create_map_sheet()
create_node_graph()

print("Evidence images created in", SCREENSHOT_DIR)
