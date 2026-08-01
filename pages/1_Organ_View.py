import json
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from utils.shapes import get_shape_for_system, real_heart_landmarks, real_brain_landmarks, real_lungs_landmarks
from utils.mesh_loader import load_heart_mesh, load_brain_mesh, load_lungs_mesh

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


def add_landmarks(fig, landmarks, mesh_data):
    mesh_center = np.array([
        np.mean(mesh_data["x"]),
        np.mean(mesh_data["y"]),
        np.mean(mesh_data["z"]),
    ])
    for idx, pt in enumerate(landmarks, start=1):
        point = np.array([pt["x"], pt["y"], pt["z"]])
        direction = point - mesh_center
        direction = direction / (np.linalg.norm(direction) + 1e-6)
        offset_point = point + direction * 0.08

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


with col_3d:
    st.subheader("3D preview")

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
        landmarks = real_lungs_landmarks()
        add_landmarks(fig, landmarks, mesh_data)

    else:
        x, y, z, colorscale = get_shape_for_system(selected)
        fig = go.Figure(data=[go.Surface(x=x, y=y, z=z, colorscale=colorscale, showscale=False)])

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[-1.2, 1.2]),
            yaxis=dict(visible=False, range=[-1.2, 1.2]),
            zaxis=dict(visible=False, range=[-1.2, 1.2]),
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

with col_legend:
    if selected in ("cardiovascular", "nervous", "respiratory") and landmarks:
        st.caption("Tap a number:")
        legend_box = st.container(height=520, border=True)
        with legend_box:
            for idx, pt in enumerate(landmarks, start=1):
                if st.button(f"{idx}. {pt['name']}", key=f"landmark_{selected}_{idx}", use_container_width=True):
                    st.session_state["active_landmark"] = (selected, idx)

            active = st.session_state.get("active_landmark")
            if active and active[0] == selected:
                pt = landmarks[active[1] - 1]
                st.info(f"**{active[1]}. {pt['name']}**\n\n{pt['desc']}")

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