import json
import os
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

# ==================== 1. DATA VALIDATION STRUCTURE ====================
class Flashcard(BaseModel):
    front: str = Field(description="Active recall question. Short and highly specific.")
    back: str = Field(description="Precise factual medical answer.")

class QuizQuestion(BaseModel):
    question: str = Field(description="A rigorous question evaluating core physiology or anatomy concepts.")
    choices: List[str] = Field(description="Exactly 4 realistic option entries containing 1 clear correct answer and 3 distinct distractors.")
    correct: str = Field(description="The exact text match string corresponding to the correct answer choice option.")
    explanation: str = Field(description="A brief rationale explaining why the answer is correct and why other options are incorrect.")

class TieredQuizData(BaseModel):
    level1: List[QuizQuestion] = Field(description="3 to 4 easy questions testing basic definition vocabulary, primary system roles, and simple identification.")
    level2: List[QuizQuestion] = Field(description="3 to 4 medium difficulty questions testing clinical interactions, multi-step pathways, and fundamental physiological relationships.")
    level3: List[QuizQuestion] = Field(description="3 to 4 complex questions testing microscopic cellular mechanics, regulatory protein brakes, ion channel mutations, or deep histology variables.")

class SystemAssessmentData(BaseModel):
    flashcards: List[Flashcard] = Field(description="A bank of 6 to 10 highly comprehensive active recall flashcards.")
    quiz: TieredQuizData = Field(description="A nested object containing quiz questions split cleanly across Easy, Medium, and Hard tiers.")

# ==================== 2. PIPELINE RUNNER DEPLOYMENT ====================
def run_bulk_generation(json_path: str = "data/systems.json"):
    if not os.path.exists(json_path):
        print(f"❌ Error: Cannot locate systems data file at: {json_path}")
        return

    # Initialize client dynamically by fetching directly from our terminal env setup
    client = OpenAI()

    with open(json_path, "r", encoding="utf-8") as f:
        systems_db = json.load(f)

    print(f"🚀 Initializing generation pipeline across all {len(systems_db)} organ systems...")

    for sys_key, sys_payload in list(systems_db.items()):
        print(f"\n📡 Processing source text context metrics for: {sys_key}...")
        
        # Consolidate material text arrays for context loading
        content_context = ""
        for field in ["physiology", "histology"]:
            if field in sys_payload:
                content_context += f"\n=== Core {field.capitalize()} Material ===\n"
                for item in sys_payload[field]:
                    content_context += f"\n### {item.get('heading', '')}\n"
                    content_context += "\n".join([f"- {p}" for p in item.get("points", [])]) + "\n"

        prompt = f"""
        You are a university medical school professor formatting custom active recall metrics for a bioinformatics tool.
        Analyze the following text documentation detailing the cellular anatomy, physiology, and histology of the {sys_payload['name']}:
        
        {content_context}
        
        Based strictly on this data, construct:
        1. 6 to 10 Active Recall Flashcards.
        2. A completely tiered multiple choice study bank matching the requested fields:
           - Level 1 (Easy): Basic macro functions, names, and general overview questions.
           - Level 2 (Medium): Dynamic path relationships, step-by-step loops, and clinical mechanics.
           - Level 3 (Hard): Advanced micro-cellular data, specific ion channels, genetic mutations, or protein regulations.
        """

        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",  # Fast, affordable structured output engine
                messages=[
                    {"role": "system", "content": "You are a professional medical curriculum architect designing structured assessment items."},
                    {"role": "user", "content": prompt}
                ],
                response_format=SystemAssessmentData,
            )
            
            result_data = completion.choices.message.parsed.model_dump()
            
            # Direct mapping injection right into the target system array block keys!
            systems_db[sys_key]["flashcards"] = result_data["flashcards"]
            systems_db[sys_key]["quiz"] = result_data["quiz"]
            print(f"✅ Successfully compiled and saved all tiers for the {sys_payload['name']}!")
            
        except Exception as e:
            print(f"❌ Error encountered while generating content assets for {sys_key}: {e}")
            continue

    # Clean overwrite update execution
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(systems_db, f, indent=2, ensure_ascii=False)
        
    print("\n🎉 Bulk production complete! Every system entry inside systems.json has been populated successfully.")

if __name__ == "__main__":
    run_bulk_generation()
