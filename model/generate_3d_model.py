"""Build the site viewer and OBJ from the canonical, exported Option F scene."""

import json
from pathlib import Path

import trimesh

ROOT = Path(__file__).resolve().parent


def main():
    data = json.loads((ROOT / "adu-option-f-scene.json").read_text())
    scene = trimesh.Scene()
    for part in data["parts"]:
        if part["category"] == "Room zone":
            continue
        mesh = trimesh.Trimesh(vertices=part["vertices"], faces=part["faces"], process=False)
        mesh.apply_translation([5, 20, 0])
        scene.add_geometry(mesh, node_name=part["name"])
    context = [
        ("Existing house approximate", [99, 22.5, 5], [48, 27, 10], "#bdb8ab"),
        ("Existing deck", [70.5, 16.5, 0.7], [9, 15, 1.4], "#b49c7e"),
        ("Replacement shed", [17, 8, 3.5], [18, 6, 7], "#b8b9ac"),
        ("Lot", [74, 22.5, -0.3], [148, 45, 0.4], "#b6bea1"),
        ("Alley", [-7, 22.5, -0.3], [14, 65, 0.3], "#b5b1a6"),
    ]
    data["context"] = []
    for name, center, size, color in context:
        mesh = trimesh.creation.box(extents=size)
        mesh.apply_translation(center)
        scene.add_geometry(mesh, node_name=name)
        data["context"].append(dict(name=name, center=center, size=size, color=color))
    # Approximate existing-house and shed gables; no field-verified height claim.
    for name, x0, x1, y0, y1, eave, ridge in (
        ("Existing house roof", 75, 123, 9, 36, 10, 20),
        ("Replacement shed roof", 8, 26, 5, 11, 7, 9.5),
    ):
        vertices = [
            [x, y, z] for x in (x0, x1) for y, z in ((y0, eave), ((y0 + y1) / 2, ridge), (y1, eave))
        ]
        faces = [
            [0, 2, 1],
            [3, 4, 5],
            [0, 1, 4],
            [0, 4, 3],
            [1, 2, 5],
            [1, 5, 4],
            [0, 3, 5],
            [0, 5, 2],
        ]
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        scene.add_geometry(mesh, node_name=name)
        data["context"].append(dict(name=name, vertices=vertices, faces=faces, color="#8e9183"))
    scene.export(ROOT / "site-model.obj")
    template = (ROOT / "viewer-template.html").read_text()
    (ROOT / "site-model-3d.html").write_text(
        template.replace("__SCENE_DATA__", json.dumps(data, separators=(",", ":")))
    )
    print(f"Site viewer: {len(data['parts'])} canonical parts; OBJ in feet, Z up")


if __name__ == "__main__":
    main()
