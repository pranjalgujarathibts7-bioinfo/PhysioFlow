import json
import os

json_path = r"C:\Pranjal\physioflow\data\systems.json"

def run_cardio():
    if not os.path.exists(json_path):
        print(f"❌ Error: Cannot find file at {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        systems_db = json.load(f)

    # Clean, fully complete data block for the cardiovascular branch
    cardio_data = {
        "flashcards": [
            {
                "front": "What event marks the beginning of the isovolumetric contraction phase of the cardiac cycle?", 
                "back": "Ventricular pressure exceeding atrial pressure, which snaps the AV valves shut (generating the S1 heart sound)."
            },
            {
                "front": "What percentage of the end-diastolic volume is normally ejected per beat (ejection fraction)?", 
                "back": "Approximately 60%."
            },
            {
                "front": "What is operationally defined by the Frank-Starling mechanism?", 
                "back": "Increasing preload stretches sarcomeres toward optimal length, increasing cross-bridge interactions and troponin C calcium sensitivity to produce a stronger contraction without altering contractility."
            },
            {
                "front": "What regulatory protein acts as a brake on the SERCA2a pump at baseline?", 
                "back": "Phospholamban. PKA-mediated phosphorylation relieves this inhibition, accelerating Ca2+ reuptake and myocardial relaxation (lusitropy)."
            },
            {
                "front": "Which ion current carries the depolarization upstroke in sinoatrial (SA) node pacemaker cells?", 
                "back": "Calcium (Ca2+) current, unlike the sodium (Na+) current that drives working myocardium upstrokes."
            },
            {
                "front": "By Poiseuille's law, how is vascular resistance related to a blood vessel's radius?", 
                "back": "Resistance is inversely proportional to the fourth power of the vessel radius (R ∝ 1/r⁴)."
            },
            {
                "front": "What structural junctions concentrate at the transverse (plicate) segments of intercalated discs?", 
                "back": "Fascia adherens and desmosomes, which provide mechanical coupling between adjacent cardiomyocytes."
            },
            {
                "front": "Why can cardiac muscle not contract in the complete absence of extracellular calcium?", 
                "back": "Its sarcoplasmic reticulum stores are less extensive than skeletal muscle, making contraction fundamentally dependent on trigger calcium entering via L-type channels to trigger calcium-induced calcium release (CICR)."
            }
        ],
        "quiz": {
            "level1": [
                {
                    "question": "Which heart layer contains the bulk of the thick cardiac muscle tissue responsible for pumping blood?",
                    "choices": ["Epicardium", "Myocardium", "Endocardium", "Pericardium"],
                    "correct": "Myocardium",
                    "explanation": "The heart wall comprises the outer epicardium, the thick muscular middle myocardium, and the innermost endothelial endocardium."
                }
            ],
            "level2": [
                {
                    "question": "By Poiseuille's law, which section of the systemic circulation serves as the principal site of resistance regulation?",
                    "choices": ["Large elastic arteries", "Arterioles", "Capillaries", "Venules and veins"],
                    "correct": "Arterioles",
                    "explanation": "Because resistance is inversely proportional to the fourth power of the radius (R ∝ 1/r⁴), the substantial smooth muscle in arterioles allows them to markedly alter caliber and control resistance."
                }
            ],
            "level3": [
                {
                    "question": "During sympathetic stimulation, which molecular target is phosphorylated by Protein Kinase A to produce a lusitropic (accelerated relaxation) effect?",
                    "choices": ["Troponin C", "Ryanodine Receptors (RyR2)", "Phospholamban", "Inward-rectifier K+ channels (IK1)"],
                    "correct": "Phospholamban",
                    "explanation": "Phospholamban inhibits the SERCA2a pump at baseline. PKA-mediated phosphorylation relieves this brake, accelerating Ca2+ reuptake into the SR and driving myocardial relaxation."
                }
            ]
        }
    }

    # Safely inject directly into the cardiovascular key branch
    if "cardiovascular" in systems_db:
        print("📦 Injecting verified facts for the Cardiovascular System...")
        systems_db["cardiovascular"]["flashcards"] = cardio_data["flashcards"]
        systems_db["cardiovascular"]["quiz"] = cardio_data["quiz"]

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(systems_db, f, indent=2, ensure_ascii=False)
        print("✅ Cardiovascular System complete and successfully saved!")
    else:
        print("❌ Error: 'cardiovascular' key not found in systems.json")

if __name__ == "__main__":
    run_cardio()
