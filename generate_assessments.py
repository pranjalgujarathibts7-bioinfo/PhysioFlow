import json
import os
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

# ==================== 1. DATA VALIDATION STRUCTURE ====================
class Flashcard(BaseModel):
    front: str = Field(description="Active recall question about histology/physiology. Short and specific.")
    back: str = Field(description="Concise, precise factual answer.")

class QuizQuestion(BaseModel):
    question: str = Field(description="A rigorous multiple-choice question testing high-yield core physiology or histology.")
    choices: List[str] = Field(description="Exactly 4 realistic options, containing 1 correct answer and 3 distinct distractors.")
    correct: str = Field(description="The exact string match of the correct option choice.")
    explanation: str = Field(description="A brief rationale explaining why the answer is correct.")

class SystemAssessmentData(BaseModel):
    flashcards: List[Flashcard] = Field(description="A bank of 6-10 high-quality flashcards.")
    quiz: List[QuizQuestion] = Field(description="A bank of 4-6 multiple-choice questions.")


# ==================== 2. INITIALIZE CLIENT DIRECTLY ====================
# No terminal setups needed! Paste your key directly as a string inside the quotes here:
# Paste your real, exact API key inside the quotes below
client = OpenAI(api_key="sk-proj-YOUR_ACTUAL_SECRET_KEY_FROM_DASHBOARD")


# ==================== 3. GENERATION PIPELINE ====================
def generate_assessment_for_system(system_key: str, system_data: dict) -> dict:
    print(f"🤖 Processing and generating assessment items for: {system_key}...")
    
    # Pack up both physiology and histology notes as context for the AI
    content_context = ""
    for sec_type in ["physiology", "histology"]:
        if sec_type in system_data:
            content_context += f"\n=== Core {sec_type.capitalize()} Material ===\n"
            for section in system_data[sec_type]:
                content_context += f"\n### {section.get('heading', '')}\n"
                for point in section.get("points", []):
                    content_context += f"- {point}\n"
            
    prompt = f"""
    You are an expert medical education instructor. 
    Analyze the following source material detailing the physiology and histology of the {system_data['name']}:
    
    {content_context}
    
    Based strictly on this data, generate:
    1. A set of 6 to 10 active-recall Flashcards (front/back pairings).
    2. A Quiz with 4 to 6 advanced Multiple Choice Questions (MCQs).
    """

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",  # Highly cost-efficient for structural parsing
        messages=[
            {"role": "system", "content": "You are a professional medical curriculum designer specializing in high-yield anatomy board questions."},
            {"role": "user", "content": prompt}
        ],
        response_format=SystemAssessmentData,
    )
    
    return completion.choices.message.parsed.model_dump()


def run_pipeline(json_path: str = "data/systems.json"):
    if not os.path.exists(json_path):
        print(f"❌ Error: Could not locate data file at: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        systems_db = json.load(f)

    for sys_key, sys_payload in list(systems_db.items()):
        if "physiology" not in sys_payload and "histology" not in sys_payload:
            print(f"⚠️ Skipping '{sys_key}' - no source text found.")
            continue
            
        try:
            assessment_payload = generate_assessment_for_system(sys_key, sys_payload)
            systems_db[sys_key]["flashcards"] = assessment_payload["flashcards"]
            systems_db[sys_key]["quiz"] = assessment_payload["quiz"]
        except Exception as e:
            print(f"❌ Error generating items for {sys_key}: {e}")
            continue

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(systems_db, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Successfully updated systems.json with dynamic flashcards and quizzes!")

if __name__ == "__main__":
    # Force the absolute path to your root project data directory
    run_pipeline(json_path="C:/Pranjal/physioflow/data/systems.json")
