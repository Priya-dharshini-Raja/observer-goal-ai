
import json
import sys
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)

# Locate backend directory and import goal detection
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from goal_model import detect_goals

# Load validation dataset
DATASET_PATH = Path(__file__).parent / "validation_queries.json"

with open(DATASET_PATH, "r", encoding="utf-8") as file:
    dataset = json.load(file)

queries = dataset["queries"]

categories = [
    "security",
    "business",
    "technical",
    "user_experience",
    "general"
]

results = []
y_true = []
y_pred = []

print("\n========== VERSION 2 VALIDATION ==========\n")

# Run predictions
for item in queries:

    query = item["query"]
    expected_goal = item["expected"]

    prediction = detect_goals(query)
    predicted_goal = prediction.get("primary_goal", "general")

    y_true.append(expected_goal)
    y_pred.append(predicted_goal)

    is_correct = predicted_goal == expected_goal

    results.append({
        "query": query,
        "expected_goal": expected_goal,
        "predicted_goal": predicted_goal,
        "goal_weights": prediction.get("goal_weights", {}),
        "correct": is_correct
    })

    print(f"Query: {query}")
    print(f"Expected: {expected_goal}")
    print(f"Predicted: {predicted_goal}")
    print(f"Result: {'CORRECT' if is_correct else 'INCORRECT'}")
    print("-" * 55)


# Calculate evaluation metrics
total = len(y_true)

accuracy = accuracy_score(y_true, y_pred) if total else 0

precision, recall, f1, support = precision_recall_fscore_support(
    y_true,
    y_pred,
    labels=categories,
    zero_division=0
)

macro_precision, macro_recall, macro_f1, _ = (
    precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=categories,
        average="macro",
        zero_division=0
    )
)

weighted_precision, weighted_recall, weighted_f1, _ = (
    precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=categories,
        average="weighted",
        zero_division=0
    )
)

correct = sum(a == b for a, b in zip(y_true, y_pred))
incorrect = total - correct

# Overall summary
print("\n========== OVERALL SUMMARY ==========")

print(f"Total queries: {total}")
print(f"Correct predictions: {correct}")
print(f"Incorrect predictions: {incorrect}")
print(f"Accuracy: {accuracy * 100:.2f}%")

# Per-category metrics
print("\n========== CLASSIFICATION METRICS ==========")

print(
    f"{'Category':<20}"
    f"{'Precision':<12}"
    f"{'Recall':<12}"
    f"{'F1-score':<12}"
    f"{'Support':<10}"
)

for i, category in enumerate(categories):
    print(
        f"{category:<20}"
        f"{precision[i]:<12.2f}"
        f"{recall[i]:<12.2f}"
        f"{f1[i]:<12.2f}"
        f"{support[i]:<10}"
    )

# Average metrics
print("\n========== AVERAGE METRICS ==========")

print(f"Macro Precision:    {macro_precision:.4f}")
print(f"Macro Recall:       {macro_recall:.4f}")
print(f"Macro F1-score:     {macro_f1:.4f}")

print(f"Weighted Precision: {weighted_precision:.4f}")
print(f"Weighted Recall:    {weighted_recall:.4f}")
print(f"Weighted F1-score:  {weighted_f1:.4f}")

# Confusion matrix
matrix = confusion_matrix(
    y_true,
    y_pred,
    labels=categories
)

print("\n========== CONFUSION MATRIX ==========")

print(f"{'Expected / Predicted':<20}", end="")

for category in categories:
    print(f"{category[:10]:<13}", end="")

print()

for i, expected in enumerate(categories):
    print(f"{expected:<20}", end="")

    for j in range(len(categories)):
        print(f"{matrix[i][j]:<13}", end="")

    print()

# Detailed classification report
print("\n========== DETAILED CLASSIFICATION REPORT ==========")

print(classification_report(
    y_true,
    y_pred,
    labels=categories,
    zero_division=0
))

# Save validation results separately
OUTPUT_PATH = Path(__file__).parent / "validation_results.json"

with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
    json.dump({
        "total_queries": total,
        "correct_predictions": correct,
        "incorrect_predictions": incorrect,
        "accuracy_percentage": round(accuracy * 100, 2),
        "macro_precision": round(macro_precision, 4),
        "macro_recall": round(macro_recall, 4),
        "macro_f1_score": round(macro_f1, 4),
        "weighted_precision": round(weighted_precision, 4),
        "weighted_recall": round(weighted_recall, 4),
        "weighted_f1_score": round(weighted_f1, 4),
        "confusion_matrix": matrix.tolist(),
        "categories": categories,
        "results": results
    }, file, indent=4)

print(f"\nValidation results saved to: {OUTPUT_PATH}")
