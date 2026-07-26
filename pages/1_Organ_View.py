import json
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from utils.shapes import get_shape_for_system, anatomical_heart, heart_landmarks_v2, heart_vessels

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

col_3d, col_info = st.columns([3, 2])

with col_3d:
    st.subheader("3D preview")

    if selected == "cardiovascular":
        from utils.mesh_loader import load_heart_mesh

        mesh_data = load_heart_mesh()

        y_vals = np.array(mesh_data["y"])
        y_min, y_max = y_vals.min(), y_vals.max()
        # Normalize so the top ~25% of the mesh (where vessels are) shades toward blue
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
        )])

    else:
        x, y, z, colorscale = get_shape_for_system(selected)
        fig = go.Figure(data=[go.Surface(x=x, y=y, z=z, colorscale=colorscale, showscale=False)])

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(eye=dict(x=0, y=-2.2, z=0.3)),
            dragmode="orbit",
            aspectmode="cube",
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, use_container_width=True)

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

    st.markdown("")

    if st.session_state["info_panel"] == "physiology":
        render_sections(sysdata.get("physiology"))
    elif st.session_state["info_panel"] == "histology":
        render_sections(sysdata.get("histology"))
    else:
        st.caption("Select Physiology or Histology to view detailed content.")