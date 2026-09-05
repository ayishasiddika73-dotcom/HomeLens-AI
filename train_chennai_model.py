import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# Load Chennai property data
df = pd.read_csv("data/chennai-properties.csv")

print("Chennai dataset loaded!")
print("Total properties:", len(df))


# Remove missing values
df = df.dropna(
    subset=[
        "location",
        "price_lakhs",
        "area_sqft",
        "bhk"
    ]
)


# Features and target
X = df[
    [
        "location",
        "area_sqft",
        "bhk"
    ]
]

y = df["price_lakhs"]


# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


# Preprocessing
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


# Model
model = RandomForestRegressor(
    n_estimators=300,
    random_state=42
)


# Pipeline
pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# Train
pipeline.fit(
    X_train,
    y_train
)


# Test
predictions = pipeline.predict(X_test)


mae = mean_absolute_error(
    y_test,
    predictions
)

r2 = r2_score(
    y_test,
    predictions
)


print()
print("==========================================")
print("      CHENNAI PRICE MODEL RESULTS")
print("==========================================")

print(
    f"MAE: ₹{mae:.2f} Lakhs"
)

print(
    f"R² Score: {r2:.4f}"
)


# Save model
joblib.dump(
    pipeline,
    "model/chennai_price_model.pkl"
)


print()
print(
    "Model saved successfully!"
)

print(
    "model/chennai_price_model.pkl"
)