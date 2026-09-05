import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import os

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# =========================================================
# HOMELENS AI - MODEL EVALUATION
# =========================================================

print("=" * 65)
print("        HOMELENS AI - CHENNAI PRICE MODEL EVALUATION")
print("=" * 65)


# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(
    "data/chennai-properties.csv"
)

print("\nDataset loaded.")
print(f"Total properties: {len(df)}")


# =========================================================
# CLEAN DATA
# =========================================================

df["location"] = (
    df["location"]
    .astype(str)
    .str.strip()
    .str.lower()
)

df["price_lakhs"] = pd.to_numeric(
    df["price_lakhs"],
    errors="coerce"
)

df["area_sqft"] = pd.to_numeric(
    df["area_sqft"],
    errors="coerce"
)

df["bhk"] = pd.to_numeric(
    df["bhk"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "price_lakhs",
        "area_sqft",
        "bhk",
        "location"
    ]
)


# =========================================================
# FEATURES AND TARGET
# =========================================================

X = df[
    [
        "area_sqft",
        "bhk",
        "location"
    ]
]

y = df[
    "price_lakhs"
]


# =========================================================
# TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


# =========================================================
# PREPROCESSING
# =========================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "location",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            ["location"]
        )
    ],
    remainder="passthrough"
)


# =========================================================
# MODELS
# =========================================================

models = {

    "Linear Regression":
        LinearRegression(),

    "Random Forest":
        RandomForestRegressor(
            n_estimators=300,
            random_state=42,
            max_depth=12,
            min_samples_split=4,
            min_samples_leaf=2
        )
}


# =========================================================
# OUTPUT DIRECTORY
# =========================================================

os.makedirs(
    "model_outputs",
    exist_ok=True
)


results = {}


# =========================================================
# TRAIN AND EVALUATE MODELS
# =========================================================

for model_name, model in models.items():

    print("\n" + "-" * 65)
    print(model_name)
    print("-" * 65)

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                model
            )
        ]
    )

    # Train

    pipeline.fit(
        X_train,
        y_train
    )

    # Predict

    predictions = pipeline.predict(
        X_test
    )

    # Metrics

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    mse = mean_squared_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mse
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    # Cross validation

    cv_scores = cross_val_score(
        pipeline,
        X,
        y,
        cv=5,
        scoring="r2"
    )

    cv_mean = cv_scores.mean()

    print(
        f"MAE  : ₹{mae:.2f} Lakhs"
    )

    print(
        f"MSE  : {mse:.2f}"
    )

    print(
        f"RMSE : ₹{rmse:.2f} Lakhs"
    )

    print(
        f"R²   : {r2:.4f}"
    )

    print(
        f"5-Fold CV R² : {cv_mean:.4f}"
    )

    results[
        model_name
    ] = {
        "MAE": mae,
        "MSE": mse,
        "RMSE": rmse,
        "R2": r2,
        "CV_R2": cv_mean
    }


# =========================================================
# MODEL COMPARISON
# =========================================================

comparison = pd.DataFrame(
    results
).T

print("\n" + "=" * 65)
print("MODEL COMPARISON")
print("=" * 65)

print(
    comparison.round(4)
)


comparison.to_csv(
    "model_outputs/model_comparison.csv"
)


# =========================================================
# SELECT BEST MODEL
# =========================================================

best_model_name = comparison[
    "R2"
].idxmax()

print(
    f"\nBest model based on R²: {best_model_name}"
)


# =========================================================
# TRAIN BEST MODEL AGAIN
# =========================================================

best_model = models[
    best_model_name
]

best_pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            best_model
        )
    ]
)


best_pipeline.fit(
    X_train,
    y_train
)


best_predictions = best_pipeline.predict(
    X_test
)


# =========================================================
# 1. ACTUAL VS PREDICTED
# =========================================================

plt.figure(
    figsize=(9, 7)
)

plt.scatter(
    y_test,
    best_predictions,
    alpha=0.65
)

minimum = min(
    y_test.min(),
    best_predictions.min()
)

maximum = max(
    y_test.max(),
    best_predictions.max()
)

plt.plot(
    [minimum, maximum],
    [minimum, maximum],
    linestyle="--"
)

plt.title(
    "Actual vs Predicted Property Prices"
)

plt.xlabel(
    "Actual Price (Lakhs)"
)

plt.ylabel(
    "Predicted Price (Lakhs)"
)

plt.grid(
    alpha=0.2
)

plt.tight_layout()

plt.savefig(
    "model_outputs/01_actual_vs_predicted.png",
    dpi=300
)

plt.close()


# =========================================================
# 2. RESIDUAL ANALYSIS
# =========================================================

residuals = (
    y_test.values
    - best_predictions
)


plt.figure(
    figsize=(10, 6)
)

plt.scatter(
    best_predictions,
    residuals,
    alpha=0.65
)

plt.axhline(
    y=0,
    linestyle="--"
)

plt.title(
    "Residual Error Analysis"
)

plt.xlabel(
    "Predicted Price (Lakhs)"
)

plt.ylabel(
    "Residual Error"
)

plt.grid(
    alpha=0.2
)

plt.tight_layout()

plt.savefig(
    "model_outputs/02_residual_analysis.png",
    dpi=300
)

plt.close()


# =========================================================
# 3. RESIDUAL DISTRIBUTION
# =========================================================

plt.figure(
    figsize=(10, 6)
)

plt.hist(
    residuals,
    bins=25,
    edgecolor="black"
)

plt.title(
    "Residual Error Distribution"
)

plt.xlabel(
    "Prediction Error (Lakhs)"
)

plt.ylabel(
    "Number of Properties"
)

plt.grid(
    alpha=0.2
)

plt.tight_layout()

plt.savefig(
    "model_outputs/03_residual_distribution.png",
    dpi=300
)

plt.close()


# =========================================================
# FEATURE IMPORTANCE
# =========================================================

if best_model_name == "Random Forest":

    fitted_model = (
        best_pipeline
        .named_steps["model"]
    )

    fitted_preprocessor = (
        best_pipeline
        .named_steps["preprocessor"]
    )

    location_encoder = (
        fitted_preprocessor
        .named_transformers_["location"]
    )

    location_features = (
        location_encoder
        .get_feature_names_out(
            ["location"]
        )
    )

    feature_names = list(
        location_features
    ) + [
        "area_sqft",
        "bhk"
    ]

    importances = (
        fitted_model
        .feature_importances_
    )

    importance_df = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": importances
        }
    )

    importance_df = (
        importance_df
        .sort_values(
            "importance",
            ascending=False
        )
    )

    print("\n" + "=" * 65)
    print("TOP 15 FEATURE IMPORTANCES")
    print("=" * 65)

    print(
        importance_df
        .head(15)
        .to_string(
            index=False
        )
    )

    # Top 15 only for visualization

    top_features = (
        importance_df
        .head(15)
        .sort_values(
            "importance"
        )
    )

    plt.figure(
        figsize=(10, 8)
    )

    plt.barh(
        top_features["feature"],
        top_features["importance"]
    )

    plt.title(
        "Top 15 Feature Importances"
    )

    plt.xlabel(
        "Importance"
    )

    plt.ylabel(
        "Feature"
    )

    plt.tight_layout()

    plt.savefig(
        "model_outputs/04_feature_importance.png",
        dpi=300
    )

    plt.close()

    importance_df.to_csv(
        "model_outputs/feature_importance.csv",
        index=False
    )


# =========================================================
# SAVE BEST MODEL
# =========================================================

joblib.dump(
    best_pipeline,
    "model/chennai_price_model_professional.pkl"
)


# =========================================================
# FINAL REPORT
# =========================================================

print("\n" + "=" * 65)
print("MODEL EVALUATION COMPLETED")
print("=" * 65)

print(
    f"\nBest Model: {best_model_name}"
)

print(
    f"MAE : ₹{comparison.loc[best_model_name, 'MAE']:.2f} Lakhs"
)

print(
    f"RMSE: ₹{comparison.loc[best_model_name, 'RMSE']:.2f} Lakhs"
)

print(
    f"R²  : {comparison.loc[best_model_name, 'R2']:.4f}"
)

print(
    f"CV R²: {comparison.loc[best_model_name, 'CV_R2']:.4f}"
)

print(
    "\nModel saved:"
)

print(
    "model/chennai_price_model_professional.pkl"
)

print(
    "\nEvaluation files saved inside:"
)

print(
    "model_outputs/"
)

print(
    "\nDone!"
)