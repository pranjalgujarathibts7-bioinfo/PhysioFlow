import json
import os

root_json = r"C:\Pranjal\physioflow\data\systems.json"
pages_json = r"C:\Pranjal\physioflow\pages\data\systems.json"

print("--- Checking Root JSON ---")
if os.path.exists(root_json):
    with open(root_json, 'r', encoding='utf-8') as f:
        d = json.load(f)
    print("Keys in cardiovascular:", list(d.get("cardiovascular", {}).keys()))
else:
    print("Root JSON missing!")

print("\n--- Checking Pages Folder JSON ---")
if os.path.exists(pages_json):
    with open(pages_json, 'r', encoding='utf-8') as f:
        d_p = json.load(f)
    print("Keys in pages cardiovascular:", list(d_p.get("cardiovascular", {}).keys()))
else:
    print("No stray copy in pages folder.")
