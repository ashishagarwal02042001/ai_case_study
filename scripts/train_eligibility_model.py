import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

os.makedirs("models", exist_ok= True)

# Creation of the Synthetic Dataset
np.random.seed(42)
N = 2000
age = np.random.randint(18,70,size = N)
family_size = np.random.randint(1,8,size = N)
monthly_income = np.random.normal(1000,700,size = N).clip(100,10000)
employment_status = np.random.choice(['employed','self-employed','unemployed'],size = N, p=[0.6,0.2,0.2])
assets = np.random.exponential(2000, size = N)
liabilities = np.random.exponential(1000, size = N)
credit_score = np.random.normal(600,80,size = N).clip(300,850)

# Simple labeling
per_capita = monthly_income/np.maximum(1,family_size)
label = np.where(per_capita < 300, 'approve', np.where(per_capita < 700, 'soft-decline','reject'))

df = pd.DataFrame({
    'age':age,
    'family_size':family_size,
    'monthly_income':monthly_income,
    'employment_status':employment_status,
    'assets':assets,
    'liabilities':liabilities,
    'credit_score':credit_score,
    'label':label
})
df.to_csv("Synthetic_data.csv", index=False)

num_features = ['age','family_size','monthly_income','assets','liabilities','credit_score']
cat_features = ['employment_status']

x = df[num_features + cat_features]
y = df['label']

numeric_transformation = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformation = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformation, num_features),
        ('cat', categorical_transformation, cat_features)
    ]
)

clf = Pipeline(steps=[('preprocessor',preprocessor),
                      ('classifier',RandomForestClassifier(n_estimators=200, random_state=42))])

x_train, x_test, y_train, y_test = train_test_split(x,y,stratify=y,test_size=0.2,random_state=42)
clf.fit(x_train, y_train)

model_path = 'models/eligibility_v1.joblib'
joblib.dump(clf,model_path)
print(f"Model Saved at {model_path}")

y_pred = clf.predict(x_test)
if hasattr(clf.named_steps['classifier'],'predict_proba'):
    y_proba = clf.predict_proba(x_test)
else:
    y_proba = None

print(classification_report(y_test, y_pred))
