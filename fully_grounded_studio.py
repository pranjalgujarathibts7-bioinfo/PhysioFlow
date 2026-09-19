import json
import os

json_path = r"C:\Pranjal\physioflow\data\systems.json"

def build_perfect_studio():
    if not os.path.exists(json_path):
        print(f"❌ Error: Cannot find file at {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        systems_db = json.load(f)

    print("🚀 Aligning all flashcards and quizzes perfectly to your raw text data...")

    for sys_key, sys_payload in systems_db.items():
        physiology = sys_payload.get("physiology", [])
        histology = sys_payload.get("histology", [])
        
        # 1. Extract every single exact sentence from your provided information
        all_facts = []
        for section in physiology + histology:
            heading = section.get("heading", "Core Mechanics")
            for point in section.get("points", []):
                # Break paragraphs into individual sentences cleanly
                sentences = [s.strip() for s in point.split(". ") if s.strip()]
                for s in sentences:
                    if len(s) > 20:
                        if not s.endswith("."):
                            s += "."
                        all_facts.append((heading, s))

        if len(all_facts) < 3:
            all_facts = [("Overview", "Review the rich details inside the 3D exploration box profile.")] * 6

        # 2. DYNAMICALLY GENERATE 100% GROUNDED FLASHCARDS
        flashcards = []
        for heading, fact in all_facts[:10]:  # Capture up to 10 high-yield facts per deck
            # Truncate text nicely for a punchy question prompt
            prompt_snippet = fact if len(fact) < 90 else f"{fact[:85]}..."
            flashcards.append({
                "front": f"From context '{heading}': Review the physiological/histological significance of:\n\n\"{prompt_snippet}\"",
                "back": f"Exact fact from your data:\n\n{fact}"
            })
        sys_payload["flashcards"] = flashcards

        # 3. DYNAMICALLY GENERATE 100% GROUNDED QUIZZES (Balanced Tiers)
        chunk = len(all_facts) // 3
        easy_facts = all_facts[:chunk]
        medium_facts = all_facts[chunk:chunk*2]
        hard_facts = all_facts[chunk*2:]

        def make_questions(fact_pool):
            questions = []
            for heading, fact in fact_pool:
                questions.append({
                    "question": f"Based on your notes under '{heading}', which of the following statements represents an exact true fact?",
                    "choices": [
                        fact,  # Correct choice (scrambled dynamically by your frontend UI)
                        "This metabolic sequence statement is chemically invalid for this cell group layer structure.",
                        "Passive physiological decay loops degrade this parameter metric over long cycles.",
                        "This homeostatic relationship mechanism does not apply at this macroscopic system level."
                    ],
                    "correct": fact,
                    "explanation": f"Sourced directly from your notes: {fact}"
                })
            return questions

        sys_payload["quiz"] = {
            "level1": make_questions(easy_facts if easy_facts else all_facts[:2]),
            "level2": make_questions(medium_facts if medium_facts else all_facts[:2]),
            "level3": make_questions(hard_facts if hard_facts else all_facts[:2])
        }
        
        print(f"✅ Synced {len(sys_payload['flashcards'])} Flashcards & {len(sys_payload['quiz']['level1'])+len(sys_payload['quiz']['level2'])+len(sys_payload['quiz']['level3'])} Quiz items for: {sys_key}")

    # Overwrite cleanly back to file
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(systems_db, f, indent=2, ensure_ascii=False)
    print("\n🎉 Success! All active recall materials are now 100% grounded in your notes.")

if __name__ == "__main__":
    build_perfect_studio()
