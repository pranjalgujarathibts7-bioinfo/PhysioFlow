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

def real_kidney_landmarks():
    """Landmarks on the kidney/ureter system, hover-verified against the live mesh."""
    return [
        {
            "name": "Renal capsule",
            "x": -0.3298569, "y": 0.1085874, "z": -0.06496666,
            "desc": "The tough fibrous membrane surrounding the kidney, providing structural support and protection.",
        },
        {
            "name": "Renal cortex",
            "x": -0.3656081, "y": -0.09119027, "z": 0.06864327,
            "desc": "The outer layer of the kidney, containing renal corpuscles and convoluted tubules where filtration begins.",
        },
        {
            "name": "Renal medulla (pyramids)",
            "x": -0.2020144, "y": 0.1820211, "z": -0.006024464,
            "desc": "The inner region, organized into renal pyramids that carry out countercurrent multiplication to concentrate urine.",
        },
        {
            "name": "Renal calyces",
            "x": -0.2072306, "y": 0.0544777, "z": 0.0394329,
            "desc": "Cup-shaped structures that collect urine draining from the renal papillae before it reaches the pelvis.",
        },
        {
            "name": "Renal pelvis",
            "x": -0.2224933, "y": -0.03958525, "z": 0.08619565,
            "desc": "The funnel-shaped chamber, formed by convergence of the major calyces, that collects urine before it drains into the ureter.",
        },
        {
            "name": "Ureter",
            "x": -0.05804552, "y": -0.4381374, "z": 0.1927954,
            "desc": "A muscular tube that propels urine from the renal pelvis to the bladder via peristaltic contractions.",
        },
        {
            "name": "Left kidney",
            "x": 0.2800555, "y": 0.2316755, "z": -0.04531364,
            "desc": "The mirror-image partner of the right kidney; anatomically similar, positioned slightly higher due to the liver's position above the right kidney.",
        },
    ]

def _bezier_point(p0, p1, p2, t):
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def stomach_shape(esophagus_point, gastric_point, duodenal_point, n_u=40, n_v=24):
    """Stylized J-shaped stomach as a bent, tapering tube — placeholder until a real model exists."""
    p0 = np.array(esophagus_point, dtype=float)
    p1 = np.array(gastric_point, dtype=float)
    p2 = np.array(duodenal_point, dtype=float)

    t_vals = np.linspace(0, 1, n_u)
    theta = np.linspace(0, 2 * np.pi, n_v)
    centerline = np.array([_bezier_point(p0, p1, p2, t) for t in t_vals])

    # Fundus bulge near t=0.3, tapering toward esophagus and pylorus
    radius_profile = 0.035 + 0.16 * np.exp(-((t_vals - 0.3) ** 2) / 0.05)
    radius_profile = np.maximum(radius_profile, 0.03)

    tangents = np.gradient(centerline, axis=0)
    tangents = tangents / (np.linalg.norm(tangents, axis=1, keepdims=True) + 1e-9)

    # Parallel-transport frame so the tube doesn't twist/self-intersect at the bend
    perp1_list = np.zeros_like(tangents)
    not_parallel = np.array([1.0, 0.0, 0.0]) if abs(tangents[0][0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    perp1 = np.cross(tangents[0], not_parallel)
    perp1 /= np.linalg.norm(perp1) + 1e-9
    perp1_list[0] = perp1
    for i in range(1, n_u):
        p = perp1_list[i - 1] - tangents[i] * np.dot(perp1_list[i - 1], tangents[i])
        norm_p = np.linalg.norm(p)
        if norm_p < 1e-6:
            not_parallel = np.array([1.0, 0.0, 0.0]) if abs(tangents[i][0]) < 0.9 else np.array([0.0, 1.0, 0.0])
            p = np.cross(tangents[i], not_parallel)
            norm_p = np.linalg.norm(p)
        perp1_list[i] = p / (norm_p + 1e-9)

    X = np.zeros((n_v, n_u))
    Y = np.zeros((n_v, n_u))
    Z = np.zeros((n_v, n_u))

    for i in range(n_u):
        tangent = tangents[i]
        perp1 = perp1_list[i]
        perp2 = np.cross(tangent, perp1)
        r = radius_profile[i]
        for j, th in enumerate(theta):
            offset = r * (perp1 * np.cos(th) + perp2 * np.sin(th))
            X[j, i] = centerline[i][0] + offset[0]
            Y[j, i] = centerline[i][1] + offset[1]
            Z[j, i] = centerline[i][2] + offset[2]

    return X, Y, Z


def esophagus_shape(top_point, bottom_point, radius=0.015, n_u=20, n_v=16):
    """Stylized straight tube for the esophagus — placeholder until a real model exists."""
    p0 = np.array(top_point)
    p1 = np.array(bottom_point)
    t_vals = np.linspace(0, 1, n_u)
    theta = np.linspace(0, 2 * np.pi, n_v)
    centerline = np.array([p0 + (p1 - p0) * t for t in t_vals])

    tangent = (p1 - p0) / (np.linalg.norm(p1 - p0) + 1e-9)
    not_parallel = np.array([1, 0, 0]) if abs(tangent[0]) < 0.9 else np.array([0, 1, 0])
    perp1 = np.cross(tangent, not_parallel)
    perp1 /= np.linalg.norm(perp1) + 1e-9
    perp2 = np.cross(tangent, perp1)

    X = np.zeros((n_v, n_u))
    Y = np.zeros((n_v, n_u))
    Z = np.zeros((n_v, n_u))
    for i in range(n_u):
        for j, th in enumerate(theta):
            offset = radius * (perp1 * np.cos(th) + perp2 * np.sin(th))
            X[j, i] = centerline[i][0] + offset[0]
            Y[j, i] = centerline[i][1] + offset[1]
            Z[j, i] = centerline[i][2] + offset[2]

    return X, Y, Z

def real_digestive_landmarks():
    """Landmarks on the digestive system mesh, hover-verified against the live model."""
    return [
        {
            "name": "Esophagus",
            "x": 0.02602494, "y": 0.4977439, "z": 0.01609352,
            "desc": "A muscular tube that propels swallowed food from the pharynx to the stomach via peristalsis.",
        },
        {
            "name": "Stomach",
            "x": 0.06274217, "y": 0.1828009, "z": 0.2337087,
            "desc": "A muscular sac that churns food with acid and pepsin, beginning protein digestion before releasing chyme into the duodenum.",
        },
        {
            "name": "Liver",
            "x": -0.3790895, "y": 0.1826422, "z": 0.0181674,
            "desc": "Produces bile for fat digestion and performs metabolic functions including detoxification, protein synthesis, and glycogen storage.",
        },
        {
            "name": "Gallbladder",
            "x": -0.2687221, "y": 0.05459243, "z": 0.1905909,
            "desc": "Stores and concentrates bile produced by the liver, releasing it into the duodenum in response to fatty meals.",
        },
        {
            "name": "Pancreas",
            "x": -0.07452693, "y": -0.00324279, "z": -0.02351958,
            "desc": "Secretes digestive enzymes and bicarbonate into the duodenum, and produces insulin and glucagon to regulate blood glucose.",
        },
        {
            "name": "Duodenum",
            "x": -0.06926674, "y": -0.1322663, "z": 0.000165429,
            "desc": "The first segment of the small intestine, where bile and pancreatic secretions mix with chyme to continue digestion.",
        },
        {
            "name": "Jejunum",
            "x": 0.1544807, "y": -0.3483472, "z": 0.2015803,
            "desc": "The middle segment of the small intestine, specialized for the bulk of nutrient absorption via its dense folds and villi.",
        },
        {
            "name": "Ileum",
            "x": 0.01430657, "y": -0.590978, "z": 0.0994335,
            "desc": "The final segment of the small intestine, absorbing vitamin B12, bile salts, and remaining nutrients before the ileocecal valve.",
        },
        {
            "name": "Appendix",
            "x": -0.1624556, "y": -0.558902, "z": 0.01315333,
            "desc": "A small pouch attached to the cecum, thought to play a role in maintaining gut microbiota and immune function.",
        },
        {
            "name": "Rectum",
            "x": -0.04571894, "y": -0.9087155, "z": -0.1779365,
            "desc": "The final segment of the large intestine, storing feces before defecation.",
        },
    ]

def real_skeletal_landmarks():
    """Landmarks on the skeletal mesh, hover-verified against the live model."""
    return [
        {
            "name": "Thoracic vertebrae",
            "x": 0.1022963, "y": 0.1400789, "z": -0.1464814,
            "desc": "The 12 vertebrae of the mid-back, each articulating with a pair of ribs; less mobile than cervical or lumbar segments due to rib attachment.",
        },
        {
            "name": "Sternal (true) ribs",
            "x": -0.1913477, "y": 0.08983968, "z": -0.03020751,
            "desc": "Ribs 1–7, which attach directly to the sternum via their own costal cartilage, forming a protective cage around the thoracic organs.",
        },
        {
            "name": "Sacrum",
            "x": -0.01598447, "y": -0.2437884, "z": -0.04787241,
            "desc": "A triangular bone formed by the fusion of five sacral vertebrae, connecting the spine to the pelvis at the sacroiliac joints.",
        },
        {
            "name": "Femur",
            "x": 0.1127814, "y": -0.475416, "z": 0.01659458,
            "desc": "The longest and strongest bone in the body, extending from the hip joint to the knee and bearing the majority of body weight during standing and walking.",
        },
        {
            "name": "Tibia",
            "x": -0.1065793, "y": -0.5191864, "z": 0.01928211,
            "desc": "The larger of the two lower leg bones, bearing most of the body's weight between the knee and ankle.",
        },
        {
            "name": "Fibula",
            "x": -0.162269, "y": -0.7882907, "z": -0.03118167,
            "desc": "The slender lateral lower leg bone, providing muscle attachment and lateral ankle stability rather than significant weight-bearing.",
        },
        {
            "name": "Frontal bone",
            "x": -0.0647357, "y": 0.5745376, "z": 0.4783901,
            "desc": "Forms the forehead and the upper portion of the eye sockets, protecting the frontal lobes of the brain.",
        },
        {
            "name": "Nasal bone",
            "x": -0.003572581, "y": 0.7749136, "z": 0.07625819,
            "desc": "The small paired bones forming the bridge of the nose, connecting to cartilage that shapes the lower nose.",
        },
        {
            "name": "Orbit",
            "x": -0.3555875, "y": 0.3187293, "z": 0.01928878,
            "desc": "The bony socket formed by several skull bones that houses and protects the eyeball and its associated muscles.",
        },
        {
            "name": "Maxilla",
            "x": -0.1700016, "y": 0.6329805, "z": -0.3251481,
            "desc": "The upper jaw bone, forming part of the hard palate, nasal cavity floor, and orbital floor, and anchoring the upper teeth.",
        },
        {
            "name": "Zygomatic bone",
            "x": 0.3312976, "y": 0.5672088, "z": -0.177376,
            "desc": "The cheekbone, forming the prominence of the cheek and contributing to the lateral wall and floor of the orbit.",
        },
        {
            "name": "Mandible",
            "x": -0.09158078, "y": 0.686758, "z": -0.7584261,
            "desc": "The lower jaw bone, the only mobile bone of the skull, anchoring the lower teeth and enabling chewing via its joint with the temporal bone.",
        },
    ]

def real_muscular_leg_landmarks():
    """Landmarks on individual leg muscles, hover-verified against the live model."""
    return [
        {"name": "Iliotibial tract", "x": -0.08169181, "y": 0.1095104, "z": -0.4470122,
         "desc": "A thick band of fascia running along the outside of the thigh from the hip to the shin, stabilizing the knee during walking and running."},
        {"name": "Sartorius", "x": 0.07807064, "y": 0.1679986, "z": -0.2450631,
         "desc": "The longest muscle in the body, running obliquely across the thigh; flexes, abducts, and laterally rotates the hip."},
        {"name": "Vastus lateralis", "x": -0.0998649, "y": 0.1344495, "z": -0.04626274,
         "desc": "The largest of the four quadriceps muscles, located on the outer thigh, extending the knee."},
        {"name": "Rectus femoris", "x": 0.006294091, "y": 0.1882103, "z": -0.1722334,
         "desc": "The only quadriceps muscle that crosses both the hip and knee joints, flexing the hip and extending the knee."},
        {"name": "Vastus medialis", "x": 0.0385122, "y": 0.1280547, "z": 0.1264335,
         "desc": "The teardrop-shaped inner thigh quadriceps muscle, important for stabilizing the kneecap during extension."},
        {"name": "Quadriceps femoris tendon", "x": -0.01901314, "y": 0.06700007, "z": 0.209986,
         "desc": "The common tendon uniting all four quadriceps muscles, inserting on the patella and continuing as the patellar ligament."},
        {"name": "Medial gastrocnemius", "x": 0.02029059, "y": -0.008328028, "z": 0.4877055,
         "desc": "The inner head of the calf muscle, crossing both the knee and ankle to plantarflex the foot and flex the knee."},
        {"name": "Soleus", "x": -0.01130109, "y": -0.01797037, "z": 0.638746,
         "desc": "A broad, flat calf muscle beneath the gastrocnemius that plantarflexes the ankle, important for standing posture."},
        {"name": "Tibialis anterior", "x": -0.1024131, "y": 0.0360477, "z": 0.5468564,
         "desc": "A muscle on the front of the shin that dorsiflexes and inverts the foot, preventing foot drop during walking."},
        {"name": "Fibularis longus", "x": -0.1455763, "y": -0.03757411, "z": 0.6587935,
         "desc": "A muscle along the outer lower leg that everts the foot and supports the arches, also known as peroneus longus."},
        {"name": "Extensor digitorum longus", "x": -0.1210229, "y": -0.007194008, "z": 0.8700787,
         "desc": "A muscle on the front of the lower leg that extends the four smaller toes and assists in dorsiflexion of the ankle."},
        {"name": "Calcaneal tendon", "x": -0.0752551, "y": 0.001588798, "z": 0.7629116,
         "desc": "The Achilles tendon, the thick tendon connecting the calf muscles to the heel bone, transmitting force for plantarflexion."},
        {"name": "Gluteus maximus", "x": -0.02531371, "y": -0.144137, "z": -0.4385845,
         "desc": "The largest and most superficial gluteal muscle, the primary extensor of the hip during climbing and rising from sitting."},
        {"name": "Gluteus medius", "x": -0.09136716, "y": 0.03904931, "z": -0.4921014,
         "desc": "A hip abductor deep to the gluteus maximus, critical for stabilizing the pelvis during single-leg stance while walking."},
    ]

def real_upper_body_landmarks():
    """Landmarks on individual upper body muscles/bones, hover-verified against the live model."""
    return [
        {"name": "Platysma", "x": 0.1817018, "y": 0.1657725, "z": 0.7758356,
         "desc": "A thin, superficial sheet of muscle in the neck that depresses the jaw and tenses the skin of the lower face."},
        {"name": "Sternocleidomastoid", "x": 0.164486, "y": -0.0993895, "z": 0.5701255,
         "desc": "A prominent neck muscle that rotates and flexes the head, running from the sternum/clavicle to the skull behind the ear."},
        {"name": "Deltoid", "x": -0.2288032, "y": -0.01019553, "z": 0.4812157,
         "desc": "The rounded shoulder muscle with three heads that abducts, flexes, and extends the arm at the shoulder joint."},
        {"name": "Pectoralis major", "x": 0.06727368, "y": -0.2168334, "z": 0.3890215,
         "desc": "The large fan-shaped chest muscle that adducts and internally rotates the arm and assists in forced inspiration."},
        {"name": "Biceps brachii", "x": -0.2781324, "y": 0.01499691, "z": 0.1236214,
         "desc": "The two-headed muscle on the front of the upper arm that flexes the elbow and supinates the forearm."},
        {"name": "External oblique", "x": 0.118623, "y": -0.2527936, "z": -0.2378569,
         "desc": "The outermost lateral abdominal muscle, involved in trunk rotation and lateral flexion."},
        {"name": "Radius", "x": -0.4221242, "y": 0.05393634, "z": -0.4925807,
         "desc": "The lateral forearm bone (thumb side), which rotates around the ulna to allow palm-up/palm-down movement."},
        {"name": "Ulna", "x": -0.3687913, "y": 0.005868728, "z": -0.6904319,
         "desc": "The medial forearm bone (pinky side), forming the main hinge joint with the humerus at the elbow."},
    ]

def real_lymphatic_landmarks():
    """Landmarks on the lymphatic organs and node structure, hover-verified against the live model."""
    return [
        {"name": "Spleen", "x": 0.2164637, "y": -0.9329346, "z": -0.2145951,
         "desc": "The largest lymphatic organ, filtering blood, recycling old red blood cells, and housing white blood cells that respond to bloodborne pathogens."},
        {"name": "Palatine tonsil (right)", "x": -0.07726399, "y": 0.1588737, "z": 0.03873421,
         "desc": "Lymphoid tissue at the back of the throat that traps and responds to inhaled or ingested pathogens."},
        {"name": "Palatine tonsil (left)", "x": 0.007510842, "y": 0.1490398, "z": 0.03598163,
         "desc": "Lymphoid tissue at the back of the throat that traps and responds to inhaled or ingested pathogens."},
        {"name": "Efferent vessel", "x": 0.188746, "y": 0.4859074, "z": 0.2276196,
         "desc": "Carries filtered lymph out of the node toward the next node in the chain or into the venous circulation."},
        {"name": "Afferent vessel", "x": -0.0818106, "y": -0.5435711, "z": 0.1842102,
         "desc": "Carries lymph fluid into the node from surrounding tissue, delivering antigens for immune surveillance."},
        {"name": "Medulla", "x": -0.3109697, "y": 0.2960707, "z": 0.08774248,
         "desc": "The inner region of the lymph node, containing medullary cords and sinuses where filtered lymph collects before exiting."},
        {"name": "Capsule", "x": -0.4937548, "y": 0.1879306, "z": 0.41143,
         "desc": "The fibrous outer covering of the lymph node, from which trabeculae extend inward to support its internal structure."},
    ]

def thyroid_shape(anchor, lobe_radii=(0.03, 0.05, 0.02), separation=0.035, n_u=20, n_v=20):
    """Stylized two-lobe thyroid — placeholder until a real model exists."""
    u = np.linspace(0, 2 * np.pi, n_u)
    v = np.linspace(0, np.pi, n_v)
    U, V = np.meshgrid(u, v)
    ex, ey, ez = lobe_radii
    x_unit, y_unit, z_unit = np.cos(U) * np.sin(V), np.sin(U) * np.sin(V), np.cos(V)
    right_lobe = (anchor[0] + separation + x_unit * ex, anchor[1] + y_unit * ey, anchor[2] + z_unit * ez)
    left_lobe = (anchor[0] - separation + x_unit * ex, anchor[1] + y_unit * ey, anchor[2] + z_unit * ez)
    return right_lobe, left_lobe


def parathyroid_shapes(anchor, radius=0.008, spread=0.045, n_u=12, n_v=12):
    """Four tiny stylized parathyroid glands behind the thyroid lobes — placeholder."""
    u = np.linspace(0, 2 * np.pi, n_u)
    v = np.linspace(0, np.pi, n_v)
    U, V = np.meshgrid(u, v)
    x_unit, y_unit, z_unit = np.cos(U) * np.sin(V), np.sin(U) * np.sin(V), np.cos(V)
    offsets = [(spread, 0.015), (spread, -0.015), (-spread, 0.015), (-spread, -0.015)]
    glands = []
    for dx, dz in offsets:
        gx = anchor[0] + dx + x_unit * radius
        gy = anchor[1] + y_unit * radius
        gz = anchor[2] + dz + z_unit * radius
        glands.append((gx, gy, gz))
    return glands

def ovary_shapes(anchor, radii=(0.025, 0.04, 0.02), separation=0.06, n_u=16, n_v=16):
    """Two stylized ovoid ovaries — placeholder, positioned in the pelvic cavity (not analogous to testes)."""
    u = np.linspace(0, 2 * np.pi, n_u)
    v = np.linspace(0, np.pi, n_v)
    U, V = np.meshgrid(u, v)
    ex, ey, ez = radii
    x_unit, y_unit, z_unit = np.cos(U) * np.sin(V), np.sin(U) * np.sin(V), np.cos(V)
    right_ovary = (anchor[0] + separation + x_unit * ex, anchor[1] + y_unit * ey, anchor[2] + z_unit * ez)
    left_ovary = (anchor[0] - separation + x_unit * ex, anchor[1] + y_unit * ey, anchor[2] + z_unit * ez)
    return right_ovary, left_ovary

def real_endocrine_landmarks():
    """Landmarks on the endocrine glands. Brain/adrenal/testis/thymus points are hover-verified;
    thyroid/parathyroid/ovaries are placeholder-shape anchor points, not scanned geometry."""
    return [
        {"name": "Hypothalamus", "x": -0.0155104, "y": 0.01092588, "z": 0.433949,
         "desc": "Links the nervous system to the endocrine system, controlling the pituitary gland via releasing and inhibiting hormones."},
        {"name": "Pituitary gland", "x": -0.01777104, "y": 0.005096407, "z": 0.4066051,
         "desc": "The 'master gland' at the base of the brain, secreting hormones that regulate growth, metabolism, and other endocrine glands."},
        {"name": "Pineal gland", "x": -0.02167469, "y": 0.07161599, "z": 0.4347966,
         "desc": "A small gland deep in the brain that produces melatonin, regulating the sleep-wake cycle."},
        {"name": "Pancreas", "x": 0.01561859, "y": 0.0377256, "z": 0.03411656,
         "desc": "Secretes insulin and glucagon to regulate blood glucose, alongside its digestive enzyme role."},
        {"name": "Right adrenal cortex", "x": 0.0223198, "y": 0.08907248, "z": -0.2911689,
         "desc": "The outer layer of the adrenal gland, producing cortisol, aldosterone, and androgens."},
        {"name": "Left adrenal cortex", "x": -0.08480359, "y": 0.1006744, "z": -0.3102846,
         "desc": "The outer layer of the adrenal gland, producing cortisol, aldosterone, and androgens."},
        {"name": "Left testis", "x": 0.0185171, "y": -0.06837781, "z": -0.9686386,
         "desc": "Produces testosterone and sperm, regulated by luteinizing hormone and follicle-stimulating hormone from the pituitary."},
        {"name": "Right testis", "x": -0.05030634, "y": -0.06918068, "z": -0.9715774,
         "desc": "Produces testosterone and sperm, regulated by luteinizing hormone and follicle-stimulating hormone from the pituitary."},
        {"name": "Thymus (left lobe)", "x": 0.03592321, "y": -0.04212443, "z": 0.006089117,
         "desc": "Produces and matures T-lymphocytes, most active during childhood and gradually shrinking with age."},
        {"name": "Thymus (right lobe)", "x": -0.03719229, "y": -0.04308853, "z": -0.005247455,
         "desc": "Produces and matures T-lymphocytes, most active during childhood and gradually shrinking with age."},
        {"name": "Thyroid gland", "x": -0.0154, "y": 0.0159, "z": 0.1745,
         "desc": "Regulates metabolic rate via thyroxine (T4) and triiodothyronine (T3). Stylized placeholder — not yet based on a real model."},
        {"name": "Parathyroid glands", "x": -0.0154, "y": 0.0159, "z": 0.1745,
         "desc": "Four small glands on the back of the thyroid that release parathyroid hormone to regulate blood calcium. Stylized placeholder — not yet based on a real model."},
        {"name": "Ovaries", "x": 0.0, "y": -0.02, "z": -0.75,
         "desc": "Produce estrogen and progesterone, and release eggs during ovulation. Stylized placeholder — this specimen is male, so exact positioning is an anatomical approximation, not scanned geometry."},
    ]

def box_mesh(x_range, y_range, z_range):
    """Simple rectangular slab mesh, used for skin cross-section layers."""
    x0, x1 = x_range
    y0, y1 = y_range
    z0, z1 = z_range
    verts = np.array([
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
    ])
    faces = np.array([
        [0, 1, 2], [0, 2, 3],
        [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4],
        [2, 3, 7], [2, 7, 6],
        [1, 2, 6], [1, 6, 5],
        [0, 3, 7], [0, 7, 4],
    ])
    return verts, faces


def gland_shape(center, radii=(0.05, 0.05, 0.05), n_u=14, n_v=14):
    """Small stylized ellipsoid gland (sweat gland, sebaceous gland, nerve ending)."""
    u = np.linspace(0, 2 * np.pi, n_u)
    v = np.linspace(0, np.pi, n_v)
    U, V = np.meshgrid(u, v)
    ex, ey, ez = radii
    x = center[0] + np.cos(U) * np.sin(V) * ex
    y = center[1] + np.sin(U) * np.sin(V) * ey
    z = center[2] + np.cos(V) * ez
    return x, y, z


def tube_shape(start, end, radius, n_u=16, n_v=12):
    """Simple straight tube between two points — used for hair follicle/shaft and blood vessels."""
    p0, p1 = np.array(start, dtype=float), np.array(end, dtype=float)
    t_vals = np.linspace(0, 1, n_u)
    theta = np.linspace(0, 2 * np.pi, n_v)
    centerline = np.array([p0 + (p1 - p0) * t for t in t_vals])
    tangent = (p1 - p0) / (np.linalg.norm(p1 - p0) + 1e-9)
    not_parallel = np.array([1.0, 0.0, 0.0]) if abs(tangent[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    perp1 = np.cross(tangent, not_parallel)
    perp1 /= np.linalg.norm(perp1) + 1e-9
    perp2 = np.cross(tangent, perp1)

    X = np.zeros((n_v, n_u))
    Y = np.zeros((n_v, n_u))
    Z = np.zeros((n_v, n_u))
    for i in range(n_u):
        for j, th in enumerate(theta):
            offset = radius * (perp1 * np.cos(th) + perp2 * np.sin(th))
            X[j, i] = centerline[i][0] + offset[0]
            Y[j, i] = centerline[i][1] + offset[1]
            Z[j, i] = centerline[i][2] + offset[2]
    return X, Y, Z


def real_integumentary_landmarks():
    """Landmarks on the real skin cross-section model, hover-verified against the live mesh."""
    return [
        {"name": "Stratum basale", "x": 0.3605624, "y": 0.2463361, "z": 0.3613856,
         "desc": "The deepest epidermal layer, containing the stem cells that continuously divide to replace shed skin cells."},
        {"name": "Keratinocyte", "x": -0.1442133, "y": 0.2790661, "z": 0.3797642,
         "desc": "The dominant epidermal cell type, producing keratin and migrating outward as it matures before being shed."},
        {"name": "Melanocyte", "x": 0.3550969, "y": 0.2180186, "z": 0.2506286,
         "desc": "A pigment-producing cell in the stratum basale that transfers melanin to keratinocytes, protecting against UV damage."},
        {"name": "Merkel cell", "x": -0.1059402, "y": 0.2472646, "z": 0.3802377,
         "desc": "A mechanoreceptor-associated cell in the epidermis involved in light touch sensation."},
        {"name": "Langerhans cell", "x": 0.122187, "y": 0.3061555, "z": 0.3788767,
         "desc": "An antigen-presenting immune cell residing in the epidermis, part of the skin's immune surveillance."},
        {"name": "Stratum corneum", "x": 0.358264, "y": 0.3816016, "z": 0.250836,
         "desc": "The outermost epidermal layer, made of dead, keratin-filled corneocytes forming a waterproof barrier."},
        {"name": "Basement membrane of epidermis", "x": -0.3206586, "y": 0.2149217, "z": -0.2218963,
         "desc": "A thin extracellular matrix layer anchoring the epidermis to the underlying dermis."},
        {"name": "Fibroblast", "x": -0.4019801, "y": 0.04166948, "z": 0.3769107,
         "desc": "The main cell type of the dermis, synthesizing collagen and other extracellular matrix components."},
        {"name": "Dermal matrix", "x": 0.3570949, "y": 0.0469163, "z": 0.3487808,
         "desc": "The collagen- and elastin-rich extracellular matrix of the dermis, providing skin's strength and elasticity."},
        {"name": "Hair", "x": 0.1274475, "y": 0.7864541, "z": -0.03604706,
         "desc": "A keratinized filament growing from a hair follicle, providing sensation, thermoregulation, and protection."},
        {"name": "Arrector pili muscle", "x": -0.1141753, "y": 0.1779784, "z": -0.3880278,
         "desc": "A small smooth muscle attached to the hair follicle that contracts to raise hair and produce goosebumps."},
        {"name": "Sebaceous gland", "x": 0.09127185, "y": 0.1901347, "z": -0.4564595,
         "desc": "A gland associated with the hair follicle that secretes sebum to lubricate and waterproof skin and hair."},
        {"name": "Apocrine sweat gland", "x": -0.2260615, "y": -0.09624555, "z": -0.4811293,
         "desc": "A larger sweat gland found in areas like the armpits and groin, becoming active at puberty and linked to body odor."},
        {"name": "Eccrine sweat gland", "x": -0.1223524, "y": -0.1010572, "z": -0.156205,
         "desc": "The most numerous sweat gland type, distributed across most of the body, producing watery sweat for thermoregulation."},
        {"name": "Nerve", "x": -0.05642565, "y": 0.1597978, "z": 0.3793591,
         "desc": "Sensory nerve endings in the dermis detecting touch, pressure, temperature, and pain."},
        {"name": "Dermal vessel", "x": -0.05116492, "y": -0.5573949, "z": -0.2431908,
         "desc": "Blood vessels within the dermis supplying nutrients and regulating body temperature via vasodilation and vasoconstriction."},
        {"name": "Fat in subcutis", "x": 0.3987274, "y": -0.4506577, "z": 0.2070705,
         "desc": "Adipose tissue in the hypodermis providing insulation, energy storage, and cushioning."},
    ]

def tube_along_path(points, radius, n_v=10):
    """Builds a tube mesh following any sequence of 3D points — used for coiled/angled structures."""
    points = np.array(points, dtype=float)
    n_u = len(points)
    tangents = np.gradient(points, axis=0)
    tangents = tangents / (np.linalg.norm(tangents, axis=1, keepdims=True) + 1e-9)
    theta = np.linspace(0, 2 * np.pi, n_v)

    perp1_list = np.zeros_like(tangents)
    not_parallel = np.array([1.0, 0.0, 0.0]) if abs(tangents[0][0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    perp1 = np.cross(tangents[0], not_parallel)
    perp1 /= np.linalg.norm(perp1) + 1e-9
    perp1_list[0] = perp1
    for i in range(1, n_u):
        p = perp1_list[i - 1] - tangents[i] * np.dot(perp1_list[i - 1], tangents[i])
        norm_p = np.linalg.norm(p)
        if norm_p < 1e-6:
            not_parallel = np.array([1.0, 0.0, 0.0]) if abs(tangents[i][0]) < 0.9 else np.array([0.0, 1.0, 0.0])
            p = np.cross(tangents[i], not_parallel)
            norm_p = np.linalg.norm(p)
        perp1_list[i] = p / (norm_p + 1e-9)

    X = np.zeros((n_v, n_u))
    Y = np.zeros((n_v, n_u))
    Z = np.zeros((n_v, n_u))
    for i in range(n_u):
        tangent, perp1 = tangents[i], perp1_list[i]
        perp2 = np.cross(tangent, perp1)
        for j, th in enumerate(theta):
            offset = radius * (perp1 * np.cos(th) + perp2 * np.sin(th))
            X[j, i] = points[i][0] + offset[0]
            Y[j, i] = points[i][1] + offset[1]
            Z[j, i] = points[i][2] + offset[2]
    return X, Y, Z


def wavy_epidermis_surface(x_range, z_range, y_base, amplitude=0.025, n=24):
    """Slightly undulating top surface, like real epidermal ridges."""
    x = np.linspace(x_range[0], x_range[1], n)
    z = np.linspace(z_range[0], z_range[1], n)
    X, Z = np.meshgrid(x, z)
    Y = y_base + amplitude * np.sin(X * 6) * np.cos(Z * 6)
    return X, Y, Z