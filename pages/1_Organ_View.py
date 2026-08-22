import json
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from utils.shapes import (
    get_shape_for_system,
    real_heart_landmarks,
    real_brain_landmarks,
    real_lungs_landmarks,
    real_kidney_landmarks,
    real_digestive_landmarks,
    real_skeletal_landmarks,
    real_muscular_leg_landmarks,
    real_upper_body_landmarks,
    real_endocrine_landmarks,
    real_lymphatic_landmarks,
    stomach_shape,
    esophagus_shape,
    thyroid_shape,
    parathyroid_shapes,
    ovary_shapes,
    box_mesh,
    gland_shape,
    tube_along_path,
    wavy_epidermis_surface,
    real_integumentary_landmarks,
)
from utils.mesh_loader import (
    load_heart_mesh,
    load_brain_mesh,
    load_lungs_mesh,
    load_kidney_system,
    load_digestive_system,
    load_skeletal_axial_appendicular,
    load_skull_mesh_standalone,
    load_ribcage_mesh,
    load_muscular_leg_system,
    load_upper_body_system,
    load_endocrine_system,
    load_lymphatic_organs,
    load_lymph_node_structure,
    load_male_reproductive_system,
    load_female_reproductive_system,
    load_female_reproductive_xsection,
    load_real_skin_model,
)

st.set_page_config(page_title="PhysioFlow", page_icon="🫀", layout="wide")


def load_css(path: str):
    with open(path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css("assets/style.css")

with open("data/systems.json", encoding="utf-8") as f:
    systems = json.load(f)

selected = st.session_state.get("selected_system")

if selected is None or selected not in systems:
    st.warning("No organ system selected. Go back to the homepage and click Explore on a card.")
    st.stop()

sysdata = systems[selected]

st.markdown(f"## {sysdata['icon']} {sysdata['name']}")
st.write(sysdata["summary"])

st.divider()

col_3d, col_legend, col_info = st.columns([3, 1.3, 2])

landmarks = []
view_suffix = ""  # disambiguates legend button keys across toggle views (Skull vs Full skeleton, etc.)


def add_landmarks(fig, landmarks, mesh_data, offset=0.08):
    mesh_center = np.array([
        np.mean(mesh_data["x"]),
        np.mean(mesh_data["y"]),
        np.mean(mesh_data["z"]),
    ])
    for idx, pt in enumerate(landmarks, start=1):
        point = np.array([pt["x"], pt["y"], pt["z"]])
        direction = point - mesh_center
        direction = direction / (np.linalg.norm(direction) + 1e-6)
        offset_point = point + direction * offset

        fig.add_trace(go.Scatter3d(
            x=[offset_point[0]], y=[offset_point[1]], z=[offset_point[2]],
            mode="markers+text",
            marker=dict(size=16, color="#F5EDE8", line=dict(width=2, color="#1F1A18")),
            text=[str(idx)],
            textposition="middle center",
            textfont=dict(size=12, color="#1F1A18", family="Arial Black"),
            hovertemplate=f"<b>{idx}. {pt['name']}</b><br>{pt['desc']}<extra></extra>",
            showlegend=False,
        ))


def mesh_trace(mesh_data, color, name, opacity=1.0):
    verts = np.array([mesh_data["x"], mesh_data["y"], mesh_data["z"]]).T
    faces = np.array([mesh_data["i"], mesh_data["j"], mesh_data["k"]]).T
    return go.Mesh3d(
        x=verts[:, 0], y=verts[:, 1], z=verts[:, 2],
        i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
        color=color, opacity=opacity,
        lighting=dict(ambient=0.45, diffuse=0.9, specular=0.3, roughness=0.5),
        hoverinfo="x+y+z", name=name, showlegend=True,
    )


with col_3d:
    st.subheader("3D preview")

    x_range = [-1.2, 1.2]
    y_range = [-1.2, 1.2]
    z_range = [-1.2, 1.2]

    if selected == "cardiovascular":
        mesh_data = load_heart_mesh()

        y_vals = np.array(mesh_data["y"])
        y_min, y_max = y_vals.min(), y_vals.max()
        intensity = (y_vals - y_min) / (y_max - y_min)

        fig = go.Figure(data=[go.Mesh3d(
            x=mesh_data["x"], y=mesh_data["y"], z=mesh_data["z"],
            i=mesh_data["i"], j=mesh_data["j"], k=mesh_data["k"],
            intensity=intensity,
            colorscale=[
                [0.0, "#9E3A3A"],
                [0.65, "#9E3A3A"],
                [0.8, "#7A4A6E"],
                [1.0, "#3B6FC2"],
            ],
            showscale=False,
            opacity=1.0,
            lighting=dict(ambient=0.35, diffuse=0.9, specular=0.25, roughness=0.65, fresnel=0.1),
            flatshading=False,
            hoverinfo="skip",
        )])

        landmarks = real_heart_landmarks()
        add_landmarks(fig, landmarks, mesh_data)

    elif selected == "nervous":
        mesh_data = load_brain_mesh()

        z_vals = np.array(mesh_data["z"])
        z_min, z_max = z_vals.min(), z_vals.max()
        intensity = (z_vals - z_min) / (z_max - z_min)

        fig = go.Figure(data=[go.Mesh3d(
            x=mesh_data["x"], y=mesh_data["y"], z=mesh_data["z"],
            i=mesh_data["i"], j=mesh_data["j"], k=mesh_data["k"],
            intensity=intensity,
            colorscale=[
                [0.0, "#7A9E5A"],
                [0.5, "#B08A6E"],
                [1.0, "#9B7FC2"],
            ],
            showscale=False,
            opacity=1.0,
            lighting=dict(ambient=0.45, diffuse=0.85, specular=0.3, roughness=0.55),
            flatshading=False,
            hoverinfo="skip",
        )])

        landmarks = real_brain_landmarks()
        add_landmarks(fig, landmarks, mesh_data)

    elif selected == "respiratory":
        mesh_data = load_lungs_mesh()

        verts = np.array([mesh_data["x"], mesh_data["y"], mesh_data["z"]]).T
        faces = np.array([mesh_data["i"], mesh_data["j"], mesh_data["k"]]).T

        x_vals = verts[:, 0]
        y_vals = verts[:, 1]
        x_min, x_max = x_vals.min(), x_vals.max()
        y_min, y_max = y_vals.min(), y_vals.max()

        x_norm = (x_vals - x_min) / (x_max - x_min)
        y_norm = (y_vals - y_min) / (y_max - y_min)
        intensity = (x_norm * 0.7) + (y_norm * 0.3)

        fig = go.Figure(data=[go.Mesh3d(
            x=verts[:, 0], y=verts[:, 1], z=verts[:, 2],
            i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
            intensity=intensity,
            colorscale=[
                [0.0, "#B85C5C"],
                [0.35, "#D89A9A"],
                [0.65, "#E8C4A8"],
                [1.0, "#F0B0B8"],
            ],
            showscale=False,
            opacity=1.0,
            lighting=dict(ambient=0.4, diffuse=0.9, specular=0.35, roughness=0.5),
            flatshading=False,
            hoverinfo="skip",
        )])

        landmarks = real_lungs_landmarks()
        add_landmarks(fig, landmarks, mesh_data)

    elif selected == "renal":
        kidney_data = load_kidney_system()

        fig = go.Figure(data=[
            mesh_trace(kidney_data["right_shell"], "#D9A090", "Right kidney (capsule/cortex)", 0.22),
            mesh_trace(kidney_data["right_column_hilum"], "#8A4A45", "Right kidney (column/hilum)", 0.5),
            mesh_trace(kidney_data["right_pyramids"], "#E8935E", "Right kidney (pyramids)", 1.0),
            mesh_trace(kidney_data["left"], "#C9998E", "Left kidney", 1.0),
            mesh_trace(kidney_data["ureter"], "#E8D4A8", "Ureter", 1.0),
        ])

        landmarks = real_kidney_landmarks()
        add_landmarks(fig, landmarks, kidney_data["right_shell"], offset=0.015)

    elif selected == "digestive":
        dig = load_digestive_system()
        anchors = dig["_anchors"]
        esophagus_top = np.array(anchors["esophageal"]) + np.array([0, 0.35, 0])

        stomach_x, stomach_y, stomach_z = stomach_shape(anchors["esophageal"], anchors["gastric"], anchors["duodenal"])
        esophagus_x, esophagus_y, esophagus_z = esophagus_shape(esophagus_top.tolist(), anchors["esophageal"])

        fig = go.Figure(data=[
            mesh_trace(dig["liver"], "#8A3B2E", "Liver", 0.85),
            mesh_trace(dig["pancreas"], "#D9A05B", "Pancreas"),
            mesh_trace(dig["pancreatic_ducts"], "#E8C88A", "Pancreatic ducts"),
            mesh_trace(dig["gallbladder"], "#5A8A5A", "Gallbladder"),
            mesh_trace(dig["duodenum"], "#C77B5E", "Duodenum"),
            mesh_trace(dig["jejunum_ileum"], "#D9A88E", "Jejunum/Ileum"),
            mesh_trace(dig["large_intestine"], "#B5624F", "Large intestine"),
            mesh_trace(dig["appendix"], "#B5624F", "Appendix"),
            go.Surface(x=stomach_x, y=stomach_y, z=stomach_z,
                       colorscale=[[0, "#D9695A"], [1, "#D9695A"]], showscale=False, opacity=1.0,
                       name="Stomach", showlegend=True, hoverinfo="x+y+z"),
            go.Surface(x=esophagus_x, y=esophagus_y, z=esophagus_z,
                       colorscale=[[0, "#C98A6E"], [1, "#C98A6E"]], showscale=False, opacity=0.9,
                       name="Esophagus", showlegend=True, hoverinfo="x+y+z"),
        ])

        landmarks = real_digestive_landmarks()
        add_landmarks(fig, landmarks, dig["liver"], offset=0.02)

    elif selected == "skeletal":
        skeletal_view = st.radio("View", ["Full skeleton", "Skull"], horizontal=True, key="skeletal_view")
        view_suffix = skeletal_view

        if skeletal_view == "Skull":
            skull_raw = load_skull_mesh_standalone()
            verts = np.array([skull_raw["x"], skull_raw["y"], skull_raw["z"]]).T
            faces = np.array([skull_raw["i"], skull_raw["j"], skull_raw["k"]]).T

            fig = go.Figure(data=[go.Mesh3d(
                x=verts[:, 0], y=verts[:, 1], z=verts[:, 2],
                i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
                color="#EAE0C8",
                lighting=dict(ambient=0.5, diffuse=0.85, specular=0.3, roughness=0.5),
                hoverinfo="x+y+z",
            )])
            all_skel_landmarks = real_skeletal_landmarks()
            landmarks = all_skel_landmarks[6:]
            add_landmarks(fig, landmarks, skull_raw, offset=0.03)

        else:
            skel = load_skeletal_axial_appendicular()
            ribcage = load_ribcage_mesh()

            fig = go.Figure(data=[
                mesh_trace(skel["spine"], "#E8DCC0", "Spine"),
                mesh_trace(skel["pelvis"], "#D9CBA8", "Pelvis"),
                mesh_trace(skel["right_leg"], "#F0E4C8", "Right leg"),
                mesh_trace(skel["left_leg"], "#F0E4C8", "Left leg"),
                mesh_trace(skel["knee_ligaments"], "#C97A6E", "Knee ligaments"),
                mesh_trace(ribcage, "#DCD0B0", "Ribcage"),
            ])
            all_skel_landmarks = real_skeletal_landmarks()
            landmarks = all_skel_landmarks[:6]
            add_landmarks(fig, landmarks, skel["spine"], offset=0.02)

    elif selected == "muscular":
        muscular_view = st.radio("View", ["Leg", "Upper body"], horizontal=True, key="muscular_view")
        view_suffix = muscular_view

        if muscular_view == "Upper body":
            ub = load_upper_body_system()
            fig = go.Figure(data=[
                mesh_trace(ub["bones"], "#E8DCC0", "Bones", 0.6),
                mesh_trace(ub["deltoid"], "#C9524A", "Deltoid"),
                mesh_trace(ub["pectoralis_major"], "#B5624F", "Pectoralis major"),
                mesh_trace(ub["biceps_brachii"], "#D9846E", "Biceps brachii"),
                mesh_trace(ub["triceps_brachii"], "#A83E3E", "Triceps brachii"),
                mesh_trace(ub["trapezius"], "#8A5A5A", "Trapezius"),
                mesh_trace(ub["latissimus_dorsi"], "#C97A6E", "Latissimus dorsi"),
                mesh_trace(ub["rectus_abdominis"], "#B5726A", "Rectus abdominis"),
                mesh_trace(ub["external_oblique"], "#D99A8E", "External oblique"),
            ])
            landmarks = real_upper_body_landmarks()
            add_landmarks(fig, landmarks, ub["bones"], offset=0.02)
        else:
            musc = load_muscular_leg_system()
            fig = go.Figure(data=[
                mesh_trace(musc["bones"], "#E8DCC0", "Bones", 0.6),
                mesh_trace(musc["quadriceps"], "#C9524A", "Quadriceps"),
                mesh_trace(musc["hamstrings"], "#B5624F", "Hamstrings"),
                mesh_trace(musc["adductors"], "#D9846E", "Adductors"),
                mesh_trace(musc["glutes"], "#A83E3E", "Glutes"),
                mesh_trace(musc["deep_hip_rotators"], "#8A5A5A", "Deep hip rotators"),
                mesh_trace(musc["hip_flexors"], "#C97A6E", "Hip flexors"),
                mesh_trace(musc["calf"], "#B5726A", "Calf"),
                mesh_trace(musc["lower_leg"], "#D99A8E", "Lower leg"),
            ])
            landmarks = real_muscular_leg_landmarks()
            add_landmarks(fig, landmarks, musc["bones"], offset=0.02)

    elif selected == "endocrine":
        endo = load_endocrine_system()
        dig_endo = load_digestive_system()
        endocrine_view = st.radio("View", ["Brain", "Neck & Chest", "Abdomen", "Reproductive"], horizontal=True, key="endocrine_view")
        view_suffix = endocrine_view

        all_endo_landmarks = real_endocrine_landmarks()

        if endocrine_view == "Brain":
            fig = go.Figure(data=[
                mesh_trace(endo["pituitary"], "#D9A05B", "Pituitary gland"),
                mesh_trace(endo["pineal"], "#8A7BC2", "Pineal gland"),
                mesh_trace(endo["hypothalamus"], "#7A9E5A", "Hypothalamus"),
            ])
            landmarks = [all_endo_landmarks[0], all_endo_landmarks[1], all_endo_landmarks[2]]
            add_landmarks(fig, landmarks, endo["pituitary"], offset=0.03)

        elif endocrine_view == "Neck & Chest":
            (rx, ry, rz), (lx, ly, lz) = thyroid_shape(endo["_thyroid_anchor"])
            para = parathyroid_shapes(endo["_thyroid_anchor"])
            fig = go.Figure(data=[
                go.Surface(x=rx, y=ry, z=rz, colorscale=[[0, "#D9695A"], [1, "#D9695A"]],
                           showscale=False, name="Thyroid (right lobe)", showlegend=True, hoverinfo="skip"),
                go.Surface(x=lx, y=ly, z=lz, colorscale=[[0, "#D9695A"], [1, "#D9695A"]],
                           showscale=False, name="Thyroid (left lobe)", showlegend=True, hoverinfo="skip"),
                *[go.Surface(x=gx, y=gy, z=gz, colorscale=[[0, "#C9A05B"], [1, "#C9A05B"]],
                             showscale=False, name="Parathyroid gland", showlegend=(i == 0), hoverinfo="skip")
                  for i, (gx, gy, gz) in enumerate(para)],
                mesh_trace(endo["thymus_R"], "#C9998E", "Thymus (right lobe)"),
                mesh_trace(endo["thymus_L"], "#C9998E", "Thymus (left lobe)"),
            ])
            landmarks = [all_endo_landmarks[8], all_endo_landmarks[9], all_endo_landmarks[10], all_endo_landmarks[11]]
            add_landmarks(fig, landmarks, endo["thymus_R"], offset=0.03)

        elif endocrine_view == "Abdomen":
            fig = go.Figure(data=[
                mesh_trace(endo["adrenal_R"], "#B5624F", "Adrenal gland (right)"),
                mesh_trace(endo["adrenal_L"], "#B5624F", "Adrenal gland (left)"),
                mesh_trace(dig_endo["pancreas"], "#D9A05B", "Pancreas"),
            ])
            landmarks = [all_endo_landmarks[3], all_endo_landmarks[4], all_endo_landmarks[5]]
            add_landmarks(fig, landmarks, endo["adrenal_R"], offset=0.03)

        else:
            ovary_anchor = [all_endo_landmarks[12]["x"], all_endo_landmarks[12]["y"], all_endo_landmarks[12]["z"]]
            (orx, ory, orz), (olx, oly, olz) = ovary_shapes(ovary_anchor)
            fig = go.Figure(data=[
                mesh_trace(endo["testis_R"], "#D9A88E", "Testis (right)"),
                mesh_trace(endo["testis_L"], "#D9A88E", "Testis (left)"),
                go.Surface(x=orx, y=ory, z=orz, colorscale=[[0, "#C97AA0"], [1, "#C97AA0"]],
                           showscale=False, name="Ovary (right)", showlegend=True, hoverinfo="skip"),
                go.Surface(x=olx, y=oly, z=olz, colorscale=[[0, "#C97AA0"], [1, "#C97AA0"]],
                           showscale=False, name="Ovary (left)", showlegend=True, hoverinfo="skip"),
            ])
            landmarks = [all_endo_landmarks[6], all_endo_landmarks[7], all_endo_landmarks[12]]
            add_landmarks(fig, landmarks, endo["testis_R"], offset=0.03)

        all_x = np.concatenate([np.ravel(t.x) for t in fig.data if hasattr(t, "x") and t.x is not None])
        all_y = np.concatenate([np.ravel(t.y) for t in fig.data if hasattr(t, "y") and t.y is not None])
        all_z = np.concatenate([np.ravel(t.z) for t in fig.data if hasattr(t, "z") and t.z is not None])
        pad = 0.03
        x_range = [float(all_x.min()) - pad, float(all_x.max()) + pad]
        y_range = [float(all_y.min()) - pad, float(all_y.max()) + pad]
        z_range = [float(all_z.min()) - pad, float(all_z.max()) + pad]

    elif selected == "lymphatic":
        lymph_view = st.radio("View", ["Organs", "Lymph node structure"], horizontal=True, key="lymph_view")
        view_suffix = lymph_view
        all_lymph_landmarks = real_lymphatic_landmarks()

        if lymph_view == "Lymph node structure":
            node = load_lymph_node_structure()
            fig = go.Figure(data=[
                mesh_trace(node["capsule"], "#C9998E", "Capsule", 0.4),
                mesh_trace(node["medulla"], "#B5624F", "Medulla"),
                mesh_trace(node["afferent_vessel"], "#8A7BC2", "Afferent vessel"),
                mesh_trace(node["efferent_vessel"], "#7A9E5A", "Efferent vessel"),
            ])
            landmarks = all_lymph_landmarks[3:7]
            add_landmarks(fig, landmarks, node["capsule"], offset=0.15)
        else:
            lymph = load_lymphatic_organs()
            fig = go.Figure(data=[
                mesh_trace(lymph["spleen"], "#B5624F", "Spleen"),
                mesh_trace(lymph["tonsil_L"], "#C9998E", "Palatine tonsil (left)"),
                mesh_trace(lymph["tonsil_R"], "#C9998E", "Palatine tonsil (right)"),
            ])
            landmarks = all_lymph_landmarks[0:3]
            add_landmarks(fig, landmarks, lymph["spleen"], offset=0.03)

        all_x = np.concatenate([np.ravel(t.x) for t in fig.data if hasattr(t, "x") and t.x is not None])
        all_y = np.concatenate([np.ravel(t.y) for t in fig.data if hasattr(t, "y") and t.y is not None])
        all_z = np.concatenate([np.ravel(t.z) for t in fig.data if hasattr(t, "z") and t.z is not None])
        pad = 0.03
        x_range = [float(all_x.min()) - pad, float(all_x.max()) + pad]
        y_range = [float(all_y.min()) - pad, float(all_y.max()) + pad]
        z_range = [float(all_z.min()) - pad, float(all_z.max()) + pad]

    elif selected == "reproductive":
        repro_view = st.radio("View", ["Male", "Female", "Female (cross-section)"], horizontal=True, key="repro_view")
        view_suffix = repro_view

        if repro_view == "Male":
            male = load_male_reproductive_system()
            fig = go.Figure(data=[
                mesh_trace(male["prostate"], "#B5624F", "Prostate"),
                mesh_trace(male["seminal_vesicle_R"], "#C9998E", "Seminal vesicle (right)"),
                mesh_trace(male["seminal_vesicle_L"], "#C9998E", "Seminal vesicle (left)"),
                mesh_trace(male["epididymis_R"], "#8A7BC2", "Epididymis (right)"),
                mesh_trace(male["epididymis_L"], "#8A7BC2", "Epididymis (left)"),
                mesh_trace(male["testis_R"], "#D9A88E", "Testis (right)"),
                mesh_trace(male["testis_L"], "#D9A88E", "Testis (left)"),
                mesh_trace(male["corpus_cavernosum"], "#D9695A", "Corpus cavernosum"),
                mesh_trace(male["corpus_spongiosum"], "#E8A08E", "Corpus spongiosum"),
                mesh_trace(male["glans_penis"], "#C9524A", "Glans penis"),
            ])

        elif repro_view == "Female":
            female = load_female_reproductive_system()
            fig = go.Figure(data=[
                mesh_trace(female["uterus_system"], "#C9998E", "Uterus, tubes, cervix, vagina"),
                mesh_trace(female["ovary_A"], "#C97AA0", "Ovary"),
                mesh_trace(female["ovary_B"], "#C97AA0", "Ovary"),
            ])

        else:
            female_x = load_female_reproductive_xsection()
            fig = go.Figure(data=[
                mesh_trace(female_x["uterus_system_xsection"], "#C9998E", "Uterus, tubes, cervix, vagina (cross-section)"),
                mesh_trace(female_x["ovary_A"], "#C97AA0", "Ovary"),
                mesh_trace(female_x["ovary_B"], "#C97AA0", "Ovary"),
            ])

        landmarks = []

        all_x = np.concatenate([np.ravel(t.x) for t in fig.data if hasattr(t, "x") and t.x is not None])
        all_y = np.concatenate([np.ravel(t.y) for t in fig.data if hasattr(t, "y") and t.y is not None])
        all_z = np.concatenate([np.ravel(t.z) for t in fig.data if hasattr(t, "z") and t.z is not None])
        pad = 0.03
        x_range = [float(all_x.min()) - pad, float(all_x.max()) + pad]
        y_range = [float(all_y.min()) - pad, float(all_y.max()) + pad]
        z_range = [float(all_z.min()) - pad, float(all_z.max()) + pad]

    elif selected == "integumentary":
        view_suffix = ""
        skin_parts = load_real_skin_model()

        all_verts_x = np.concatenate([skin_parts[n]["x"] for n in skin_parts])
        all_verts_y = np.concatenate([skin_parts[n]["y"] for n in skin_parts])
        all_verts_z = np.concatenate([skin_parts[n]["z"] for n in skin_parts])

        traces = []
        for name, part_data in skin_parts.items():
            verts = np.array([part_data["x"], part_data["y"], part_data["z"]]).T
            faces = np.array([part_data["i"], part_data["j"], part_data["k"]]).T
            traces.append(go.Mesh3d(
                x=verts[:, 0], y=verts[:, 1], z=verts[:, 2],
                i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
                vertexcolor=part_data["vertexcolor"],
                opacity=1.0,
                lighting=dict(ambient=0.55, diffuse=0.8, specular=0.15, roughness=0.7),
                hoverinfo="skip", showlegend=False,
            ))

        fig = go.Figure(data=traces)

        landmarks = real_integumentary_landmarks()
        skin_center_ref = {"x": all_verts_x, "y": all_verts_y, "z": all_verts_z}
        add_landmarks(fig, landmarks, skin_center_ref, offset=0.08)

        pad = 0.05
        x_range = [float(all_verts_x.min()) - pad, float(all_verts_x.max()) + pad]
        y_range = [float(all_verts_y.min()) - pad, float(all_verts_y.max()) + pad]
        z_range = [float(all_verts_z.min()) - pad, float(all_verts_z.max()) + pad]

    else:
        x, y, z, colorscale = get_shape_for_system(selected)
        fig = go.Figure(data=[go.Surface(x=x, y=y, z=z, colorscale=colorscale, showscale=False)])

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=x_range),
            yaxis=dict(visible=False, range=y_range),
            zaxis=dict(visible=False, range=z_range),
            camera=dict(eye=dict(x=0, y=-2.8, z=0.4)),
            dragmode="orbit",
            aspectmode="cube",
        ),
        margin=dict(l=40, r=40, t=20, b=20),
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, use_container_width=True)

    if selected == "cardiovascular":
        st.caption("Heart model: HannahNewey / University of Dundee — CC BY-NC-SA")
    elif selected == "nervous":
        st.caption("Brain model: Johnson J / NIH 3D — CC BY")
    elif selected == "respiratory":
        st.caption("Respiratory model: kbrowne / NIH 3D (Visible Human Project) — CC BY")
    elif selected == "renal":
        st.caption("Kidney model: Human Reference Atlas / NIH 3D (Visible Human Male) — CC BY")
    elif selected == "digestive":
        st.caption("Liver/pancreas/intestines: Human Reference Atlas / NIH 3D (Visible Human Male) — CC BY. Stomach/esophagus: stylized placeholder, not yet based on a real model.")
    elif selected == "skeletal":
        st.caption("Spine/pelvis/legs/skull/ribcage: Human Reference Atlas / NIH 3D (Visible Human Male) — CC BY. Arms not yet included.")
    elif selected == "muscular":
        st.caption("Leg muscles: Andreassen et al. 2023, Visible Human Male, University of Denver — CC BY 4.0. Upper body: BodyParts3D/Anatomography, DBCLS Japan — CC BY-SA 2.1.")
    elif selected == "endocrine":
        st.caption("Pituitary, pineal, hypothalamus, thymus, adrenals, testes: BodyParts3D/Anatomography, DBCLS Japan — CC BY-SA 2.1. Pancreas: NIH 3D Human Reference Atlas — CC BY. Thyroid/parathyroid/ovaries: stylized placeholders, not yet based on real models.")
    elif selected == "lymphatic":
        st.caption("Spleen, tonsils, lymph node structure: Human Reference Atlas / NIH 3D (Visible Human Male) — CC BY. Thymus is covered under the Endocrine system. Named lymph node chains aren't included — no open-licensed model of the full node network exists.")
    elif selected == "reproductive":
        st.caption("Male organs: BodyParts3D/Anatomography, DBCLS Japan — CC BY-SA 2.1. Female organs: Catherine Vallance, Leiden University Medical Center via AnatomyTOOL — CC BY.")
    elif selected == "integumentary":
        st.caption("Skin cross-section (layers, follicle, glands, vessels): stylized diagram — no open-licensed microscopic skin model exists.") 
        
with col_legend:
    if landmarks:
        st.caption("Tap a number:")
        legend_box = st.container(height=520, border=True)
        with legend_box:
            for idx, pt in enumerate(landmarks, start=1):
                if st.button(f"{idx}. {pt['name']}", key=f"landmark_{selected}_{view_suffix}_{idx}", use_container_width=True):
                    st.session_state["active_landmark"] = (selected, view_suffix, idx)

            active = st.session_state.get("active_landmark")
            if active and active[0] == selected and active[1] == view_suffix:
                pt = landmarks[active[2] - 1]
                st.info(f"**{active[2]}. {pt['name']}**\n\n{pt['desc']}")

with col_info:
    def render_sections(sections):
        if not sections:
            st.write("Content coming soon.")
            return
        for section in sections:
            st.markdown(f"#### {section['heading']}")
            for point in section["points"]:
                st.markdown(f"- {point}")
            st.markdown("")

    if "info_panel" not in st.session_state:
        st.session_state["info_panel"] = None

    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        if st.button("🔬 Physiology", use_container_width=True):
            st.session_state["info_panel"] = "physiology"

    with btn_col2:
        if st.button("🧫 Histology", use_container_width=True):
            st.session_state["info_panel"] = "histology"

    content_box = st.container(height=520, border=True)

    with content_box:
        if st.session_state["info_panel"] == "physiology":
            render_sections(sysdata.get("physiology"))
        elif st.session_state["info_panel"] == "histology":
            render_sections(sysdata.get("histology"))
        else:
            st.caption("Select Physiology or Histology to view detailed content.")