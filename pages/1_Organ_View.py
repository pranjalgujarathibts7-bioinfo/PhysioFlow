import json
import streamlit as st
import plotly.graph_objects as go
from utils.shapes import get_shape_for_system, anatomical_heart, heart_landmarks

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
        from utils.shapes import anatomical_heart, heart_vessels, heart_landmarks_v2

        x, y, z = anatomical_heart()
        fig = go.Figure(data=[go.Surface(
            x=x, y=y, z=z,
            colorscale=[[0, "#8A2A2A"], [0.5, "#B23A3A"], [1, "#CC5555"]],
            showscale=False,
            lighting=dict(ambient=0.55, diffuse=0.85, specular=0.4, roughness=0.4),
            hoverinfo="skip",
        )])

        for vessel in heart_vessels():
            fig.add_trace(go.Surface(
                x=vessel["x"], y=vessel["y"], z=vessel["z"],
                colorscale=[[0, vessel["color"]], [1, vessel["color"]]],
                showscale=False,
                hoverinfo="skip",
            ))

        for pt in heart_landmarks_v2():
            fig.add_trace(go.Scatter3d(
                x=[pt["x"]], y=[pt["y"]], z=[pt["z"]],
                mode="markers+text",
                marker=dict(size=5, color="#F5EDE8", line=dict(width=1, color="#000000")),
                text=[pt["name"]],
                textposition="top center",
                textfont=dict(size=10, color="#F5EDE8"),
                hovertemplate=f"<b>{pt['name']}</b><br>{pt['desc']}<extra></extra>",
                showlegend=False,
            ))

    else:
        x, y, z, colorscale = get_shape_for_system(selected)
        fig = go.Figure(data=[go.Surface(x=x, y=y, z=z, colorscale=colorscale, showscale=False)])

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(eye=dict(x=0, y=-2.2, z=0.3)),
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