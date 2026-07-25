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