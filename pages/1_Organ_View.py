import json
import streamlit as st

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

import numpy as np
import plotly.graph_objects as go

st.subheader("3D preview")

u = np.linspace(0, 2 * np.pi, 60)
v = np.linspace(0, np.pi, 60)
U, V = np.meshgrid(u, v)

# Heart-shaped parametric surface
x = np.sin(V) * (15 * np.sin(U) - 4 * np.sin(3 * U))
y = np.sin(V) * (15 * np.cos(U) - 5 * np.cos(2 * U) - 2 * np.cos(3 * U) - np.cos(4 * U))
z = 8 * np.cos(V) * 6

# Normalize so it's a reasonable, consistent size
x = x / np.abs(x).max()
y = y / np.abs(y).max()
z = z / np.abs(z).max()

fig = go.Figure(data=[go.Surface(x=x, y=y, z=z, colorscale="Reds", showscale=False)])

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