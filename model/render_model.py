"""Render coordinated architectural studies from the exported Option F scene.

Run with Blender (no pip dependencies)::
    blender --background --python model/render_model.py -- --views yard alley upper lower

The building and furniture come exclusively from adu-option-f-scene.json. This
script adds only presentation materials, lighting, ground and a sparse planting
context. Cutaways clip architectural parts at three feet above the selected
floor; selected-floor furniture remains full height. Earlier concept images
are retained, never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

import bmesh  # ty: ignore[unresolved-import]
import bpy  # ty: ignore[unresolved-import]
from mathutils import Vector  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
NAMES = {
    "yard": "option-f-yard-model.png",
    "alley": "option-f-alley-model.png",
    "upper": "option-f-upper-cutaway.png",
    "lower": "option-f-lower-cutaway.png",
}
MATERIALS = {}


def material(name, rgb, roughness=0.65, grain=False, glass=False):
    key = (name, tuple(rgb), roughness, grain, glass)
    if key in MATERIALS:
        return MATERIALS[key]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    linear_rgb = tuple(
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in rgb[:3]
    )
    shader.inputs["Base Color"].default_value = (*linear_rgb, 1)
    if name == "Warm paper":
        shader.inputs["Emission Color"].default_value = (*linear_rgb, 1)
        shader.inputs["Emission Strength"].default_value = 0.35
    shader.inputs["Roughness"].default_value = roughness
    if glass:
        shader.inputs["Transmission Weight"].default_value = 0.64
        shader.inputs["IOR"].default_value = 1.45
        shader.inputs["Roughness"].default_value = 0.16
    elif grain:
        nodes = mat.node_tree.nodes
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 7
        noise.inputs["Detail"].default_value = 2
        mapping = nodes.new("ShaderNodeVectorMath")
        mapping.operation = "MULTIPLY"
        mapping.inputs[1].default_value = (1, 24, 3)
        coords = nodes.new("ShaderNodeTexCoord")
        mat.node_tree.links.new(coords.outputs["Generated"], mapping.inputs[0])
        mat.node_tree.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.14
        bump.inputs["Distance"].default_value = 0.018
        mat.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    else:
        noise = mat.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 90
        bump = mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.09
        bump.inputs["Distance"].default_value = 0.012
        mat.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    if name == "Muted sage siding":
        # Presentation-only double-teardrop approximation: two rounded 4-inch
        # profiles per nominal 8-inch repeat. World Z keeps courses aligned
        # across split wall pieces and gables. No product is specified.
        nodes = mat.node_tree.nodes
        geometry = nodes.new("ShaderNodeNewGeometry")
        separate = nodes.new("ShaderNodeSeparateXYZ")
        scale = nodes.new("ShaderNodeMath")
        scale.operation = "MULTIPLY"
        scale.inputs[1].default_value = 3
        repeat = nodes.new("ShaderNodeMath")
        repeat.operation = "FRACT"
        profile = nodes.new("ShaderNodeValToRGB")
        profile.color_ramp.interpolation = "EASE"
        profile.color_ramp.elements.remove(profile.color_ramp.elements[1])
        profile.color_ramp.elements[0].position = 0
        profile.color_ramp.elements[0].color = (0.05, 0.05, 0.05, 1)
        for position, value in ((0.12, 0.15), (0.60, 0.75), (0.90, 1.0), (0.985, 0.05)):
            element = profile.color_ramp.elements.new(position)
            element.color = (value, value, value, 1)
        siding = nodes.new("ShaderNodeBump")
        siding.inputs["Strength"].default_value = 0.5
        siding.inputs["Distance"].default_value = 0.018
        mat.node_tree.links.new(geometry.outputs["Position"], separate.inputs[0])
        mat.node_tree.links.new(separate.outputs["Z"], scale.inputs[0])
        mat.node_tree.links.new(scale.outputs[0], repeat.inputs[0])
        mat.node_tree.links.new(repeat.outputs[0], profile.inputs[0])
        mat.node_tree.links.new(profile.outputs[0], siding.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"], siding.inputs["Normal"])
        mat.node_tree.links.new(siding.outputs["Normal"], shader.inputs["Normal"])
    MATERIALS[key] = mat
    return mat


def part_material(part):
    name = part["name"].lower()
    category = part["category"].lower()
    rgba = part["color"]
    rgb = tuple(value / 255 if max(rgba) > 1 else value for value in rgba[:3])
    glass = category in ("glass", "glazing") or "glass" in name or "glazing" in name
    if category == "window" and not any(x in name for x in ("frame", "trim", "sill")):
        glass = True
    wood = any(word in name for word in ("wood", "cedar", "deck board", "tread", "table", "desk"))
    if "roof" in category:
        return material("Charcoal roof finish", (0.12, 0.145, 0.135), 0.46)
    if category == "exterior wall":
        return material("Muted sage siding", (0.43, 0.49, 0.37), 0.85)
    if category == "interior wall":
        return material("Warm ivory plaster", (0.83, 0.80, 0.71), 0.85)
    if category in ("trim", "guard", "post"):
        return material("Warm white painted timber", (0.83, 0.81, 0.72), 0.62)
    if category in ("deck", "exterior stair"):
        return material("Oiled cedar decking", (0.70, 0.52, 0.34), grain=True)
    if glass:
        return material("Clear glass", (0.61, 0.76, 0.77), glass=True)
    return material(part["category"] + " " + str(rgb), rgb, grain=wood)


def box(name, center, size, mat, rotation=0, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.rotation_euler.x = rotation
    obj.data.materials.append(mat)
    if bevel and min(size) > 0.03:
        modifier = obj.modifiers.new("Soft construction edges", "BEVEL")
        modifier.width = min(bevel, min(size) * 0.2)
        modifier.segments = 2
        obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return obj


def gable(part):
    x, y, z = part["center"]
    dx, dy, dz = part["size"]
    verts = []
    for xx in (x - dx / 2, x + dx / 2):
        verts.extend(
            ((xx, y - dy / 2, z - dz / 2), (xx, y + dy / 2, z - dz / 2), (xx, y, z + dz / 2))
        )
    mesh = bpy.data.meshes.new(part["name"])
    mesh.from_pydata(verts, [], ((0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)))
    mesh.update()
    obj = bpy.data.objects.new(part["name"], mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(part_material(part))


def exact_mesh(part):
    """Use exported triangles, including sloping rails, without interpretation."""
    mesh = bpy.data.meshes.new(part["name"])
    mesh.from_pydata(part["vertices"], [], part["faces"])
    mesh.update()
    if "_cutoff" in part:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        cut = bmesh.ops.bisect_plane(
            bm,
            geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
            plane_co=(0, 0, part["_cutoff"]),
            plane_no=(0, 0, 1),
            clear_outer=True,
            clear_inner=False,
        )
        edges = [edge for edge in cut["geom_cut"] if isinstance(edge, bmesh.types.BMEdge)]
        if edges:
            bmesh.ops.holes_fill(bm, edges=edges)
        bm.to_mesh(mesh)
        bm.free()
    obj = bpy.data.objects.new(part["name"], mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(part_material(part))
    if min(part["size"]) > 0.03:
        bevel = obj.modifiers.new("Soft construction edges", "BEVEL")
        bevel.width = min(0.025, min(part["size"]) * 0.2)
        bevel.segments = 2
        obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")


def build_parts(parts, view):
    cutaway = view in ("upper", "lower")
    floor = 9.25 if view == "upper" else 0.5
    cutoff = floor + 3
    for source in parts:
        part = dict(source)
        cat = part["category"].lower()
        if cat == "room zone":
            continue
        if view == "lower" and cat == "vehicle":
            continue
        level = str(part["level"]).lower()
        if cutaway:
            if "roof" in cat or part.get("shape") == "gable":
                continue
            if view == "upper" and level in ("level 1", "1", "ground"):
                continue
            if view == "lower" and level in ("level 2", "2", "upper"):
                continue
            center = list(part["center"])
            size = list(part["size"])
            bottom = center[2] - size[2] / 2
            top = center[2] + size[2] / 2
            is_furniture = "furniture" in cat or cat in ("fixture", "appliance", "vehicle")
            if not is_furniture:
                if bottom >= cutoff:
                    continue
                if top > cutoff:
                    part["_cutoff"] = cutoff
                    size[2] = cutoff - bottom
                    center[2] = bottom + size[2] / 2
            if view == "upper" and top < floor - 0.8:
                continue
            part["center"], part["size"] = center, size
        if "vertices" in part and "faces" in part:
            exact_mesh(part)
        elif part.get("shape") == "stairrail":
            dx, dy, dz = part["size"]
            obj = box(
                part["name"],
                part["center"],
                (math.hypot(dx, dz - 0.12), dy, 0.12),
                part_material(part),
            )
            obj.rotation_euler.y = -math.atan2(dz - 0.12, dx)
        elif part.get("shape") == "gable":
            gable(part)
        else:
            box(
                part["name"],
                part["center"],
                part["size"],
                part_material(part),
                part.get("rotate_x", 0),
            )


def environment(view):
    exterior = view in ("yard", "alley")
    z = -0.28 if exterior or view == "lower" else 8.17
    box(
        "Presentation ground",
        (12, 9, z - 0.5),
        (2000, 2000, 1),
        material("Warm paper", (0.95, 0.93, 0.88)),
        bevel=0,
    )
    if not exterior:
        return
    box(
        "Site study base",
        (13, 8, -0.23),
        (42, 39, 0.35),
        material("Limestone model base", (0.84, 0.81, 0.73)),
        bevel=0.15,
    )
    box(
        "Alley approach",
        (-4, 8, -0.039),
        (7.5, 27, 0.018),
        material("Alley gravel", (0.57, 0.57, 0.51)),
        bevel=0,
    )
    # Sparse context only. No implied site design, fencing or invented buildings.
    grass_mat = material("Low planting", (0.30, 0.36, 0.21), 0.9)
    rng = random.Random(24020)
    vertices, faces = [], []
    for _index in range(40):
        xx = rng.uniform(30.3, 32.5)
        yy = rng.uniform(-5, 24)
        for stem in range(4):
            height = rng.uniform(0.25, 0.6)
            first = len(vertices)
            for i in range(5):
                angle = i * math.tau / 5
                vertices.append(
                    (xx + stem * 0.07 + math.cos(angle) * 0.06, yy + math.sin(angle) * 0.06, 0)
                )
            vertices.append((xx + stem * 0.07, yy + rng.uniform(-0.15, 0.15), height))
            faces.extend((first + i, first + (i + 1) % 5, first + 5) for i in range(5))
    mesh = bpy.data.meshes.new("Sparse context grasses")
    mesh.from_pydata(vertices, [], faces)
    obj = bpy.data.objects.new("Sparse context grasses", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(grass_mat)


def camera(location, target, ortho=None, lens=50):
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.object
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    if ortho:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ortho
    bpy.context.scene.camera = cam


def lighting():
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()
    sky = nodes.new("ShaderNodeBackground")
    sky.inputs["Color"].default_value = (0.78, 0.83, 0.91, 1)
    sky.inputs["Strength"].default_value = 0.7
    backdrop = nodes.new("ShaderNodeBackground")
    backdrop.inputs["Color"].default_value = (3.0, 2.8, 2.5, 1)
    ray = nodes.new("ShaderNodeLightPath")
    mix = nodes.new("ShaderNodeMixShader")
    output = nodes.new("ShaderNodeOutputWorld")
    world.node_tree.links.new(ray.outputs["Is Camera Ray"], mix.inputs[0])
    world.node_tree.links.new(sky.outputs[0], mix.inputs[1])
    world.node_tree.links.new(backdrop.outputs[0], mix.inputs[2])
    world.node_tree.links.new(mix.outputs[0], output.inputs[0])
    bpy.ops.object.light_add(type="SUN", location=(40, -30, 50))
    sun = bpy.context.object
    sun.name = "Late morning daylight"
    sun.rotation_euler = (math.radians(25), math.radians(-30), math.radians(-28))
    sun.data.energy = 3.5
    sun.data.color = (1.0, 0.93, 0.83)
    sun.data.angle = math.radians(12)
    bpy.ops.object.light_add(type="AREA", location=(28, -22, 40))
    fill = bpy.context.object
    fill.name = "Soft sky"
    fill.data.energy = 1800
    fill.data.shape = "DISK"
    fill.data.size = 24
    fill.rotation_euler = (Vector((12, 10, 6)) - fill.location).to_track_quat("-Z", "Y").to_euler()


def render(parts, view, args):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    MATERIALS.clear()
    build_parts(parts, view)
    environment(view)
    lighting()
    if view == "yard":
        camera((58, -49, 19), (13.5, 8, 8.3), lens=52)
    elif view == "alley":
        camera((-46, -42, 20), (12, 8, 8.2), lens=50)
    elif view == "upper":
        camera((42, -36, 62), (13.2, 8, 9.7), ortho=47)
    else:
        camera((42, -36, 55), (12, 9, 0.8), ortho=45)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    if args.device != "cpu":
        try:
            preferences = bpy.context.preferences.addons["cycles"].preferences
            preferences.compute_device_type = "METAL"
            # Small stills finish faster without recompiling scene-specialized
            # GPU kernels for every camera/cutaway variation.
            preferences.kernel_optimization_level = "OFF"
            preferences.get_devices()
            gpu_devices = [device for device in preferences.devices if device.type == "METAL"]
            if gpu_devices:
                for device in preferences.devices:
                    device.use = device.type == "METAL"
                scene.cycles.device = "GPU"
                print(
                    "Using Metal GPU: " + ", ".join(device.name for device in gpu_devices),
                    flush=True,
                )
        except (TypeError, RuntimeError) as exc:
            print(f"Metal unavailable; using CPU: {exc}", flush=True)
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 6
    scene.cycles.transparent_max_bounces = 6
    scene.render.resolution_x = args.width
    scene.render.resolution_y = round(args.width * 2 / 3)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.filepath = str(args.output / NAMES[view])
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {view}: {scene.render.filepath}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", type=Path, default=ROOT / "model/adu-option-f-scene.json")
    parser.add_argument("--output", type=Path, default=ROOT / "renderings")
    parser.add_argument("--views", nargs="+", choices=NAMES, default=list(NAMES))
    parser.add_argument("--width", type=int, default=1800)
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--device", choices=("auto", "cpu"), default="auto")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    scene_bytes = args.scene.read_bytes()
    source_sha256 = hashlib.sha256(scene_bytes).hexdigest()
    renderer_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    data = json.loads(scene_bytes)
    if data["units"] != "feet":
        raise ValueError("Renderer expects feet and a Z-up coordinate system")
    args.output.mkdir(parents=True, exist_ok=True)
    for view in args.views:
        render(data["parts"], view, args)
    manifest_path = args.output / "model-render-manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for view in args.views:
        manifest[NAMES[view]] = {
            "scene": str(args.scene.relative_to(ROOT))
            if args.scene.is_relative_to(ROOT)
            else str(args.scene),
            "scene_sha256": source_sha256,
            "image_sha256": hashlib.sha256((args.output / NAMES[view]).read_bytes()).hexdigest(),
            "renderer_sha256": renderer_sha256,
            "scene_version": data.get("version"),
            "renderer": "Blender Cycles",
            "blender_version": bpy.app.version_string,
            "view": view,
            "width": args.width,
            "samples": args.samples,
            "cut_height_above_floor_ft": 3 if view in ("upper", "lower") else None,
            "vehicle_envelope_shown": view != "lower",
            "surface_study": "Approximate world-Z-aligned double-teardrop siding bump, 4-inch profiles; charcoal roof finish. Illustrative appearance, not a selected product or construction detail.",
            "note": "Geometry-derived schematic study. Context and surface finishes are illustrative.",
        }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
