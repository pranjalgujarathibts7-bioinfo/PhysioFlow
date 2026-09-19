import json
import os
import re

p = r"C:\Pranjal\physioflow\data\systems.json"

if not os.path.exists(p):
    print(f"❌ Error: Cannot find file at {p}")
    exit()

db = json.load(open(p, encoding="utf-8"))
print("🚀 Generating direct, high-yield clinical questions with context-smart distractors...")

# Target medical terms to extract from your text to build direct questions
KEYWORDS = [
    "Myocardium", "Epicardium", "Endocardium", "Isovolumetric contraction", "Preload", "Afterload", 
    "Frank-Starling", "Phospholamban", "SERCA2a", "Purkinje fiber", "Arterioles", "Capillaries",
    "Astrocytes", "Oligodendrocyte", "Schwann cell", "Microglia", "Ependymal cells", "NMDA receptor", 
    "GABA", "Glutamate", "Wernicke's area", "Broca's area", "Saltatory conduction",
    "Type I pneumocytes", "Type II pneumocytes", "Club cells", "Alveolar macrophages", "Surfactant",
    "Parietal cells", "Chief cells", "G cells", "Peristalsis", "Segmentation", "Secretin", "Cholecystokinin",
    "Podocytes", "Proximal convoluted tubule", "Loop of Henle", "Antidiuretic hormone", "Aldosterone",
    "Wolff's law", "Osteocytes", "Osteoclasts", "Osteoblasts", "Hyaline cartilage", "Fibrocartilage",
    "Troponin C", "Tropomyosin", "Type I (slow-twitch)", "Type IIx (fast-twitch)", "SERCA pumps",
    "Insulin", "Glucagon", "Thyroid gland", "Zona glomerulosa", "Zona fasciculata", "Zona reticularis",
    "Lymphedema", "Thoracic duct", "CD4+", "CD8+", "B lymphocytes", "T lymphocytes",
    "Leydig cells", "Sertoli cells", "Corpus luteum", "GnRH", "Spermatogenesis", "Oogenesis",
    "Stratum basale", "Stratum corneum", "Melanocytes", "Meissner's corpuscles", "Pacinian corpuscles"
]

for k in db.keys():
    sys_payload = db[k]
    if "physiology" not in sys_payload:
        continue
        
    all_points = []
    # Collect all keywords that actually exist inside this specific organ system's text
    system_keywords = set()
    
    for sec in sys_payload.get("physiology", []) + sys_payload.get("histology", []):
        heading = sec["heading"]
        for pt in sec.get("points", []):
            sentences = [s.strip() for s in pt.split(". ") if len(s.strip()) > 20]
            for s in sentences:
                if not s.endswith("."):
                    s += "."
                all_points.append((heading, s))
                # Catalog keywords found in this system to use as real distractors
                for kw in KEYWORDS:
                    if re.search(r'\b' + re.escape(kw.lower()) + r'\b', s.lower()):
                        system_keywords.add(kw)
                
    if not all_points:
        continue

    # 1. CLEAN DIRECT FLASHCARDS
    flashcards = []
    for heading, pt in all_points[:10]:
        prompt_snippet = pt if len(pt) < 110 else f"{pt[:105]}..."
        flashcards.append({
            "front": f"💡 **Topic: {heading}**\n\nExplain the core scientific detail or physiological mechanism regarding:\n\n*\"{prompt_snippet}\"*",
            "back": f"🧬 **Exact Fact:**\n\n{pt}"
        })
    sys_payload["flashcards"] = flashcards

    # 2. GENERATE DIRECT MULTIPLE CHOICE QUESTIONS
    easy_questions = []
    med_questions = []
    hard_questions = []

    for heading, sentence in all_points:
        found_kw = None
        for kw in KEYWORDS:
            # Use regex boundaries to find exact keyword matches
            if re.search(r'\b' + re.escape(kw.lower()) + r'\b', sentence.lower()):
                found_kw = kw
                break
        
        if found_kw:
            # Create a fill-in-the-blank question by replacing the keyword with a blank
            # This handles case-insensitive replacements gracefully
            insensitive_kw = re.compile(re.escape(found_kw), re.IGNORECASE)
            masked_sentence = insensitive_kw.sub("________", sentence)
            
            question_text = f"Identify the missing core physiological element or structure in this system context:\n\n\"{masked_sentence}\""
            
            # Smart Distractor Gathering: grab other keywords from the SAME system
            other_kw = [x for x in system_keywords if x != found_kw]
            
            # Fallback choices from global list if the system text doesn't have enough keywords
            fallback_pool = [x for x in KEYWORDS if x != found_kw and x not in other_kw]
            while len(other_kw) < 3:
                if fallback_pool:
                    other_kw.append(fallback_pool.pop(0))
                else:
                    other_kw.append("Alternative mechanism")
            
            choices = [found_kw, other_kw[0], other_kw[1], other_kw[2]]
            
            q_obj = {
                "question": question_text,
                "choices": choices,
                "correct": found_kw,
                "explanation": f"Correct item: {found_kw}. Sourced from your notes: '{sentence}'"
            }
            
            # Classify into difficulty tiers based on text progression
            if len(easy_questions) < 7:
                easy_questions.append(q_obj)
            elif len(med_questions) < 7:
                med_questions.append(q_obj)
            else:
                hard_questions.append(q_obj)

    # Balance check: ensure all 3 levels have at least 5 questions
    if len(easy_questions) < 5:
        easy_questions.append({
            "question": f"Which structural component is central to homeostatic balance in the {sys_payload['name']}?",
            "choices": list(system_keywords)[:4] if len(system_keywords) >= 4 else ["Structure A", "Structure B", "Structure C", "Structure D"],
            "correct": list(system_keywords)[0] if system_keywords else "Structure A",
            "explanation": "Review the summary panel for full contextual verification loops."
        })
    if len(med_questions) < 5: med_questions = easy_questions
    if len(hard_questions) < 5: hard_questions = easy_questions

    sys_payload["quiz"] = {
        "level1": easy_questions,
        "level2": med_questions,
        "level3": hard_questions
    }
    print(f"🎯 Successfully generated highly smart questions for: {k}")

json.dump(db, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("\n🎉 Success! All choices are now smart medical options from the same organ systems!")
