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
st.info("3D view and detailed facts will go here soon.")