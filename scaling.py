# -*- coding: utf-8 -*-
"""scaling.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ypjhKFIfAtp3XebIY31dYECkS8Qrz3E9
"""

"""

SO FEATURE SCALING TECHNIQUE IS MOSTLY NEEDED ONLY FOR LINEAR,LOGISTIC,SVM,KMEANS AND
 CLUSTERING MODELS LIKE KMEANS AND DBSCAN.

1️.Min-Max Scaling (Normalization)="Shrink everything between 0 and 1"

Best for: When features have different ranges, and you want everything to be proportional.
Not good if: Data has outliers—because they can distort the scaling!

2.Standard Scaling (Z-Score) ="Make everything centered at 0 with equal spread"

Best for: When data follows a normal distribution (bell curve) or for ML models like SVMs, K-Means, PCA.
Not good if: Data has many outliers, as it can be affected by extreme values.

3️.Robust Scaling ="Ignore outliers and use the middle values"

Best for: Datasets with outliers that you don’t want to influence your scaling.
Not good if: Your data doesn’t have many outliers (then standard scaling might be better).

4️. MaxAbs Scaling ="Keep all numbers between -1 and 1"

Best for: When data contains both positive and negative values and you need to keep signs intact.
Not good if: Data is not centered or has extreme differences in values.

FIRST ,LET ME GIVE CODE FOR DETECTING SCALING AND GIVE CODE FOR DIFFERENT SCALING
TECHNIQUES AND THEIR IMPLEMENTATION

Detecting scaling
"""
import pandas as pd
from scipy.stats import kurtosis, skew

# ── Load your dataset ─────────────────────────────────────────────
df = pd.read_csv("your_data.csv")  # Replace with your dataset
X = df.drop(columns=["target"])    # Replace with your target

# ── Select numeric features ───────────────────────────────────────
numeric_cols = X.select_dtypes(include=["number"]).columns

# ── Analyze scaling needs ─────────────────────────────────────────
scaling_suggestions = {}

for col in numeric_cols:
    col_data = X[col].dropna()
    range_ = col_data.max() - col_data.min()
    std_ = col_data.std()
    skewness = skew(col_data)
    kurt = kurtosis(col_data)

    if abs(skewness) > 2 or abs(kurt) > 5:
        scaler = "RobustScaler"  # high skew or outliers
    elif col_data.min() >= 0 and col_data.max() <= 1:
        scaler = "None"  # already scaled
    elif range_ < 1:
        scaler = "MinMaxScaler"
    elif abs(col_data).max() > 1000:
        scaler = "MaxAbsScaler"  # large absolute values
    else:
        scaler = "StandardScaler"

    scaling_suggestions[col] = scaler

# ── Print result ─────────────────────────────────────────────────
print("Recommended scalers per column:\n")
for col, suggestion in scaling_suggestions.items():
    print(f"{col:25}: {suggestion}")

"""
example results for scalers per column:

Age : StandardScaler
Income : RobustScaler
LoanAmount : MaxAbsScaler
CreditScore : MinMaxScaler


SCALING TECHNIQUES TO APPLY

Below is a drop-in template that takes the scaling_suggestions dictionary from the previous snippet
and builds a ColumnTransformer that applies the right scaler to each set of columns.
"""

# ── 1. Imports ───────────────────────────────────────────────────────────────
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler
)
from sklearn.impute import SimpleImputer   # optional, shown for completeness

# ── 2. Load data & reuse the scaling_suggestions dict ────────────────────────
df = pd.read_csv("your_data.csv")
X  = df.drop(columns=["target"])            # drop target column

# scaling_suggestions comes from the detection step you already ran
# Example:
# scaling_suggestions = {
#     "Age":          "StandardScaler",
#     "Income":       "RobustScaler",
#     "LoanAmount":   "MaxAbsScaler",
#     "CreditScore":  "MinMaxScaler",
#     "Already01Col": "None"
# }

# ── 3. Map scaler names → actual objects ─────────────────────────────────────
scaler_factory = {
    "StandardScaler": StandardScaler(),
    "MinMaxScaler":   MinMaxScaler(),
    "RobustScaler":   RobustScaler(),
    "MaxAbsScaler":   MaxAbsScaler(),
}

# ── 4. Group columns by suggested scaler ─────────────────────────────────────
grouped_cols = {}
for col, scaler_name in scaling_suggestions.items():
    grouped_cols.setdefault(scaler_name, []).append(col)

# ── 5. Build ColumnTransformer ------------------------------------------------
transformers = []

for scaler_name, cols in grouped_cols.items():
    if scaler_name == "None":
        # Pass-through (optionally with only imputation)
        transformers.append(
            (f"passthrough_{len(cols)}", "passthrough", cols)
        )
    else:
        scaler = scaler_factory[scaler_name]
        transformers.append(
            (
                scaler_name.lower(),                      # name
                Pipeline([                               # optional: impute, then scale
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler",  scaler)
                ]),
                cols
            )
        )

preprocessor = ColumnTransformer(
    transformers=transformers,
    remainder="drop"   # keep columns not listed? → "passthrough"
)

# ── 6. Fit & transform --------------------------------------------------------
X_scaled = preprocessor.fit_transform(X)

# Optional: retrieve feature names
scaled_feature_names = []
for name, trans, cols in preprocessor.transformers_:
    if name.startswith("passthrough"):
        scaled_feature_names.extend(cols)
    else:
        scaled_feature_names.extend(cols)  # scaler doesn't change names

print("Scaled data shape:", X_scaled.shape)