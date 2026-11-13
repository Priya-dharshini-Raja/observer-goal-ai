import json
import sys
from pathlib import Path
from collections import Counter

# --------------------------------------------------
# STEP 1: Locate project directories
# --------------------------------------------------

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parents[1]

sys.path.insert(0, str(BACKEND_DIR))


# --------------------------------------------------
# STEP 2: Import required libraries
# --------------------------------------------------

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)

from goal_model import detect_goals


# --------------------------------------------------
# STEP 3: Define dataset and result paths
# --------------------------------------------------

DATASET_PATH = CURRENT_DIR / "independent_test_queries.json"

OUTPUT_PATH = CURRENT_DIR / "independent_test_results.json"

CATEGORIES = [
    "security",
    "business",
    "technical",
    "user_experience",
    "general"
]


# --------------------------------------------------
# STEP 4: Load the independent evaluation dataset
# --------------------------------------------------

with open(DATASET_PATH, "r", encoding="utf-8") as file:
    dataset = json.load(file)

print("\n========== INDEPENDENT TEST EVALUATION ==========\n")

print("Total queries loaded:", len(dataset))


# --------------------------------------------------
# STEP 5: Validate the dataset
# --------------------------------------------------

if not isinstance(dataset, list):
    raise ValueError("Dataset must be a list of query dictionaries.")

for index, item in enumerate(dataset, start=1):

    if "query" not in item or "expected_goal" not in item:
        raise ValueError(f"Invalid dataset entry at position {index}")

    if item["expected_goal"] not in CATEGORIES:
        raise ValueError(
            f"Unknown category at position {index}: "
            f"{item['expected_goal']}"
        )

class_distribution = Counter(
    item["expected_goal"] for item in dataset
)

print("\n========== DATASET DISTRIBUTION ==========\n")

for category in CATEGORIES:
    print(f"{category}: {class_distribution[category]}")


# --------------------------------------------------
# STEP 6: Run predictions
# --------------------------------------------------

y_true = []
y_pred = []
results = []

print("\n========== MODEL PREDICTIONS ==========\n")

for index, item in enumerate(dataset, start=1):

    query = item["query"]
    expected_goal = item["expected_goal"]

    # Predict observer goal using the existing model
    prediction = detect_goals(query)

    predicted_goal = prediction.get("primary_goal", "general")

    # Store actual and predicted categories
    y_true.append(expected_goal)
    y_pred.append(predicted_goal)

    is_correct = expected_goal == predicted_goal

    # Save detailed prediction
    results.append({
        "id": index,
        "query": query,
        "expected_goal": expected_goal,
        "predicted_goal": predicted_goal,
        "goal_weights": prediction.get("goal_weights", {}),
        "correct": is_correct
    })

    status = "CORRECT" if is_correct else "INCORRECT"

    print(f"\n{index:03d}. {status}")
    print("Query:", query)
    print("Expected:", expected_goal)
    print("Predicted:", predicted_goal)

    print("-" * 60)


# --------------------------------------------------
# STEP 7: Calculate evaluation metrics
# --------------------------------------------------

total = len(y_true)

if total == 0:
    raise ValueError("The evaluation dataset is empty.")

accuracy = accuracy_score(y_true, y_pred)

correct_count = sum(
    actual == predicted
    for actual, predicted in zip(y_true, y_pred)
)

incorrect_count = total - correct_count


# --------------------------------------------------
# STEP 8: Calculate category-wise metrics
# --------------------------------------------------

precision, recall, f1, support = precision_recall_fscore_support(
    y_true,
    y_pred,
    labels=CATEGORIES,
    zero_division=0
)


# Macro averages
macro_precision, macro_recall, macro_f1, _ = (
    precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=CATEGORIES,
        average="macro",
        zero_division=0
    )
)


# Weighted averages
weighted_precision, weighted_recall, weighted_f1, _ = (
    precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=CATEGORIES,
        average="weighted",
        zero_division=0
    )
)


# --------------------------------------------------
# STEP 9: Display overall evaluation summary
# --------------------------------------------------

print("\n\n========== INDEPENDENT TEST SUMMARY ==========\n")

print("Total queries:", total)
print("Correct predictions:", correct_count)
print("Incorrect predictions:", incorrect_count)

print(f"Accuracy: {accuracy * 100:.2f}%")


# --------------------------------------------------
# STEP 10: Display classification metrics
# --------------------------------------------------

print("\n========== CATEGORY-WISE METRICS ==========\n")

print(
    f"{'Category':<20}"
    f"{'Precision':<12}"
    f"{'Recall':<12}"
    f"{'F1-score':<12}"
    f"{'Support':<10}"
)

for index, category in enumerate(CATEGORIES):

    print(
        f"{category:<20}"
        f"{precision[index]:<12.2f}"
        f"{recall[index]:<12.2f}"
        f"{f1[index]:<12.2f}"
        f"{support[index]:<10}"
    )


# --------------------------------------------------
# STEP 11: Display average metrics
# --------------------------------------------------

print("\n========== AVERAGE METRICS ==========\n")

print(f"Macro Precision: {macro_precision:.4f}")
print(f"Macro Recall: {macro_recall:.4f}")
print(f"Macro F1-score: {macro_f1:.4f}")

print(f"Weighted Precision: {weighted_precision:.4f}")
print(f"Weighted Recall: {weighted_recall:.4f}")
print(f"Weighted F1-score: {weighted_f1:.4f}")


# --------------------------------------------------
# STEP 12: Generate confusion matrix
# --------------------------------------------------

matrix = confusion_matrix(
    y_true,
    y_pred,
    labels=CATEGORIES
)

print("\n========== CONFUSION MATRIX ==========\n")

print(f"{'Expected / Predicted':<22}", end="")

for category in CATEGORIES:
    print(f"{category[:10]:<13}", end="")

print()

for index, category in enumerate(CATEGORIES):

    print(f"{category:<22}", end="")

    for value in matrix[index]:
        print(f"{value:<13}", end="")

    print()


# --------------------------------------------------
# STEP 13: Display detailed classification report
# --------------------------------------------------

print("\n========== CLASSIFICATION REPORT ==========\n")

print(
    classification_report(
        y_true,
        y_pred,
        labels=CATEGORIES,
        zero_division=0
    )
)


# --------------------------------------------------
# STEP 14: Prepare final results
# --------------------------------------------------

final_results = {

    "dataset": "new_manually_curated_independent_test",

    "total_queries": total,

    "correct_predictions": correct_count,

    "incorrect_predictions": incorrect_count,

    "accuracy_percentage": round(accuracy * 100, 2),

    "macro_precision": round(float(macro_precision), 4),

    "macro_recall": round(float(macro_recall), 4),

    "macro_f1_score": round(float(macro_f1), 4),

    "weighted_precision": round(float(weighted_precision), 4),

    "weighted_recall": round(float(weighted_recall), 4),

    "weighted_f1_score": round(float(weighted_f1), 4),

    "categories": CATEGORIES,

    "class_distribution": dict(class_distribution),

    "confusion_matrix": matrix.tolist(),

    "classification_report": classification_report(
        y_true,
        y_pred,
        labels=CATEGORIES,
        output_dict=True,
        zero_division=0
    ),

    "detailed_results": results
}


# --------------------------------------------------
# STEP 15: Save results to JSON
# --------------------------------------------------

with open(OUTPUT_PATH, "w", encoding="utf-8") as file:

    json.dump(
        final_results,
        file,
        indent=4,
        ensure_ascii=False
    )


# --------------------------------------------------
# STEP 16: Final confirmation
# --------------------------------------------------

print("\n==============================================")
print("INDEPENDENT EVALUATION COMPLETED")
print("==============================================")

print("\nResults saved successfully to:")

print(OUTPUT_PATH)