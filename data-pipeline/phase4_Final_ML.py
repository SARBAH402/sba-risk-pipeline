import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib

print("--- PHASE 5: THE PRODUCTION ML SHOWDOWN ---")

# 1. Secure Authentication & Extraction
load_dotenv()
db_uri = os.getenv("SUPABASE_DB_URI")
engine = create_engine(db_uri)

print("Pulling ML-ready matrix from Supabase into memory...")
df = pd.read_sql("SELECT * FROM ml_ready_sandbox", engine)

# 2. Prepare the Features and Target
X = df.drop(columns=['is_default'])
print(X.columns.tolist())
y = df['is_default']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. The Secret Sauce: Dynamic Imbalance Ratio
print("\nCalculating dynamic class imbalance weights...")
# Using your exact mathematical formulation
ratio = (len(y_train) - sum(y_train)) / sum(y_train)
print(f"Class Imbalance Ratio Calculated: {ratio:.4f}")

# 4. Engine 1: Random Forest Baseline
print("\nIgniting Random Forest Engine...")
rf_model = RandomForestClassifier(
    n_estimators=100, 
    max_depth=10, 
    class_weight='balanced', # RF's native way of handling your ratio
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)

# 5. Engine 2: XGBoost with Custom Ratio
print("Igniting XGBoost Engine with Custom Weighting...")
xgb_model = xgb.XGBClassifier(
    n_estimators=100, 
    max_depth=6, 
    learning_rate=0.1, 
    scale_pos_weight=ratio, # Injecting your exact mathematical formula here
    random_state=42, 
    eval_metric='logloss'
)
xgb_model.fit(X_train, y_train)

# 6. The Showdown Evaluation
print("\n=========================================")
print("          🏆 ALGORITHM SHOWDOWN 🏆       ")
print("=========================================\n")

# Evaluate Random Forest
rf_preds = rf_model.predict(X_test)
print("--- RANDOM FOREST RESULTS ---")
print(f"Accuracy: {accuracy_score(y_test, rf_preds) * 100:.2f}%")
print("Confusion Matrix:\n", confusion_matrix(y_test, rf_preds))
print(classification_report(y_test, rf_preds))

# Evaluate XGBoost
xgb_preds = xgb_model.predict(X_test)
print("\n--- XGBOOST RESULTS (Custom Ratio) ---")
print(f"Accuracy: {accuracy_score(y_test, xgb_preds) * 100:.2f}%")
print("Confusion Matrix:\n", confusion_matrix(y_test, xgb_preds))
print(classification_report(y_test, xgb_preds))

# 7. Save the Winning Artifact
print("\nSaving XGBoost as the primary deployment artifact...")
joblib.dump(xgb_model, "production_xgboost_engine.pkl")
print("SUCCESS: Engine ready for Excel What-If deployment.")