import pandas as pd
import numpy as np
import shap
import pickle
import os
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score

# ── 1. Load both sheets and combine ───────────────────────────────────────
print("Loading Year 2009-2010...")
df1 = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2009-2010", engine="openpyxl")

print("Loading Year 2010-2011...")
df2 = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011", engine="openpyxl")

df = pd.concat([df1, df2], ignore_index=True)
print("\nCombined shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nMissing values:\n", df.isnull().sum())

# ── 2. Drop rows with missing CustomerID (can't link to a customer) ────────
df.dropna(subset=["Customer ID"], inplace=True)
print("\nShape after dropping missing CustomerID:", df.shape)

# ── 3. Remove cancellations (Invoice starts with C) ───────────────────────
df = df[~df["Invoice"].astype(str).str.startswith("C")]
print("Shape after removing cancellations:", df.shape)

# ── 4. Remove invalid rows ─────────────────────────────────────────────────
df = df[df["Quantity"] > 0]
df = df[df["Price"] > 0]
print("Shape after removing invalid quantity/price:", df.shape)

# ── 5. Clean up types ──────────────────────────────────────────────────────
df["Customer ID"] = df["Customer ID"].astype(int)
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# ── 6. Final check ─────────────────────────────────────────────────────────
print("\nFinal shape:", df.shape)
print("\nSample rows:")
print(df.head(3))
print("\nAny nulls left:", df.isnull().sum().sum())

print("\n Preprocessing complete.")

# ── 7. Feature Engineering ─────────────────────────────────────────────────
# Goal: predict whether a customer will purchase a product (StockCode)
# We build customer-level and product-level features

print("\nEngineering features...")

# Customer-level features
customer_features = df.groupby("Customer ID").agg(
    customer_total_orders   = ("Invoice", "nunique"),
    customer_total_spent    = ("Price", "sum"),
    customer_avg_order_value= ("Price", "mean"),
    customer_total_items    = ("Quantity", "sum"),
    customer_unique_products= ("StockCode", "nunique")
).reset_index()

# Product-level features
product_features = df.groupby("StockCode").agg(
    product_total_sold      = ("Quantity", "sum"),
    product_avg_price       = ("Price", "mean"),
    product_unique_customers= ("Customer ID", "nunique")
).reset_index()

# ── 8. Build customer-product pairs ───────────────────────────────────────
# Positive samples: customer DID buy this product
positives = df[["Customer ID", "StockCode"]].drop_duplicates()
positives["purchased"] = 1

# Negative samples: customer did NOT buy this product
# Sample same number as positives to keep balance
print("Building negative samples (this may take a moment)...")
all_customers = positives["Customer ID"].unique()
all_products  = positives["StockCode"].unique()

np.random.seed(42)
neg_customers = np.random.choice(all_customers, size=len(positives), replace=True)
neg_products  = np.random.choice(all_products,  size=len(positives), replace=True)

negatives = pd.DataFrame({
    "Customer ID": neg_customers,
    "StockCode"  : neg_products,
    "purchased"  : 0
})

# Remove any accidental true positives from negatives
pos_set = set(zip(positives["Customer ID"], positives["StockCode"]))
mask = [
    (c, s) not in pos_set
    for c, s in zip(negatives["Customer ID"], negatives["StockCode"])
]
negatives = negatives[mask]

# Combine
data = pd.concat([positives, negatives], ignore_index=True)
print(f"Dataset: {len(positives)} positives | {len(negatives)} negatives")

# ── 9. Merge features ──────────────────────────────────────────────────────
data = data.merge(customer_features, on="Customer ID", how="left")
data = data.merge(product_features,  on="StockCode",   how="left")
data.fillna(0, inplace=True)

# ── 10. Define X and y ─────────────────────────────────────────────────────
feature_cols = [
    "customer_total_orders",
    "customer_total_spent",
    "customer_avg_order_value",
    "customer_total_items",
    "customer_unique_products",
    "product_total_sold",
    "product_avg_price",
    "product_unique_customers"
]

X = data[feature_cols]
y = data["purchased"]
feature_names = feature_cols

print(f"\nFinal X shape: {X.shape}")
print(f"Target balance:\n{y.value_counts()}")

# ── 11. Train/Test split ───────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ── 12. Scale features (required for Logistic Regression) ──────────────────
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# ── 13. Train Logistic Regression ──────────────────────────────────────────
print("\nTraining Logistic Regression...")
model = LogisticRegression(
    max_iter=1000,
    random_state=42,
    class_weight="balanced"
)
model.fit(X_train_scaled, y_train)

# ── 14. Evaluate ───────────────────────────────────────────────────────────
y_pred  = model.predict(X_test_scaled)
y_proba = model.predict_proba(X_test_scaled)[:, 1]

print("\n── Classification Report ──────────────────────────────")
print(classification_report(y_test, y_pred, target_names=["Not Purchased", "Purchased"]))
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_proba):.4f}")

# ── 15. Build SHAP LinearExplainer ─────────────────────────────────────────
# LinearExplainer is used for Logistic Regression (not TreeExplainer)
print("\nBuilding SHAP LinearExplainer...")

# LinearExplainer needs a background dataset — use a sample of training data
background = shap.utils.sample(X_train_scaled, 100, random_state=42)
explainer = shap.LinearExplainer(model, background)

# sanity check on small sample
shap_values = explainer.shap_values(X_test_scaled[:5])
print("SHAP values shape:", shap_values.shape)  # should be (5, 8)

# ── 16. Save artifacts ─────────────────────────────────────────────────────
with open("lr_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("explainer.pkl", "wb") as f:
    pickle.dump(explainer, f)

with open("feature_names.pkl", "wb") as f:
    pickle.dump(feature_names, f)

# ── 17. Verify all three files exist ───────────────────────────────────────
for fname in ["lr_model.pkl", "explainer.pkl", "feature_names.pkl"]:
    size_kb = os.path.getsize(fname) / 1024
    print(f"   {fname} → {size_kb:.1f} KB")
