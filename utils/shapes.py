# utils/shapes.py

import numpy as np


def heart_shape():
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 60)
    U, V = np.meshgrid(u, v)

    x = np.sin(V) * (15 * np.sin(U) - 4 * np.sin(3 * U))
    y = np.sin(V) * (15 * np.cos(U) - 5 * np.cos(2 * U) - 2 * np.cos(3 * U) - np.cos(4 * U))
    z = 8 * np.cos(V) * 6

    return _normalize(x, y, z)


def lung_shape():
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 60)
    U, V = np.meshgrid(u, v)

    # Two elongated lobes, roughly lung-like
    x = np.sin(V) * np.cos(U) * 0.6
    y = np.sin(V) * np.sin(U) * 1.4
    z = np.cos(V) * 1.2

    return _normalize(x, y, z)


def generic_organ_shape():
    u = np.linspace(0, 2 * np.pi, 40)
    v = np.linspace(0, np.pi, 40)
    U, V = np.meshgrid(u, v)

    x = np.cos(U) * np.sin(V)
    y = np.sin(U) * np.sin(V) * 0.85
    z = np.cos(V) * 1.1

    return _normalize(x, y, z)


def _normalize(x, y, z):
    x = x / np.abs(x).max()
    y = y / np.abs(y).max()
    z = z / np.abs(z).max()
    return x, y, z


# Maps each organ system key to its shape function and display color
SHAPE_REGISTRY = {
    "cardiovascular": {"shape_fn": heart_shape, "color": "Reds"},
    "respiratory": {"shape_fn": lung_shape, "color": "Blues"},
}


def get_shape_for_system(key: str):
    entry = SHAPE_REGISTRY.get(key, {"shape_fn": generic_organ_shape, "color": "Purples"})
    x, y, z = entry["shape_fn"]()
    return x, y, z, entry["color"]

def anatomical_heart():
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 60)
    U, V = np.meshgrid(u, v)

    # Rounder, more compact heart silhouette than the previous version
    r = 1 - 0.35 * np.cos(V)
    x = r * np.sin(V) * np.cos(U) * 0.85
    y = r * np.sin(V) * np.sin(U)
    z = np.cos(V) * 1.15 - 0.25 * np.sin(V) ** 4

    x, y, z = _normalize(x, y, z)
    return x, y, z


def heart_landmarks():
    # Approximate label positions on the normalized heart surface
    return [
        {"name": "Left ventricle", "x": -0.35, "y": 0.1, "z": -0.55},
        {"name": "Right ventricle", "x": 0.35, "y": 0.1, "z": -0.5},
        {"name": "Left atrium", "x": -0.4, "y": 0.15, "z": 0.55},
        {"name": "Right atrium", "x": 0.4, "y": 0.15, "z": 0.5},
        {"name": "Aorta", "x": 0.0, "y": 0.2, "z": 0.9},
    ]

def _cylinder(start, end, radius, n=20):
    """Builds a simple 3D tube mesh between two points — used for vessels."""
    start = np.array(start)
    end = np.array(end)
    axis = end - start
    length = np.linalg.norm(axis)
    axis_norm = axis / length

    not_parallel = np.array([1, 0, 0]) if abs(axis_norm[0]) < 0.9 else np.array([0, 1, 0])
    perp1 = np.cross(axis_norm, not_parallel)
    perp1 /= np.linalg.norm(perp1)
    perp2 = np.cross(axis_norm, perp1)

    t = np.linspace(0, length, 2)
    theta = np.linspace(0, 2 * np.pi, n)
    t, theta = np.meshgrid(t, theta)

    x = start[0] + axis_norm[0] * t + radius * (perp1[0] * np.cos(theta) + perp2[0] * np.sin(theta))
    y = start[1] + axis_norm[1] * t + radius * (perp1[1] * np.cos(theta) + perp2[1] * np.sin(theta))
    z = start[2] + axis_norm[2] * t + radius * (perp1[2] * np.cos(theta) + perp2[2] * np.sin(theta))

    return x, y, z


def heart_vessels():
    """
    Returns a list of vessel definitions: each with its 3D tube coordinates,
    a color (matching standard oxygenated/deoxygenated convention), and a label.
    Positioned relative to the normalized heart body (roughly -1 to 1 on each axis).
    """
    vessels = [
        {
            "name": "Aorta",
            "color": "#C23B3B",
            "start": (0.05, 0.15, 0.75),
            "end": (0.05, 0.15, 1.35),
            "radius": 0.14,
        },
        {
            "name": "Pulmonary artery",
            "color": "#3B6FC2",
            "start": (-0.15, 0.15, 0.7),
            "end": (-0.15, 0.15, 1.25),
            "radius": 0.12,
        },
        {
            "name": "Superior vena cava",
            "color": "#3B6FC2",
            "start": (0.4, 0.1, 0.7),
            "end": (0.4, 0.1, 1.3),
            "radius": 0.11,
        },
        {
            "name": "Inferior vena cava",
            "color": "#3B6FC2",
            "start": (0.35, -0.1, -0.6),
            "end": (0.35, -0.1, -1.1),
            "radius": 0.11,
        },
    ]

    for v in vessels:
        x, y, z = _cylinder(v["start"], v["end"], v["radius"])
        v["x"], v["y"], v["z"] = x, y, z

    return vessels


def heart_landmarks_v2():
    """Labeled points with short functional descriptions for hover display."""
    return [
        {
            "name": "Aorta",
            "x": 0.05, "y": 0.15, "z": 1.35,
            "desc": "Carries oxygen-rich blood from the heart to the entire body.",
        },
        {
            "name": "Pulmonary artery",
            "x": -0.15, "y": 0.15, "z": 1.25,
            "desc": "Carries deoxygenated blood from the right ventricle to the lungs.",
        },
        {
            "name": "Superior vena cava",
            "x": 0.4, "y": 0.1, "z": 1.3,
            "desc": "Returns deoxygenated blood from the upper body into the right atrium.",
        },
        {
            "name": "Inferior vena cava",
            "x": 0.35, "y": -0.1, "z": -1.1,
            "desc": "Returns deoxygenated blood from the lower body into the right atrium.",
        },
        {
            "name": "Left ventricle",
            "x": -0.35, "y": 0.1, "z": -0.55,
            "desc": "Pumps oxygenated blood into the aorta and out to the body.",
        },
        {
            "name": "Right ventricle",
            "x": 0.35, "y": 0.1, "z": -0.5,
            "desc": "Pumps deoxygenated blood into the pulmonary artery toward the lungs.",
        },
        {
            "name": "Left atrium",
            "x": -0.4, "y": 0.15, "z": 0.55,
            "desc": "Receives oxygenated blood returning from the lungs.",
        },
        {
            "name": "Right atrium",
            "x": 0.4, "y": 0.15, "z": 0.5,
            "desc": "Receives deoxygenated blood returning from the body.",
        },
    ]