from pathlib import Path
import joblib
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve, auc

# ============================================================
# PATH
# ============================================================

root = Path(__file__).resolve().parents[1]
models = root / "models"

results = joblib.load(models / "model_results.joblib")

# ============================================================
# MODEL DATA
# ============================================================

names = list(results.keys())

accuracy = [results[x]["accuracy"] for x in names]
precision = [results[x]["precision"] for x in names]
recall = [results[x]["recall"] for x in names]
f1 = [results[x]["f1"] for x in names]

# ============================================================
# 1. OVERALL MODEL PERFORMANCE
# ============================================================

x = np.arange(len(names))
width = 0.18

plt.figure(figsize=(11, 6))

plt.bar(x - width * 1.5, accuracy, width, label="Accuracy")
plt.bar(x - width / 2, precision, width, label="Precision")
plt.bar(x + width / 2, recall, width, label="Recall")
plt.bar(x + width * 1.5, f1, width, label="F1 Score")

plt.xticks(x, names, fontsize=11)
plt.ylabel("Performance (%)", fontsize=12)
plt.xlabel("Machine Learning Models", fontsize=12)
plt.title(
    "Heart Disease Prediction - Model Performance Comparison",
    fontsize=16,
    fontweight="bold"
)

plt.ylim(0, 105)
plt.grid(axis="y", alpha=0.25)
plt.legend()

for values, offset in [
    (accuracy, -width * 1.5),
    (precision, -width / 2),
    (recall, width / 2),
    (f1, width * 1.5)
]:
    for i, value in enumerate(values):
        plt.text(
            i + offset,
            value + 1,
            f"{value:.1f}%",
            ha="center",
            fontsize=9
        )

plt.tight_layout()
plt.show()

# ============================================================
# 2. RANDOM FOREST CONFUSION MATRIX
# ============================================================

cm = results["Random Forest"]["confusion_matrix"]

plt.figure(figsize=(7, 6))

plt.imshow(cm)

plt.title(
    "Random Forest - Confusion Matrix",
    fontsize=16,
    fontweight="bold"
)

plt.xlabel("Predicted Class", fontsize=12)
plt.ylabel("Actual Class", fontsize=12)

plt.xticks(
    [0, 1],
    ["No Disease", "Disease"]
)

plt.yticks(
    [0, 1],
    ["No Disease", "Disease"]
)

for i in range(2):
    for j in range(2):
        plt.text(
            j,
            i,
            cm[i, j],
            ha="center",
            va="center",
            fontsize=18,
            fontweight="bold"
        )

plt.colorbar()
plt.tight_layout()
plt.show()

# ============================================================
# 3. ROC CURVE
# ============================================================

plt.figure(figsize=(9, 7))

for name in names:

    model = results[name]["model"]
    X_test = results[name]["X_test"]
    y_test = results[name]["y_test"]

    if hasattr(model, "predict_proba"):
        probability = model.predict_proba(X_test)[:, 1]
    else:
        probability = model.decision_function(X_test)

    fpr, tpr, _ = roc_curve(y_test, probability)

    roc_auc = auc(fpr, tpr)

    plt.plot(
        fpr,
        tpr,
        linewidth=2.5,
        label=f"{name} (AUC = {roc_auc:.3f})"
    )

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    linewidth=1.5,
    label="Random Classifier"
)

plt.title(
    "ROC Curve - Heart Disease Prediction Models",
    fontsize=16,
    fontweight="bold"
)

plt.xlabel("False Positive Rate", fontsize=12)
plt.ylabel("True Positive Rate", fontsize=12)

plt.legend(loc="lower right")
plt.grid(alpha=0.25)

plt.tight_layout()
plt.show()

# ============================================================
# 4. RANDOM FOREST FEATURE IMPORTANCE
# ============================================================

rf = results["Random Forest"]["model"]

preprocessor = rf.named_steps["pre"]
forest = rf.named_steps["model"]

feature_names = preprocessor.get_feature_names_out()
importance = forest.feature_importances_

order = np.argsort(importance)[::-1]

# Top 15 features
top_n = min(15, len(order))

top_features = feature_names[order[:top_n]]
top_importance = importance[order[:top_n]]

plt.figure(figsize=(10, 7))

plt.barh(
    top_features[::-1],
    top_importance[::-1]
)

plt.xlabel(
    "Feature Importance",
    fontsize=12
)

plt.ylabel(
    "Features",
    fontsize=12
)

plt.title(
    "Random Forest - Top Feature Importance",
    fontsize=16,
    fontweight="bold"
)

plt.grid(
    axis="x",
    alpha=0.25
)

plt.tight_layout()
plt.show()

# ============================================================
# 5. INDIVIDUAL METRIC COMPARISON
# ============================================================

metrics = {
    "Accuracy": accuracy,
    "Precision": precision,
    "Recall": recall,
    "F1 Score": f1
}

for metric_name, values in metrics.items():

    plt.figure(figsize=(8, 5))

    bars = plt.bar(
        names,
        values,
        width=0.5
    )

    plt.title(
        f"{metric_name} Comparison",
        fontsize=16,
        fontweight="bold"
    )

    plt.ylabel(
        f"{metric_name} (%)",
        fontsize=12
    )

    plt.ylim(0, 105)
    plt.grid(axis="y", alpha=0.25)

    for bar, value in zip(bars, values):

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 1,
            f"{value:.2f}%",
            ha="center",
            fontweight="bold"
        )

    plt.tight_layout()
    plt.show()

# ============================================================
# FINAL MESSAGE
# ============================================================

best_model = max(
    results,
    key=lambda x: results[x]["recall"]
)

print("\n========================================")
print("HEART DISEASE MODEL GRAPH ANALYSIS")
print("========================================")

print(f"Best Model : {best_model}")
print(
    f"Recall     : "
    f"{results[best_model]['recall']:.2f}%"
)
print(
    f"Accuracy   : "
    f"{results[best_model]['accuracy']:.2f}%"
)
print(
    f"Precision  : "
    f"{results[best_model]['precision']:.2f}%"
)
print(
    f"F1 Score   : "
    f"{results[best_model]['f1']:.2f}%"
)

print("\nAll graphs displayed successfully.")
print("========================================")
print("========================================")
print("========================================")