import json
import sys
from pathlib import Path
from collections import Counter

# --------------------------------------------------
# STEP 1: Add backend directory to Python path
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR.parents[1]

sys.path.insert(0, str(BACKEND_DIR))

# --------------------------------------------------
# STEP 2: Import required libraries
# --------------------------------------------------

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from goal_model import detect_goals


# --------------------------------------------------
# STEP 3: Define file paths and class labels
# --------------------------------------------------

DATASET_PATH = BASE_DIR / "final_test_queries.json"
RESULTS_PATH = BASE_DIR / "final_test_results.json"

LABELS = [
    "security",
    "business",
    "technical",
    "user_experience",
    "general"
]


# --------------------------------------------------
# STEP 4: Main evaluation function
# --------------------------------------------------

def main():

    # Load final test dataset
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        test_data = json.load(file)

    expected = []
    predicted = []
    detailed_results = []

    print("\n========== FINAL INDEPENDENT TEST ==========\n")

    print("Total queries loaded:", len(test_data))

    # --------------------------------------------------
    # STEP 5: Predict the goal for every query
    # --------------------------------------------------

    for index, item in enumerate(test_data, start=1):

        query = item["query"]
        expected_goal = item["expected_goal"]

        # Get prediction from goal detection model
        result = detect_goals(query)

        predicted_goal = result["primary_goal"]

        correct = expected_goal == predicted_goal

        expected.append(expected_goal)
        predicted.append(predicted_goal)

        # Store individual prediction details
        detailed_results.append({
            "id": index,
            "query": query,
            "expected_goal": expected_goal,
            "predicted_goal": predicted_goal,
            "correct": correct,
            "goal_weights": result.get("goal_weights", {})
        })

        status = "CORRECT" if correct else "INCORRECT"

        print(f"\n{index:03d}. {status}")
        print("Query:", query)
        print("Expected:", expected_goal)
        print("Predicted:", predicted_goal)
        print("-" * 60)

    # --------------------------------------------------
    # STEP 6: Calculate evaluation metrics
    # --------------------------------------------------

    accuracy = accuracy_score(expected, predicted)

    matrix = confusion_matrix(
        expected,
        predicted,
        labels=LABELS
    )

    report = classification_report(
        expected,
        predicted,
        labels=LABELS,
        output_dict=True,
        zero_division=0
    )

    correct_count = sum(
        item["correct"] for item in detailed_results
    )

    incorrect_count = len(test_data) - correct_count

    # --------------------------------------------------
    # STEP 7: Display final summary
    # --------------------------------------------------

    print("\n\n========== FINAL TEST SUMMARY ==========\n")

    print("Total queries:", len(test_data))
    print("Correct predictions:", correct_count)
    print("Incorrect predictions:", incorrect_count)

    print(f"Accuracy: {accuracy * 100:.2f}%")

    # --------------------------------------------------
    # STEP 8: Display classification report
    # --------------------------------------------------

    print("\n========== CLASSIFICATION REPORT ==========\n")

    print(
        classification_report(
            expected,
            predicted,
            labels=LABELS,
            zero_division=0
        )
    )

    # --------------------------------------------------
    # STEP 9: Display confusion matrix
    # --------------------------------------------------

    print("\n========== CONFUSION MATRIX ==========\n")

    print("Label order:", LABELS)
    print(matrix)

    # --------------------------------------------------
    # STEP 10: Prepare results JSON
    # --------------------------------------------------

    results = {

        "dataset": "final_independent_test",

        "total_queries": len(test_data),

        "correct_predictions": correct_count,

        "incorrect_predictions": incorrect_count,

        "accuracy": round(float(accuracy), 4),

        "labels": LABELS,

        "confusion_matrix": matrix.tolist(),

        "classification_report": report,

        "class_distribution": dict(
            Counter(
                item["expected_goal"]
                for item in test_data
            )
        ),

        "detailed_results": detailed_results
    }

    # --------------------------------------------------
    # STEP 11: Save results to JSON file
    # --------------------------------------------------

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n==========================================")
    print("FINAL EVALUATION COMPLETED")
    print("==========================================")

    print("\nDetailed results saved to:")
    print(RESULTS_PATH)


# --------------------------------------------------
# STEP 12: Execute program
# --------------------------------------------------

if __name__ == "__main__":
    main()