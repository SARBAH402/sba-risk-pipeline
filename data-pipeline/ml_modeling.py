# %%
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

print("--- PHASE 4: CLOUD-NATIVE XGBOOST TRAINING (SANDBOX) ---")

# 1. Secure Authentication
load_dotenv()
db_uri = os.getenv("SUPABASE_DB_URI")
engine = create_engine(db_uri)

# 2. Extract (Querying the Cloud Sandbox)
print("Pulling ML-ready matrix from Supabase into memory...")
df = pd.read_sql("SELECT * FROM ml_ready_sandbox", engine)
print(f"Data Loaded: {df.shape[0]:,} rows.")
# %%
X = df.drop(columns = ['is_default'])
y = df['is_default']
# %%
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size = 0.8, stratify = y, random_state = 42
)
# %%
from sklearn.linear_model import LogisticRegression

log_pipeline = Pipeline([
    ('scaler', StandardScaler()),
   ('classifier', LogisticRegression(class_weight = 'balanced', random_state = 42))
])
# %%
log_pipeline.fit(X_train, y_train)
print('Pipeline successully trained.')

y_pred = log_pipeline.predict(X_test)

cm =confusion_matrix(y_test, y_pred)

print('\n Confusion Matrix (Raw Matrix):')
print(cm)

print('\n Classification Report:')
print(classification_report(y_test, y_pred))
# %%
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Predicted Paid', 'Predicted Default'],
            yticklabels=['Actual Paid', 'Actual Default'])
plt.title('Baseline Logistic Regression - Confusion Matrix')
plt.ylabel('True Reality')
plt.xlabel('Model Prediction')
plt.show()
# %%
trained_model = log_pipeline.named_steps['classifier']

weights = trained_model.coef_[0]

feature_names = X_train.columns

feature_importance = pd.DataFrame({
    'Variable': feature_names,
    'Risk_Weight': weights
}).sort_values(by= 'Risk_Weight', ascending= False)

print(feature_importance)

# %%
from sklearn.ensemble import RandomForestClassifier
print("--- RANDOM FOREST PIPELINE ---")

rf_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(
        n_estimators=100, class_weight='balanced', 
        n_jobs=-1, random_state=42
    ))
])

rf_pipeline.fit(X_train, y_train)

y_pred_rf = rf_pipeline.predict(X_test)

rf_cm = confusion_matrix(y_test, y_pred_rf)
print('\nConfusion Matrix (RF):')
print(rf_cm)

print('\nClassification Report (RF):')
print(classification_report(y_test, y_pred_rf))
# %%
from xgboost import XGBClassifier

print("--- XGBOOST PIPELINE ---")

ratio = (len(y) - sum(y)) / sum(y)

xgb_pipeline = Pipeline([
    ('scaler',StandardScaler()),
    ('classifier', XGBClassifier(
        n_estimators=100, learning_rate = 0.1,
        scale_pos_weight = ratio, random_state = 42,
        use_label_encoder = False,
        eval_metric = 'logloss'
    ))
])

xgb_pipeline.fit(X_train, y_train)

y_pred_xgb = xgb_pipeline.predict(X_test)

cm_xgb = confusion_matrix(y_test, y_pred_xgb)

print('\nConfusion Matrix (XGB):')
print(cm_xgb)

print('\nClassification Report (XGB):')
print(classification_report(y_test, y_pred_xgb))
# %%
importances = xgb_pipeline.named_steps['classifier'].feature_importances_
feature_importance = X.columns
importances_df = pd.DataFrame({
    'Variable': X.columns,
    'Weight': importances
}).sort_values(by='Weight', ascending=False)

print("\nTop Economic Drivers of Default")
print(importances_df.head(5))
# %%
