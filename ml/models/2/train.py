import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import shap
import pickle
import os

# ── 1. Load ────────────────────────────────────────────────────────────────
df = pd.read_csv("WA_Fn-UseC_-Telco-Customer-Churn.csv")

print("Shape:", df.shape)
print("\nColumn dtypes:\n", df.dtypes)
print("\nMissing values:\n", df.isnull().sum())

# ── 2. Drop customerID (not a feature) ────────────────────────────────────
df.drop(columns=["customerID"], inplace=True)

# ── 3. Fix TotalCharges (stored as string, has blank spaces) ───────────────
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
print("\nTotalCharges nulls after coerce:", df["TotalCharges"].isnull().sum())
df["TotalCharges"].fillna(df["TotalCharges"].median(), inplace=True)

# ── 4. Encode target ───────────────────────────────────────────────────────
df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

# ── 5. Encode binary yes/no columns ───────────────────────────────────────
binary_cols = [
    "Partner", "Dependents", "PhoneService",
    "PaperlessBilling", "gender"
]
binary_map = {"Yes": 1, "No": 0, "Male": 1, "Female": 0}
for col in binary_cols:
    df[col] = df[col].map(binary_map)

# ── 6. One-hot encode remaining categoricals ──────────────────────────────
cat_cols = [
    "MultipleLines", "InternetService", "OnlineSecurity",
    "OnlineBackup", "DeviceProtection", "TechSupport",
    "StreamingTV", "StreamingMovies", "Contract",
    "PaymentMethod"
]
df = pd.get_dummies(df, columns=cat_cols, drop_first=False)

# ── 7. Final check ─────────────────────────────────────────────────────────
print("\nFinal shape:", df.shape)
print("Churn distribution:\n", df["Churn"].value_counts())
print("\nAny nulls left:", df.isnull().sum().sum())

print("\n Preprocessing complete.")

# ── 8. Split features and target ──────────────────────────────────────────
X = df.drop(columns=["Churn"])
y = df["Churn"]

feature_names = list(X.columns)
print("Total features:", len(feature_names))

# ── 9. Train/Test split ───────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y        # keeps churn ratio balanced in both splits
)

print(f"\nTrain size: {X_train.shape[0]} | Test size: {X_test.shape[0]}")

# ── 10. Train XGBoost ──────────────────────────────────────────────────────
model = XGBClassifier(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=len(y_train[y_train==0]) / len(y_train[y_train==1]),  # handles class imbalance
    use_label_encoder=False,
    eval_metric="logloss",
    random_state=42
)

model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=50          # prints loss every 50 rounds
)

# ── 11. Evaluate ───────────────────────────────────────────────────────────
y_pred  = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print("\n── Classification Report ──────────────────────────────")
print(classification_report(y_test, y_pred, target_names=["No Churn", "Churn"]))
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_proba):.4f}")


# ── 12. Build SHAP TreeExplainer ───────────────────────────────────────────
print("\nBuilding SHAP explainer...")
explainer = shap.TreeExplainer(model)

# quick sanity check — compute shap values on a small sample
shap_values = explainer.shap_values(X_test[:5])
print("SHAP values shape:", shap_values.shape)  # should be (5, num_features)

# ── 13. Save artifacts ─────────────────────────────────────────────────────
os.makedirs(".", exist_ok=True)

with open("xgb_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("explainer.pkl", "wb") as f:
    pickle.dump(explainer, f)

with open("feature_names.pkl", "wb") as f:
    pickle.dump(feature_names, f)

# ── 14. Verify all three files exist ───────────────────────────────────────
for fname in ["xgb_model.pkl", "explainer.pkl", "feature_names.pkl"]:
    size_kb = os.path.getsize(fname) / 1024
    print(f"   {fname} → {size_kb:.1f} KB")
