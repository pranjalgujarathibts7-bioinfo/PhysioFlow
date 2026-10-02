# 🧬 PhysioFlow

**A graduate-level, interactive atlas of human anatomy and physiology — built in Streamlit, with real 3D anatomical models, graduate-depth content, and active recall study tools.**

🔗 **Live app:** [physioflow-bioinfo.streamlit.app](https://physioflow-bioinfo.streamlit.app/)

---

## What this is

PhysioFlow covers all 11 major organ systems, each with:

- An interactive **3D model** built from real, open-licensed anatomical mesh data (not illustrations) — rendered with Plotly, with hover-labeled landmarks you can tap to learn
- **Graduate/master's-level physiology and histology content**, researched and written to go well beyond undergraduate textbook depth
- **Flashcards** for active recall, including the ability to add your own custom cards
- A **multiple-choice quiz** at three difficulty tiers (Level 1–3) per system

The front page, **Body Explorer**, is a rotating anatomical hero that opens the app — tap an organ to see what it is, or jump straight into the full system grid.

---

## Organ systems covered

| System | Icon | 3D Model Source |
|---|---|---|
| Cardiovascular | ❤️ | Sketchfab / HannahNewey — CC BY-NC-SA |
| Nervous | 🧠 | NIH 3D — CC BY |
| Respiratory | 🫁 | NIH 3D (Visible Human Project) — CC BY |
| Renal | 🫘 | NIH 3D Human Reference Atlas (Visible Human Male) — CC BY |
| Digestive | 🍽️ | NIH 3D "Body, Male" + stylized stomach/esophagus — CC BY |
| Skeletal | 🦴 | NIH 3D "Body, Male" + standalone skull/ribcage — CC BY |
| Muscular | 💪 | Andreassen et al. 2023 (leg) + BodyParts3D (upper body) — CC BY 4.0 / CC BY-SA 2.1 |
| Endocrine | ⚗️ | BodyParts3D + NIH 3D pancreas + stylized thyroid/parathyroid/ovaries — CC BY-SA 2.1 / CC BY |
| Lymphatic & Immune | 🛡️ | NIH 3D "Body, Male" — CC BY |
| Reproductive | 🌸 | BodyParts3D (male) + AnatomyTOOL/Leiden University (female) — CC BY-SA 2.1 / CC BY |
| Integumentary | 🧴 | E-learning UMCG (Sketchfab) — CC BY-NC-SA |

Every model's exact source and license is also cited in-app, directly under its 3D viewer. A few sub-structures (e.g. stomach/esophagus, thyroid/parathyroid/ovaries, named lymph node chains) don't have an open-licensed real model available anywhere, so those are clearly labeled as stylized placeholders rather than passed off as real anatomy.

---

## Tech stack

- **[Streamlit](https://streamlit.io/)** — app framework, multipage navigation
- **[Plotly](https://plotly.com/python/)** (`go.Mesh3d`, `go.Surface`) — interactive 3D rendering
- **[trimesh](https://trimesh.org/)** — mesh loading and processing
- **[Three.js](https://threejs.org/)** (embedded via `streamlit.components.v1.html`) — the rotating Body Explorer hero
- **NumPy** — mesh/landmark math

---

## Project structure

```
physioflow/
├── app.py                      # Entry point — Body Explorer hero + navigation
├── pages/
│   ├── 0_Organ_Systems.py      # Card grid of all 11 systems
│   └── 1_Organ_View.py         # 3D viewer, physiology/histology, flashcards, quiz
├── data/
│   └── systems.json            # All content: physiology, histology, flashcards, quizzes
├── models/
│   ├── <system>/                # Per-system mesh files (.glb/.stl/.gltf) + license.txt
│   └── hero/                    # Body Explorer model + license.txt
├── utils/
│   ├── shapes.py                # Landmark data, procedural/stylized shape generators
│   └── mesh_loader.py           # Mesh loading functions (@st.cache_resource)
└── assets/
    └── style.css                 # App-wide styling
```

---

## Content methodology

`data/systems.json` is written to graduate/master's-level depth, not lifted from any single source. Each system's physiology and histology content was researched across multiple NCBI StatPearls/Bookshelf references, then written out from scratch in original wording — never copied — for both learning quality and copyright reasons.

**Safe-editing workflow for content updates:** new content for a system is built as a standalone JSON file, merged into the full `systems.json` via a script that validates the result by re-parsing it as real JSON before it's ever delivered, then committed to git as its own checkpoint. This was used to build out all 11 systems' content one at a time.

---

## Running locally

```bash
git clone <your-repo-url>
cd physioflow
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
streamlit run app.py
```

---

## Known gaps

A few sub-structures don't have an open-licensed real model available anywhere and are clearly labeled in-app as stylized placeholders rather than real anatomy:

- Stomach & esophagus (digestive)
- Thyroid, parathyroid, ovaries (endocrine)
- Named lymph node chains — cervical/axillary/inguinal (lymphatic)
- Female reproductive landmarks — not yet added (source model is one unsegmented mesh)
- Arm bones (skeletal) — partial skeletal coverage

---

## License & attribution

Each 3D model's specific source and license is documented in its own `models/<system>/license.txt` and cited in-app. This project redistributes third-party anatomical data under CC BY / CC BY-SA / CC BY-NC-SA terms as specified per model — see individual license files for exact attribution requirements before reusing any model asset elsewhere.

All written physiology/histology content, flashcards, and quiz questions are original work.

---

*Built as a graduate-level self-study and portfolio project.*
