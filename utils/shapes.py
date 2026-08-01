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
    # Classic 2D heart outline (parametric heart curve), then extrude/taper into 3D
    t = np.linspace(0, 2 * np.pi, 80)
    outline_x = 16 * np.sin(t) ** 3
    outline_y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)

    depth = np.linspace(-1, 1, 40)
    T, D = np.meshgrid(t, depth)

    taper = 1 - 0.65 * np.abs(D) ** 1.3  # pinches front/back toward a rounded taper

    X = (16 * np.sin(T) ** 3) * taper
    Y = (13 * np.cos(T) - 5 * np.cos(2 * T) - 2 * np.cos(3 * T) - np.cos(4 * T)) * taper
    Z = D * 14

    x, y, z = _normalize(X, Z, Y)  # reorient so the point aims downward
    return x, y, z


def heart_landmarks_v2():
    """Labeled points with short functional descriptions for hover display."""
    return [
        {
            "name": "Aorta",
            "x": 0.1, "y": 0.3, "z": 1.6,
            "desc": "Carries oxygen-rich blood from the heart to the entire body.",
        },
        {
            "name": "Pulmonary artery",
            "x": -0.6, "y": 0.3, "z": 1.3,
            "desc": "Carries deoxygenated blood from the right ventricle to the lungs.",
        },
        {
            "name": "Superior vena cava",
            "x": 0.75, "y": 0.1, "z": 1.4,
            "desc": "Returns deoxygenated blood from the upper body into the right atrium.",
        },
        {
            "name": "Inferior vena cava",
            "x": 0.6, "y": -0.3, "z": -1.3,
            "desc": "Returns deoxygenated blood from the lower body into the right atrium.",
        },
        {
            "name": "Left ventricle",
            "x": -0.65, "y": -0.5, "z": -0.6,
            "desc": "Pumps oxygenated blood into the aorta and out to the body.",
        },
        {
            "name": "Right ventricle",
            "x": 0.65, "y": -0.5, "z": -0.55,
            "desc": "Pumps deoxygenated blood into the pulmonary artery toward the lungs.",
        },
        {
            "name": "Left atrium",
            "x": -0.7, "y": -0.4, "z": 0.6,
            "desc": "Receives oxygenated blood returning from the lungs.",
        },
        {
            "name": "Right atrium",
            "x": 0.7, "y": -0.4, "z": 0.5,
            "desc": "Receives deoxygenated blood returning from the body.",
        },
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

def real_heart_landmarks():
    """Labeled points positioned on the actual NIH heart mesh, confirmed by hovering."""
    return [
        {
            "name": "Aorta",
            "x": 0.0198, "y": 0.2868, "z": -0.0515,
            "desc": "Carries oxygen-rich blood from the heart to the entire body.",
        },
        {
            "name": "Pulmonary artery",
            "x": -0.0220, "y": 0.2803, "z": -0.2348,
            "desc": "Carries deoxygenated blood from the right ventricle to the lungs.",
        },
        {
            "name": "Pulmonary veins",
            "x": -0.1100, "y": 0.1023, "z": -0.2024,
            "desc": "Carry oxygenated blood from the lungs into the left atrium.",
        },
        {
            "name": "Superior vena cava",
            "x": 0.0793, "y": 0.3428, "z": 0.1447,
            "desc": "Returns deoxygenated blood from the upper body into the right atrium.",
        },
        {
            "name": "Inferior vena cava",
            "x": 0.0771, "y": -0.4078, "z": 0.1758,
            "desc": "Returns deoxygenated blood from the lower body into the right atrium.",
        },
        {
            "name": "Right atrium",
            "x": 0.1808, "y": 0.0458, "z": 0.1358,
            "desc": "Receives deoxygenated blood returning from the body.",
        },
        {
            "name": "Left atrium",
            "x": 0.0249, "y": 0.0791, "z": -0.1813,
            "desc": "Receives oxygenated blood returning from the lungs.",
        },
        {
            "name": "Right ventricle",
            "x": 0.2355, "y": -0.2555, "z": -0.0514,
            "desc": "Pumps deoxygenated blood into the pulmonary artery toward the lungs.",
        },
        {
            "name": "Left ventricle",
            "x": 0.0943, "y": -0.2439, "z": -0.3079,
            "desc": "Pumps oxygenated blood into the aorta and out to the body.",
        },
    ]

def real_brain_landmarks():
    """Labeled points on the brain mesh, confirmed by hovering."""
    return [
        {
            "name": "Cerebral cortex",
            "x": 0.1497, "y": 0.4811, "z": 0.0642,
            "desc": "The outer layer of the cerebrum; processes sensory information, motor commands, and higher cognitive functions.",
        },
        {
            "name": "Frontal lobe",
            "x": 0.1860, "y": 0.1285, "z": 0.7256,
            "desc": "Governs motor control, executive function, planning, and personality.",
        },
        {
            "name": "Parietal lobe",
            "x": 0.2945, "y": 0.4166, "z": -0.1870,
            "desc": "Processes somatosensory information and spatial awareness.",
        },
        {
            "name": "Occipital lobe",
            "x": 0.3626, "y": 0.0823, "z": -0.4955,
            "desc": "Primary center for visual processing.",
        },
        {
            "name": "Temporal lobe",
            "x": 0.3528, "y": -0.2236, "z": 0.3818,
            "desc": "Processes auditory information, and supports memory and language comprehension.",
        },
        {
            "name": "Thalamus",
            "x": 0.4750, "y": 0.0690, "z": 0.1424,
            "desc": "Relays and filters nearly all sensory information (except smell) on its way to the cortex.",
        },
        {
            "name": "Cerebellum",
            "x": 0.2574, "y": -0.3233, "z": -0.4374,
            "desc": "Coordinates fine motor control, balance, posture, and motor learning.",
        },
        {
            "name": "Brainstem",
            "x": 0.0735, "y": -0.4040, "z": 0.0075,
            "desc": "Connects the brain to the spinal cord; controls vital functions like breathing, heart rate, and consciousness.",
        },
        {
            "name": "Medulla oblongata",
            "x": 0.1055, "y": -0.6567, "z": -0.2988,
            "desc": "The lowest part of the brainstem; regulates breathing, heart rate, and blood pressure.",
        }
    ]

def real_lungs_landmarks():
    """Labeled points on the lungs mesh, confirmed by hovering."""
    return [
        {
            "name": "Trachea",
            "x": -0.0398, "y": -0.7083, "z": 0.2889,
            "desc": "The windpipe; carries air between the larynx and the bronchi, held open by C-shaped cartilage rings.",
        },
        {
            "name": "Superior lobe",
            "x": -0.4025, "y": -0.4540, "z": 0.1480,
            "desc": "The upper lobe of the lung, one of the segments divided by the lung's fissures.",
        },
        {
            "name": "Right lung",
            "x": 0.4916, "y": -0.0851, "z": 0.3978,
            "desc": "Has three lobes; slightly larger than the left lung, which yields space to accommodate the heart.",
        },
        {
            "name": "Left lung",
            "x": -0.5643, "y": -0.1069, "z": 0.3674,
            "desc": "Has two lobes; smaller than the right lung due to the cardiac notch accommodating the heart.",
        },
        {
            "name": "Cardiac notch",
            "x": -0.0712, "y": 0.0291, "z": 0.4846,
            "desc": "An indentation in the left lung's anterior border that accommodates the heart.",
        },
    ]