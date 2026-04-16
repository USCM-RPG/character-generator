import json
from pathlib import Path

for file in Path(".").rglob("*.json"):
    print(f"Formating:  {file}\n")
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(file, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,          
            ensure_ascii=False
        )
        f.write("\n")