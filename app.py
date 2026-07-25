import json
import streamlit as st

st.set_page_config(page_title="PhysioFlow", page_icon="🫀", layout="wide")


def load_css(path: str):
    with open(path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css("assets/style.css")

# ---- Hero section ----
st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #2E211C 0%, #3A2A22 100%);
        border-radius: 20px;
        padding: 1.75rem 2rem;
        margin-bottom: 1.5rem;
    ">
        <h2 style="margin: 0 0 4px 0; color: #F5EDE8;">Welcome back 👋</h2>
        <p style="margin: 0; color: #C9B8AE;">Ready to explore a new organ system today?</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Organ system grid ----
st.subheader("Organ systems")

with open("data/systems.json", encoding="utf-8") as f:
    systems = json.load(f)

keys = list(systems.keys())
cols_per_row = 4

for i in range(0, len(keys), cols_per_row):
    row_keys = keys[i:i + cols_per_row]
    cols = st.columns(cols_per_row)

    for col, key in zip(cols, row_keys):
        sysdata = systems[key]
        with col:
            st.markdown(
                f"""
                <div style="
                    background: #1F1A18;
                    border: 1px solid #3D3532;
                    border-radius: 16px;
                    padding: 1.1rem 1.2rem;
                ">
                    <div style="font-size: 1.6rem;">{sysdata['icon']}</div>
                    <h4 style="margin: 0.5rem 0 0.2rem 0; color: #F5EDE8;">{sysdata['name']}</h4>
                    <p style="margin: 0; color: #9C8D85; font-size: 0.85rem;">{sysdata['summary']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button("Explore →", key=f"btn_{key}")