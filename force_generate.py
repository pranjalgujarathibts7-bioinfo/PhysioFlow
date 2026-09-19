import json
import os
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

# 1. Output Validation Models
class Flashcard(BaseModel):
    front: str
    back: str

class QuizQuestion(BaseModel):
    question: str
    choices: List[str]
    correct: str
    explanation: str

class SystemAssessmentData(BaseModel):
    flashcards: List[Flashcard]
    quiz: List[QuizQuestion]

# 2. Initialize with your explicit text key string
# REPLACE THIS STRING WITH YOUR ACTUAL OPENAI KEY (e.g., "sk-proj-...")
API_KEY = "your_actual_key_here"

client = OpenAI(api_key=API_KEY)
json_path = r"C:\Pranjal\physioflow\data\systems.json"

def run():
    print("🚀 Starting direct generation sequence...")
    
    with open(json_path, "r", encoding="utf-8") as f:
        systems_db = json.load(f)
        
    cardio_data = systems_db.get("cardiovascular", {})
    
    # Bundle text blocks for context window routing
    context = ""
    for sec in ["physiology", "histology"]:
        if sec in cardio_data:
            for item in cardio_data[sec]:
                context += f"\n{item.get('heading','')}\n" + "\n".join(item.get("points", []))

    print("📡 Sending data payload to OpenAI API endpoint...")
    
    # We remove the try/except block on purpose so the terminal prints the exact error if it fails!
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional medical professor formatting quiz metrics."},
            {"role": "user", "content": f"Generate 5 flashcards and 3 multiple choice quiz questions based on this text:\n\n{context}"}
        ],
        response_format=SystemAssessmentData,
    )
    
    result = completion.choices.message.parsed.model_dump()
    
    # Inject directly into the structure layout map
    systems_db["cardiovascular"]["flashcards"] = result["flashcards"]
    systems_db["cardiovascular"]["quiz"] = result["quiz"]
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(systems_db, f, indent=2, ensure_ascii=False)
        
    print("🎉 Success! Check your Streamlit application layout now!")

if __name__ == "__main__":
    run()
