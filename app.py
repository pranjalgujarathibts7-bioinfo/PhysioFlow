import base64
from pathlib import Path

import streamlit as st


st.set_page_config(page_title="PhysioFlow", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")


@st.cache_data(show_spinner=False)
def anatomy_hero_data() -> str:
    image = Path(__file__).parent / "assets" / "anatomy-hero-reference.png"
    return "data:image/png;base64," + base64.b64encode(image.read_bytes()).decode("ascii")


def feature_card(icon: str, title: str, body: str) -> None:
    st.markdown(
        f'<div class="feature-card"><div class="feature-icon">{icon}</div><h3>{title}</h3><p>{body}</p></div>',
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap');
      .stApp { background:radial-gradient(circle at 50% 46%,rgba(168,83,67,.22),transparent 29rem),radial-gradient(circle at 4% 87%,rgba(126,82,68,.12),transparent 23rem),linear-gradient(135deg,#0d0c0c,#171211 49%,#251815); color:#F5EDE8; }
      header[data-testid="stHeader"] { background:transparent; } #MainMenu, footer { visibility:hidden; }
      [data-testid="stAppViewContainer"] > .main { padding-top:0; }
      .block-container { max-width:1210px; padding:1.5rem 2rem 2.75rem; }
      .brand { display:flex; align-items:center; justify-content:center; gap:.58rem; margin:.1rem 0 1.5rem; }
      .brand-mark { display:grid; place-items:center; width:42px; height:42px; border-radius:13px; font-size:24px; background:linear-gradient(145deg,#ff8e9b,#e9566e); box-shadow:0 10px 24px rgba(234,86,109,.28); }
      .brand-name { font:700 1.72rem/1 Outfit,sans-serif; letter-spacing:-.05em; color:#ff9aa5; }
      .eyebrow { text-align:center; margin:0 0 .45rem; font:600 1rem/1.3 'DM Sans',sans-serif; color:#D9C8BE; }
      .eyebrow strong { color:#ff8d9a; letter-spacing:.035em; }
      .hero-title { max-width:1200px; margin:0 auto 1.65rem; text-align:center; font:800 clamp(2.1rem,3vw,3rem)/1.13 Outfit,sans-serif; letter-spacing:-.047em; color:#F5EDE8; }
      .hero-title .accent { color:#ff8494; }
      .feature-stack { display:flex; flex-direction:column; gap:1.7rem; padding-top:2.55rem; }
      .feature-card { min-height:126px; padding:1.1rem 1.15rem; border-radius:17px; border:1px solid rgba(207,177,162,.25); background:linear-gradient(135deg,rgba(39,29,27,.90),rgba(27,21,20,.76)); box-shadow:0 15px 35px rgba(0,0,0,.24),inset 0 1px rgba(255,255,255,.04); backdrop-filter:blur(10px); }
      .feature-icon { font-size:1.38rem; margin-bottom:.35rem; }.feature-card h3 { margin:0 0 .35rem; color:#F5EDE8; font:700 1.08rem/1.18 Outfit,sans-serif; letter-spacing:-.02em; }.feature-card p { margin:0; color:#C9B8AE; font:400 .87rem/1.43 'DM Sans',sans-serif; }
      .anatomy-visual { position:relative; height:430px; display:flex; align-items:flex-end; justify-content:center; overflow:hidden; }
      .anatomy-visual:before { content:""; position:absolute; width:390px; height:390px; bottom:-10px; border-radius:50%; background:radial-gradient(circle,rgba(201,116,88,.19),rgba(116,65,52,.07) 45%,transparent 68%); border:1px solid rgba(222,163,140,.18); }
      .anatomy-visual:after { content:""; position:absolute; width:280px; height:280px; bottom:40px; border-radius:50%; border:1px solid rgba(237,139,177,.24); }
      .anatomy-visual img { position:relative; z-index:1; height:415px; width:auto; max-width:100%; object-fit:contain; mix-blend-mode:multiply; filter:brightness(1.65) saturate(.92) contrast(1.07); transform:translateY(15px); }
      .model-hint { text-align:center; margin-top:-.7rem; color:#C9B8AE; font:500 .76rem 'DM Sans',sans-serif; letter-spacing:.055em; text-transform:uppercase; }
      .stButton { display:flex; justify-content:center; margin-top:1.55rem; }.stButton>button { min-height:57px; padding:0 2rem; border:0; border-radius:999px; color:#fff; font:700 1rem Outfit,sans-serif; letter-spacing:.015em; background:linear-gradient(100deg,#e9876c,#d94f69 58%,#be3e62); box-shadow:0 10px 0 rgba(115,39,48,.18),0 17px 32px rgba(204,76,97,.30); }.trust-line { margin:1.1rem 0 0; text-align:center; color:#AFA098; font:400 .82rem 'DM Sans',sans-serif; }
      @media(max-width:800px) { .block-container { padding:1.1rem 1rem 2rem; }.hero-title { font-size:2.22rem; }.feature-stack { padding-top:0; gap:.85rem; }.feature-card { min-height:0; }.anatomy-visual { height:365px; }.anatomy-visual img { height:355px; } }
    </style>
    <div class="brand"><span class="brand-mark">🧬</span><span class="brand-name">PhysioFlow</span></div>
    <p class="eyebrow"><strong>PHYSIOFLOW</strong> · Your interactive anatomy &amp; physiology studio</p>
    <h1 class="hero-title">Journey inside. Master anatomy. <span class="accent">Learn by exploring.</span></h1>
    """,
    unsafe_allow_html=True,
)

left, center, right = st.columns([1, 1.25, 1], gap="large", vertical_alignment="center")

with left:
    st.markdown('<div class="feature-stack">', unsafe_allow_html=True)
    feature_card("◈", "3D interactive systems", "Explore detailed, layered models of every major body system in real time.")
    feature_card("✦", "Active learning tools", "Turn exploration into recall with focused flashcards and quizzes.")
    st.markdown("</div>", unsafe_allow_html=True)

with center:
    st.markdown(f'<div class="anatomy-visual"><img src="{anatomy_hero_data()}" alt="Human anatomy"/></div>', unsafe_allow_html=True)
    st.markdown('<p class="model-hint">Explore every system, from anatomy to assessment</p>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="feature-stack">', unsafe_allow_html=True)
    feature_card("⌁", "Integrated histology", "Move from whole-system anatomy to cellular detail in a single study flow.")
    feature_card("◎", "Your study path", "Build understanding at your pace and test your knowledge as you go.")
    st.markdown("</div>", unsafe_allow_html=True)

if st.button("Start learning  →", key="start_learning", type="primary"):
    st.switch_page("pages/0_Organ_Systems.py")

st.markdown('<p class="trust-line">Interactive models · system-by-system learning · knowledge checks</p>', unsafe_allow_html=True)
