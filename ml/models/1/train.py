import pandas as pd
import numpy as np
import shap
import pickle
import os
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

# ── 1. Load ────────────────────────────────────────────────────────────────
df = pd.read_csv("cs-training.csv", index_col=0)  

print("Shape:", df.shape)
print("\nColumn dtypes:\n", df.dtypes)
print("\nMissing values:\n", df.isnull().sum())

# ── 2. Rename target for clarity ──────────────────────────────────────────
df.rename(columns={"SeriousDlqin2yrs": "target"}, inplace=True)

# ── 3. Fix the two columns with missing values ────────────────────────────
# MonthlyIncome — large number of NaNs, fill with median
df["MonthlyIncome"].fillna(df["MonthlyIncome"].median(), inplace=True)

# NumberOfDependents — small number of NaNs, fill with median
df["NumberOfDependents"].fillna(df["NumberOfDependents"].median(), inplace=True)

# ── 4. Remove extreme outliers ────────────────────────────────────────────
# age has some 0 values which are invalid
print("\nAge 0 or below:", (df["age"] <= 0).sum())
df = df[df["age"] > 0]

# RevolvingUtilizationOfUnsecuredLines > 1 are extreme outliers
print("RevolvingUtilization > 1:", (df["RevolvingUtilizationOfUnsecuredLines"] > 1).sum())
df = df[df["RevolvingUtilizationOfUnsecuredLines"] <= 1]

# ── 5. Final check ─────────────────────────────────────────────────────────
print("\nFinal shape:", df.shape)
print("\nTarget distribution:\n", df["target"].value_counts())
print("\nAny nulls left:", df.isnull().sum().sum())

print("\n Preprocessing complete.")

# ── 6. Split features and target ──────────────────────────────────────────
X = df.drop(columns=["target"])
y = df["target"]

feature_names = list(X.columns)
print("Total features:", len(feature_names))
print("Features:", feature_names)

# ── 7. Train/Test split ───────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y        # keeps default ratio balanced in both splits
)

print(f"\nTrain size: {X_train.shape[0]} | Test size: {X_test.shape[0]}")
print(f"Default rate in train: {y_train.mean():.3f}")
print(f"Default rate in test:  {y_test.mean():.3f}")

# ── 8. Train XGBoost ──────────────────────────────────────────────────────
# scale_pos_weight handles the heavy class imbalance (~93% non-default)
pos_weight = len(y_train[y_train==0]) / len(y_train[y_train==1])
print(f"\nscale_pos_weight: {pos_weight:.2f}")

model = XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=pos_weight,
    eval_metric="auc",
    random_state=42
)

model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=50
)

# ── 9. Evaluate ───────────────────────────────────────────────────────────
y_pred  = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print("\n── Classification Report ──────────────────────────────")
print(classification_report(y_test, y_pred, target_names=["No Default", "Default"]))
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_proba):.4f}")

# ── 10. Build SHAP TreeExplainer ───────────────────────────────────────────
print("\nBuilding SHAP explainer...")
explainer = shap.TreeExplainer(model)

# sanity check on small sample
shap_values = explainer.shap_values(X_test[:5])
print("SHAP values shape:", shap_values.shape)  # should be (5, 10)

# ── 11. Save artifacts ─────────────────────────────────────────────────────
with open("xgb_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("explainer.pkl", "wb") as f:
    pickle.dump(explainer, f)

with open("feature_names.pkl", "wb") as f:
    pickle.dump(feature_names, f)

# ── 12. Verify all three files exist ───────────────────────────────────────
for fname in ["xgb_model.pkl", "explainer.pkl", "feature_names.pkl"]:
    size_kb = os.path.getsize(fname) / 1024
    print(f"   {fname} → {size_kb:.1f} KB")
