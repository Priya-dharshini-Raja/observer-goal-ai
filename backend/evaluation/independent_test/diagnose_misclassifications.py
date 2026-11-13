
import json
import sys
from pathlib import Path

# Locate backend directory
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent.parent

sys.path.insert(0, str(BACKEND_DIR))

from goal_model import detect_goals

# Load independent test results
RESULTS_PATH = CURRENT_DIR / "independent_test_results.json"

with open(RESULTS_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

print("\n========== MISCLASSIFICATION DIAGNOSIS ==========\n")

wrong_predictions = [
    result for result in data["results"]
    if not result["correct"]
]

print("Total incorrect predictions:", len(wrong_predictions))

for index, result in enumerate(wrong_predictions, start=1):

    query = result["query"]

    prediction = detect_goals(query)

    print(f"\nMISCLASSIFICATION {index}")
    print("-" * 65)

    print("Query:", query)
    print("Expected:", result["expected_goal"])
    print("Predicted:", result["predicted_goal"])

    print("\nKeyword Scores:")
    for goal, score in prediction.get("keyword_scores", {}).items():
        print(f"{goal}: {score}")

    print("\nSemantic Scores:")
    for goal, score in prediction.get("semantic_scores", {}).items():
        print(f"{goal}: {score}")

    print("\nSemantic Confidence:")
    for goal, score in prediction.get("semantic_confidence", {}).items():
        print(f"{goal}: {score}")

    print("\nHybrid Scores:")
    for goal, score in prediction.get("hybrid_scores", {}).items():
        print(f"{goal}: {score}")

    print("\n" + "=" * 65)

print("\nDiagnosis completed.")
