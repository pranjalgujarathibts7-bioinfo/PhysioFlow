import trimesh
import numpy as np
import streamlit as st


@st.cache_resource
def load_heart_mesh(path: str = "models/heart/heart.stl"):
    """
    Loads the real anatomical heart mesh once and caches it,
    so it doesn't reload from disk on every Streamlit rerun.
    """
    mesh = trimesh.load(path, force="mesh")

    vertices = mesh.vertices
    faces = mesh.faces

    return {
        "x": vertices[:, 0].tolist(),
        "y": vertices[:, 1].tolist(),
        "z": vertices[:, 2].tolist(),
        "i": faces[:, 0].tolist(),
        "j": faces[:, 1].tolist(),
        "k": faces[:, 2].tolist(),
    }

@st.cache_resource
def load_brain_mesh(path: str = "models/brain/brain.stl"):
    mesh = trimesh.load(path, force="mesh")

    vertices = mesh.vertices - mesh.vertices.mean(axis=0)
    scale = np.abs(vertices).max()
    vertices = vertices / scale

    faces = mesh.faces

    return {
        "x": vertices[:, 0].tolist(),
        "y": vertices[:, 1].tolist(),
        "z": vertices[:, 2].tolist(),
        "i": faces[:, 0].tolist(),
        "j": faces[:, 1].tolist(),
        "k": faces[:, 2].tolist(),
    }

@st.cache_resource
def load_lungs_mesh(path: str = "models/lungs/lungs_simplified.stl"):
    mesh = trimesh.load(path, force="mesh")

    vertices = mesh.vertices - mesh.vertices.mean(axis=0)
    scale = np.abs(vertices).max()
    vertices = vertices / scale

    faces = mesh.faces

    return {
        "x": vertices[:, 0].tolist(),
        "y": vertices[:, 1].tolist(),
        "z": vertices[:, 2].tolist(),
        "i": faces[:, 0].tolist(),
        "j": faces[:, 1].tolist(),
        "k": faces[:, 2].tolist(),
    }

@st.cache_resource
def load_kidney_system():
    right_scene = trimesh.load("models/kidney/VH_M_Kidney_R.glb")
    left = trimesh.load("models/kidney/vh_m_kidney_l_NIH3D.stl", force="mesh")
    ureter = trimesh.load("models/kidney/vh_m_ureter_r_NIH3D.stl", force="mesh")

    right_merged = trimesh.util.concatenate(list(right_scene.geometry.values()))

    all_verts = np.vstack([right_merged.vertices, left.vertices, ureter.vertices])
    center = all_verts.mean(axis=0)
    scale = np.abs(all_verts - center).max()

    def process(mesh):
        v = (mesh.vertices - center) / scale
        f = mesh.faces
        return {
            "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
            "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
        }

    names = list(right_scene.geometry.keys())
    shell_names = ["VH_M_kidney_capsule_R", "VH_M_outer_cortex_of_kidney_R"]
    pyramid_names = [n for n in names if "pyramid" in n or "papilla" in n]
    column_hilum_names = [n for n in names if n not in shell_names and n not in pyramid_names]

    shell_mesh = trimesh.util.concatenate([right_scene.geometry[n] for n in shell_names])
    pyramid_mesh = trimesh.util.concatenate([right_scene.geometry[n] for n in pyramid_names])
    column_hilum_mesh = trimesh.util.concatenate([right_scene.geometry[n] for n in column_hilum_names])

    return {
        "right_shell": process(shell_mesh),
        "right_pyramids": process(pyramid_mesh),
        "right_column_hilum": process(column_hilum_mesh),
        "left": process(left),
        "ureter": process(ureter),
    }

@st.cache_resource
def load_digestive_system():
    scene = trimesh.load("models/digestive/3d-vh-m-united.glb")

    groups = {
        "liver": [
            "VH_M_bare_area_of_liver", "VH_M_liver_capsule", "VH_M_suprarenal_impression_of_liver",
            "VH_M_renal_impression_of_liver", "VH_M_gastric_impression_of_liver", "VH_M_colic_impression_of_liver",
            "VH_M_esophageal_impression_of_liver", "VH_M_duodenal_impression_of_liver", "VH_M_caudate_lobe_of_liver",
            "VH_M_quadrate_lobe_of_liver", "VH_M_hepataduodenal_ligament", "VH_M_round_ligament_of_liver",
            "VH_M_triangular_ligament_of_liver", "VH_M_coronary_ligament_of_liver",
        ],
        "pancreas": [
            "VH_M_body_of_pancreas", "VH_M_tail_of_pancreas", "VH_M_head_of_pancreas",
            "VH_M_neck_of_pancreas", "VH_M_uncinate_process_of_the_pancreas",
        ],
        "pancreatic_ducts": [
            "VH_M_dorsal_pancreatic_duct", "VH_M_ventral_pancreatic_duct", "VH_M_hepatopancreatic_ampulla",
        ],
        "gallbladder": ["VH_M_gallbladder"],
        "duodenum": [
            "VH_M_duodenum_ascending", "VH_M_duodenum_descending", "VH_M_duodenum_horizonal",
            "VH_M_duodenum_superior", "VH_M_duodenal_ampulla", "VH_M_sphincter_of_hepatopancreatic_ampulla",
        ],
        "jejunum_ileum": ["VH_M_jejunum", "VH_M_ileum", "VH_M_ileum_terminal"],
        "large_intestine": [
            "VH_M_ascending_colon", "VH_M_transverse_colon", "VH_M_descending_colon", "VH_M_sigmoid_colon",
            "VH_M_hepatic_flexure_of_colon", "VH_M_splenic_flexure_of_colon", "VH_M_rectum",
        ],
        "appendix": ["VH_M_vermiform_appendix"],
    }

    all_names = [n for names in groups.values() for n in names]
    all_verts = np.vstack([scene.geometry[n].vertices for n in all_names])
    center = all_verts.mean(axis=0)
    scale = np.abs(all_verts - center).max()

    def process(names):
        mesh = trimesh.util.concatenate([scene.geometry[n] for n in names])
        v = (mesh.vertices - center) / scale
        f = mesh.faces
        return {
            "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
            "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
        }

    result = {name: process(names) for name, names in groups.items()}

    # Anchor points for the stylized stomach/esophagus, using the liver's real "impression" positions
    anchors = {}
    for key, name in [
        ("gastric", "VH_M_gastric_impression_of_liver"),
        ("esophageal", "VH_M_esophageal_impression_of_liver"),
        ("duodenal", "VH_M_duodenal_impression_of_liver"),
    ]:
        c = scene.geometry[name].vertices.mean(axis=0)
        anchors[key] = ((c - center) / scale).tolist()
    result["_anchors"] = anchors

    return result

@st.cache_resource
def load_skeletal_axial_appendicular():
    scene = trimesh.load("models/digestive/3d-vh-m-united.glb")  # same body file as digestive

    groups = {
        "spine": [f"VH_M_cervical_vertebra_{i}" for i in range(1, 8)]
                 + [f"VH_M_thoracic_vertebra_{i}" for i in range(1, 13)]
                 + [f"VH_M_lumbar_vertebra_{i}" for i in range(1, 6)]
                 + ["VH_M_sacrum", "VH_M_coccyx"],
        "pelvis": [
            "VH_M_ilium_compact_bone_L", "VH_M_ilium_compact_bone_R",
            "VH_M_ilium_spongy_bone_L", "VH_M_ilium_spongy_bone_R",
            "VH_M_ischium_compact_bone_L", "VH_M_ischium_compact_bone_R",
            "VH_M_ischium_spongy_bone_L", "VH_M_ischium_spongy_bone_R",
            "VH_M_pubis_compact_bone_L", "VH_M_pubis_compact_bone_R",
            "VH_M_pubis_spongy_bone_L", "VH_M_pubis_spongy_bone_R",
        ],
        "right_leg": ["VH_M_femur_R", "VH_M_tibia_R", "VH_M_fibula_R", "VH_M_patella_R"],
        "left_leg": ["VH_M_femur_L", "VH_M_tibia_L", "VH_M_fibula_L", "VH_M_patella_L"],
        "knee_ligaments": [
            "VH_M_fibular_collateral_ligament_R", "VH_M_right_tibial_collaterial_ligament",
            "VH_M_patellar_ligament_R", "VH_M_fibular_collateral_ligament_L",
            "VH_M_left_tibial_collateral_ligament", "VH_M_patellar_ligament_L",
        ],
    }

    all_names = [n for names in groups.values() for n in names]
    all_verts = np.vstack([scene.geometry[n].vertices for n in all_names])
    center = all_verts.mean(axis=0)
    scale = np.abs(all_verts - center).max()

    def process(names):
        mesh = trimesh.util.concatenate([scene.geometry[n] for n in names])
        v = (mesh.vertices - center) / scale
        f = mesh.faces
        return {
            "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
            "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
        }

    return {name: process(names) for name, names in groups.items()}

@st.cache_resource
def load_skull_mesh(path="models/skeletal/vhm_skull_0_NIH3D.stl",
                     scale_factor=0.11, offset=(0.0, 0.36, 0.0),
                     flip=False, rotate_x_deg=90, rotate_y_deg=0):
    mesh = trimesh.load(path, force="mesh")
    v = mesh.vertices - mesh.vertices.mean(axis=0)

    long_axis = np.array([0.01870128, 0.94965226, -0.31274725])
    if flip:
        long_axis = -long_axis
    R = _rotation_matrix_from_vectors(long_axis, np.array([0, 1, 0]))
    v = v @ R.T

    theta_x = np.radians(rotate_x_deg)
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(theta_x), -np.sin(theta_x)],
        [0, np.sin(theta_x), np.cos(theta_x)],
    ])
    v = v @ Rx.T

    theta_y = np.radians(rotate_y_deg)
    Ry = np.array([
        [np.cos(theta_y), 0, np.sin(theta_y)],
        [0, 1, 0],
        [-np.sin(theta_y), 0, np.cos(theta_y)],
    ])
    v = v @ Ry.T

    v = v / np.abs(v).max()
    v = v * scale_factor
    v = v + np.array(offset)
    f = mesh.faces
    return {
        "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
        "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
    }

@st.cache_resource
def load_ribcage_mesh(path="models/skeletal/RibCage%20Spine_NIH3D.stl",
                       scale_factor=0.45, offset=(0.0, 0.05, 0.0), flip=False):
    mesh = trimesh.load(path, force="mesh")
    v = mesh.vertices - mesh.vertices.mean(axis=0)

    long_axis = np.array([-0.01351066, 0.07556613, -0.99704926])
    if flip:
        long_axis = -long_axis
    R = _rotation_matrix_from_vectors(long_axis, np.array([0, 1, 0]))
    v = v @ R.T

    v = v / np.abs(v).max()
    v = v * scale_factor
    v = v + np.array(offset)
    f = mesh.faces
    return {
        "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
        "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
    }

def _rotation_matrix_from_vectors(a, b):
    """Rotation matrix that rotates vector a onto vector b (both should be unit vectors)."""
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    c = np.dot(a, b)
    if np.linalg.norm(v) < 1e-8:
        return np.eye(3) if c > 0 else -np.eye(3)
    kmat = np.array([
        [0, -v[2], v[1]],
        [v[2], 0, -v[0]],
        [-v[1], v[0], 0],
    ])
    return np.eye(3) + kmat + kmat @ kmat * (1 / (1 + c))

@st.cache_resource
def load_skull_mesh_standalone(path="models/skeletal/vhm_skull_0_NIH3D.stl"):
    mesh = trimesh.load(path, force="mesh")
    v = mesh.vertices - mesh.vertices.mean(axis=0)
    v = v / np.abs(v).max()
    f = mesh.faces
    return {
        "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
        "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
    }

@st.cache_resource
def load_muscular_leg_system():
    base = "models/muscular/Right/"

    groups = {
        "quadriceps": ["RectusFemoris", "VastusLateralis", "VastusMedialis", "VastusIntermedius"],
        "hamstrings": ["BicepsFemorisLong", "BicepsFemorisShort", "Semimembranosus", "Semitendinosus"],
        "adductors": ["AdductorBrevis", "AdductorLongus", "AdductorMagnus", "Gracilis", "Pectineus"],
        "glutes": ["GluteusMaximus", "GluteusMedius", "GluteusMinimus"],
        "deep_hip_rotators": ["Piriformis", "ObturatorExternus", "ObturatorInternus", "SuperiorGemellus", "InferiorGemellus", "QuadratisFemoris"],
        "hip_flexors": ["Illiacus", "PsoasMajor", "Sartorius", "TensorFasciaeLatae"],
        "calf": ["GastrocnemiusLateral", "GastrocnemiusMedial", "Soleus", "Plantaris", "Popliteus"],
        "lower_leg": ["TibialisAnterior", "TibialisPosterior", "PeroneusLongus", "ExtensorDigitorumLongus", "ExtensorHallucisLongus", "FlexorDigitorumLongus", "FlexorHallucisLongus"],
    }
    bones = ["Femur", "Tibia", "Fibula", "Patella", "Pelvis"]

    def muscle_path(name):
        return f"{base}VHM_Right_Muscle_{name}_smooth.stl"

    def bone_path(name):
        return f"{base}VHM_Right_Bone_{name}_smooth.stl"

    all_paths = [muscle_path(n) for names in groups.values() for n in names] + [bone_path(n) for n in bones]
    all_meshes = [trimesh.load(p, force="mesh") for p in all_paths]
    all_verts = np.vstack([m.vertices for m in all_meshes])
    center = all_verts.mean(axis=0)
    scale = np.abs(all_verts - center).max()

    def process(paths):
        meshes = [trimesh.load(p, force="mesh") for p in paths]
        mesh = trimesh.util.concatenate(meshes)
        v = (mesh.vertices - center) / scale
        f = mesh.faces
        return {
            "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
            "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
        }

    result = {name: process([muscle_path(n) for n in names]) for name, names in groups.items()}
    result["bones"] = process([bone_path(n) for n in bones])
    return result

@st.cache_resource
def load_upper_body_system():
    base = "models/upper_body/"

    groups = {
        "deltoid": ["FMA34680", "FMA34682", "FMA34684"],
        "pectoralis_major": ["FMA34690", "FMA45874", "FMA79979"],
        "biceps_brachii": ["FMA37684", "FMA37686"],
        "triceps_brachii": ["FMA37695", "FMA37697", "FMA37699"],
        "trapezius": ["FMA33581", "FMA33584", "FMA33586"],
        "latissimus_dorsi": ["FMA13358"],
        "rectus_abdominis": ["FMA13377"],
        "external_oblique": ["FMA13336"],
    }
    bones = ["FMA23130", "FMA23464", "FMA23467", "FMA13395", "FMA13322"]

    def path(fid):
        return f"{base}{fid}.stl"

    all_paths = [path(f) for names in groups.values() for f in names] + [path(f) for f in bones]
    all_meshes = [trimesh.load(p, force="mesh") for p in all_paths]
    all_verts = np.vstack([m.vertices for m in all_meshes])
    center = all_verts.mean(axis=0)
    scale = np.abs(all_verts - center).max()

    def process(paths):
        meshes = [trimesh.load(p, force="mesh") for p in paths]
        mesh = trimesh.util.concatenate(meshes)
        v = (mesh.vertices - center) / scale
        f = mesh.faces
        return {
            "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
            "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
        }

    result = {name: process([path(f) for f in fids]) for name, fids in groups.items()}
    result["bones"] = process([path(f) for f in bones])
    return result

@st.cache_resource
def load_endocrine_system():
    base = "models/endocrine/"
    files = {
        "pituitary": "FMA13889", "adrenal_R": "FMA15629", "adrenal_L": "FMA15630",
        "thymus_R": "FMA71194", "thymus_L": "FMA71195", "pineal": "FMA62033",
        "hypothalamus": "FMA62008nsn", "testis_R": "FMA7211", "testis_L": "FMA7212",
    }

    def path(fid):
        return f"{base}{fid}.stl"

    meshes = {k: trimesh.load(path(v), force="mesh") for k, v in files.items()}
    all_verts = np.vstack([m.vertices for m in meshes.values()])
    center = all_verts.mean(axis=0)
    scale = np.abs(all_verts - center).max()

    def process(mesh):
        v = (mesh.vertices - center) / scale
        f = mesh.faces
        return {
            "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
            "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
        }

    result = {k: process(m) for k, m in meshes.items()}
    cartilage = trimesh.load(path("FMA55099"), force="mesh")
    result["_thyroid_anchor"] = ((cartilage.vertices.mean(axis=0) - center) / scale).tolist()
    return result

@st.cache_resource
def load_lymphatic_organs():
    scene = trimesh.load("models/digestive/3d-vh-m-united.glb")  # same body file

    groups = {
        "spleen": ["VH_M_colic_surface_of_spleen", "VH_M_diaphragmatic_surface_of_spleen",
                   "VH_M_gastric_surface_of_spleen", "VH_M_hilum_of_spleen", "VH_M_renal_surface_of_spleen"],
        "tonsil_L": ["VH_M_palatine_tonsil_L"],
        "tonsil_R": ["VH_M_palatine_tonsil_R"],
    }

    all_names = [n for names in groups.values() for n in names]
    all_verts = np.vstack([scene.geometry[n].vertices for n in all_names])
    center = all_verts.mean(axis=0)
    scale = np.abs(all_verts - center).max()

    def process(names):
        mesh = trimesh.util.concatenate([scene.geometry[n] for n in names])
        v = (mesh.vertices - center) / scale
        f = mesh.faces
        return {
            "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
            "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
        }

    return {name: process(names) for name, names in groups.items()}


@st.cache_resource
def load_lymph_node_structure():
    scene = trimesh.load("models/digestive/3d-vh-m-united.glb")

    groups = {
        "capsule": ["Yao_capsule_of_lymph_node"],
        "medulla": ["Yao_medulla_of_lymph_node"],
        "afferent_vessel": ["Yao_afferent_lymphatic_vessel"],
        "efferent_vessel": ["Yao_efferent_lymph_node"],
    }

    all_names = [n for names in groups.values() for n in names]
    all_verts = np.vstack([scene.geometry[n].vertices for n in all_names])
    center = all_verts.mean(axis=0)
    scale = np.abs(all_verts - center).max()

    def process(names):
        mesh = trimesh.util.concatenate([scene.geometry[n] for n in names])
        v = (mesh.vertices - center) / scale
        f = mesh.faces
        return {
            "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
            "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
        }

    return {name: process(names) for name, names in groups.items()}

@st.cache_resource
def load_male_reproductive_system():
    base = "models/reproductive/male/"
    files = {
        "prostate": "FMA9600", "epididymis_R": "FMA18256", "epididymis_L": "FMA18257",
        "seminal_vesicle_R": "FMA19387", "seminal_vesicle_L": "FMA19388",
        "glans_penis": "FMA18247", "corpus_cavernosum": "FMA19618", "corpus_spongiosum": "FMA19617nsn",
        "testis_R": "FMA7211", "testis_L": "FMA7212",
    }

    def path(fid):
        return f"{base}{fid}.stl"

    meshes = {k: trimesh.load(path(v), force="mesh") for k, v in files.items()}
    all_verts = np.vstack([m.vertices for m in meshes.values()])
    center = all_verts.mean(axis=0)
    scale = np.abs(all_verts - center).max()

    def process(mesh):
        v = (mesh.vertices - center) / scale
        f = mesh.faces
        return {
            "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
            "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
        }

    return {k: process(m) for k, m in meshes.items()}


@st.cache_resource
def load_female_reproductive_system():
    scene = trimesh.load("models/reproductive/female/whole/scene.gltf")
    names = list(scene.geometry.keys())  # Object_0, Object_1 = ovaries; Object_2 = uterus/tubes/cervix/vagina

    all_verts = np.vstack([scene.geometry[n].vertices for n in names])
    center = all_verts.mean(axis=0)
    scale = np.abs(all_verts - center).max()

    def process(name):
        mesh = scene.geometry[name]
        v = (mesh.vertices - center) / scale
        f = mesh.faces
        return {
            "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
            "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
        }

    return {
        "ovary_A": process(names[0]),
        "ovary_B": process(names[1]),
        "uterus_system": process(names[2]),
    }

@st.cache_resource
def load_female_reproductive_xsection():
    scene = trimesh.load("models/reproductive/female/xsection/scene.gltf")
    names = list(scene.geometry.keys())

    all_verts = np.vstack([scene.geometry[n].vertices for n in names])
    center = all_verts.mean(axis=0)
    scale = np.abs(all_verts - center).max()

    def process(name):
        mesh = scene.geometry[name]
        v = (mesh.vertices - center) / scale
        f = mesh.faces
        return {
            "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
            "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
        }

    return {
        "ovary_A": process(names[0]),
        "ovary_B": process(names[1]),
        "uterus_system_xsection": process(names[2]),
    }

@st.cache_resource
def load_skin_mesh():
    scene = trimesh.load("models/digestive/3d-vh-m-united.glb")
    mesh = scene.geometry["VH_M_skin"]
    v = mesh.vertices - mesh.vertices.mean(axis=0)
    v = v / np.abs(v).max()
    f = mesh.faces
    return {
        "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
        "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
    }

@st.cache_resource
def load_real_skin_model():
    scene = trimesh.load("models/integumentary/scene.gltf")
    names = list(scene.geometry.keys())

    all_verts = np.vstack([scene.geometry[n].vertices for n in names])
    center = all_verts.mean(axis=0)
    scale = np.abs(all_verts - center).max()

    def process(name):
        mesh = scene.geometry[name]
        v = (mesh.vertices - center) / scale
        f = mesh.faces

        try:
            color_visual = mesh.visual.to_color()
            colors = np.array(color_visual.vertex_colors)
            if colors.ndim == 1:
                colors = np.tile(colors, (len(v), 1))
            vertexcolor = [f"rgb({r},{g},{b})" for r, g, b, a in colors]
        except Exception:
            vertexcolor = ["rgb(217,168,142)"] * len(v)  # skin-tone fallback

        return {
            "x": v[:, 0].tolist(), "y": v[:, 1].tolist(), "z": v[:, 2].tolist(),
            "i": f[:, 0].tolist(), "j": f[:, 1].tolist(), "k": f[:, 2].tolist(),
            "vertexcolor": vertexcolor,
        }

    return {name: process(name) for name in names}
