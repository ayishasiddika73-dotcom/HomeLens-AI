import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


# =========================================================
# HOMELENS AI - CHENNAI PROPERTY EDA
# =========================================================

print("=" * 60)
print("        HOMELENS AI - CHENNAI PROPERTY EDA")
print("=" * 60)


# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(
    "data/chennai-properties.csv"
)

print("\nDataset loaded successfully!")
print(f"Total properties: {len(df)}")
print(f"Total locations: {df['location'].nunique()}")


# =========================================================
# DATA CLEANING
# =========================================================

df["name"] = df["name"].fillna("Unknown Property")

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
        "bhk"
    ]
)


# =========================================================
# FEATURE ENGINEERING
# =========================================================

df["price_per_sqft"] = (
    df["price_lakhs"] * 100000
) / df["area_sqft"]


# =========================================================
# OUTPUT DIRECTORY
# =========================================================

os.makedirs(
    "eda_outputs",
    exist_ok=True
)


# =========================================================
# BASIC STATISTICS
# =========================================================

print("\n" + "=" * 60)
print("BASIC STATISTICS")
print("=" * 60)

print(
    df[
        [
            "price_lakhs",
            "area_sqft",
            "bhk",
            "price_per_sqft"
        ]
    ].describe()
)


# =========================================================
# 1. PRICE DISTRIBUTION
# =========================================================

plt.figure(figsize=(10, 6))

plt.hist(
    df["price_lakhs"],
    bins=30,
    edgecolor="black"
)

plt.title(
    "Chennai Property Price Distribution"
)

plt.xlabel(
    "Price (Lakhs)"
)

plt.ylabel(
    "Number of Properties"
)

plt.grid(
    alpha=0.2
)

plt.tight_layout()

plt.savefig(
    "eda_outputs/01_price_distribution.png",
    dpi=300
)

plt.close()

print(
    "1/10 Price distribution saved."
)


# =========================================================
# 2. AREA DISTRIBUTION
# =========================================================

plt.figure(figsize=(10, 6))

plt.hist(
    df["area_sqft"],
    bins=30,
    edgecolor="black"
)

plt.title(
    "Property Area Distribution"
)

plt.xlabel(
    "Area (sq.ft)"
)

plt.ylabel(
    "Number of Properties"
)

plt.grid(
    alpha=0.2
)

plt.tight_layout()

plt.savefig(
    "eda_outputs/02_area_distribution.png",
    dpi=300
)

plt.close()

print(
    "2/10 Area distribution saved."
)


# =========================================================
# 3. BHK DISTRIBUTION
# =========================================================

bhk_counts = (
    df["bhk"]
    .value_counts()
    .sort_index()
)

plt.figure(figsize=(9, 6))

plt.bar(
    bhk_counts.index.astype(str),
    bhk_counts.values
)

plt.title(
    "BHK Distribution"
)

plt.xlabel(
    "BHK"
)

plt.ylabel(
    "Number of Properties"
)

plt.grid(
    axis="y",
    alpha=0.2
)

plt.tight_layout()

plt.savefig(
    "eda_outputs/03_bhk_distribution.png",
    dpi=300
)

plt.close()

print(
    "3/10 BHK distribution saved."
)


# =========================================================
# 4. PRICE VS AREA
# =========================================================

plt.figure(figsize=(10, 6))

plt.scatter(
    df["area_sqft"],
    df["price_lakhs"],
    alpha=0.6
)

plt.title(
    "Property Price vs Area"
)

plt.xlabel(
    "Area (sq.ft)"
)

plt.ylabel(
    "Price (Lakhs)"
)

plt.grid(
    alpha=0.2
)

plt.tight_layout()

plt.savefig(
    "eda_outputs/04_price_vs_area.png",
    dpi=300
)

plt.close()

print(
    "4/10 Price vs area saved."
)


# =========================================================
# 5. PRICE VS BHK
# =========================================================

plt.figure(figsize=(10, 6))

plt.scatter(
    df["bhk"],
    df["price_lakhs"],
    alpha=0.6
)

plt.title(
    "Property Price vs BHK"
)

plt.xlabel(
    "BHK"
)

plt.ylabel(
    "Price (Lakhs)"
)

plt.grid(
    alpha=0.2
)

plt.tight_layout()

plt.savefig(
    "eda_outputs/05_price_vs_bhk.png",
    dpi=300
)

plt.close()

print(
    "5/10 Price vs BHK saved."
)


# =========================================================
# 6. TOP 15 LOCATIONS BY PROPERTY COUNT
# =========================================================

location_counts = (
    df["location"]
    .value_counts()
    .head(15)
    .sort_values()
)

plt.figure(figsize=(10, 7))

plt.barh(
    location_counts.index,
    location_counts.values
)

plt.title(
    "Top 15 Chennai Locations by Number of Properties"
)

plt.xlabel(
    "Number of Properties"
)

plt.ylabel(
    "Location"
)

plt.tight_layout()

plt.savefig(
    "eda_outputs/06_top_locations.png",
    dpi=300
)

plt.close()

print(
    "6/10 Top locations saved."
)


# =========================================================
# 7. AVERAGE PRICE BY LOCATION
# =========================================================

location_price = (
    df.groupby("location")["price_lakhs"]
    .agg(
        ["mean", "count"]
    )
)

location_price = location_price[
    location_price["count"] >= 3
]

location_price = (
    location_price
    .sort_values("mean")
    .tail(15)
)


plt.figure(figsize=(10, 7))

plt.barh(
    location_price.index,
    location_price["mean"]
)

plt.title(
    "Top 15 Locations by Average Property Price"
)

plt.xlabel(
    "Average Price (Lakhs)"
)

plt.ylabel(
    "Location"
)

plt.tight_layout()

plt.savefig(
    "eda_outputs/07_location_average_price.png",
    dpi=300
)

plt.close()

print(
    "7/10 Location average price saved."
)


# =========================================================
# 8. PRICE PER SQ.FT
# =========================================================

plt.figure(figsize=(10, 6))

plt.hist(
    df["price_per_sqft"],
    bins=30,
    edgecolor="black"
)

plt.title(
    "Price per Square Foot Distribution"
)

plt.xlabel(
    "Price per sq.ft (₹)"
)

plt.ylabel(
    "Number of Properties"
)

plt.grid(
    alpha=0.2
)

plt.tight_layout()

plt.savefig(
    "eda_outputs/08_price_per_sqft.png",
    dpi=300
)

plt.close()

print(
    "8/10 Price per sq.ft saved."
)


# =========================================================
# 9. CORRELATION ANALYSIS
# =========================================================

numeric_data = df[
    [
        "price_lakhs",
        "area_sqft",
        "bhk",
        "price_per_sqft"
    ]
]

correlation = numeric_data.corr()

print("\n" + "=" * 60)
print("CORRELATION MATRIX")
print("=" * 60)

print(
    correlation.round(3)
)


plt.figure(figsize=(8, 6))

plt.imshow(
    correlation,
    interpolation="nearest"
)

plt.colorbar()

plt.xticks(
    range(len(correlation.columns)),
    correlation.columns,
    rotation=45,
    ha="right"
)

plt.yticks(
    range(len(correlation.columns)),
    correlation.columns
)

plt.title(
    "Feature Correlation Matrix"
)

plt.tight_layout()

plt.savefig(
    "eda_outputs/09_correlation_matrix.png",
    dpi=300
)

plt.close()

print(
    "9/10 Correlation matrix saved."
)


# =========================================================
# 10. OUTLIER ANALYSIS
# =========================================================

plt.figure(figsize=(10, 6))

plt.boxplot(
    [
        df["price_lakhs"],
        df["area_sqft"],
        df["bhk"]
    ],
    tick_labels=[
        "Price",
        "Area",
        "BHK"
    ]
)

plt.title(
    "Outlier Analysis"
)

plt.ylabel(
    "Value"
)

plt.grid(
    axis="y",
    alpha=0.2
)

plt.tight_layout()

plt.savefig(
    "eda_outputs/10_outlier_analysis.png",
    dpi=300
)

plt.close()

print(
    "10/10 Outlier analysis saved."
)


# =========================================================
# STARRED PROPERTY ANALYSIS
# =========================================================

starred = (
    df.groupby("is_starred")["price_lakhs"]
    .mean()
)

print("\n" + "=" * 60)
print("STARRED PROPERTY ANALYSIS")
print("=" * 60)

print(
    starred.round(2)
)


# =========================================================
# TOP 10 MOST EXPENSIVE PROPERTIES
# =========================================================

print("\n" + "=" * 60)
print("TOP 10 MOST EXPENSIVE PROPERTIES")
print("=" * 60)

top_expensive = (
    df.sort_values(
        "price_lakhs",
        ascending=False
    )
    [
        [
            "name",
            "location",
            "price_lakhs",
            "area_sqft",
            "bhk"
        ]
    ]
    .head(10)
)

print(
    top_expensive.to_string(
        index=False
    )
)


# =========================================================
# TOP 10 MOST AFFORDABLE PROPERTIES
# =========================================================

print("\n" + "=" * 60)
print("TOP 10 MOST AFFORDABLE PROPERTIES")
print("=" * 60)

top_affordable = (
    df.sort_values(
        "price_lakhs"
    )
    [
        [
            "name",
            "location",
            "price_lakhs",
            "area_sqft",
            "bhk"
        ]
    ]
    .head(10)
)

print(
    top_affordable.to_string(
        index=False
    )
)


# =========================================================
# FINAL SUMMARY
# =========================================================

print("\n" + "=" * 60)
print("EDA COMPLETED SUCCESSFULLY")
print("=" * 60)

print("\nCharts saved inside:")

print(
    "eda_outputs/"
)

print(
    "\nTotal generated visualizations: 10"
)

print("\nFiles created:")

for i in range(1, 11):

    print(
        f"  {i:02d} - ",
        end=""
    )

    files = [
        "price_distribution.png",
        "area_distribution.png",
        "bhk_distribution.png",
        "price_vs_area.png",
        "price_vs_bhk.png",
        "top_locations.png",
        "location_average_price.png",
        "price_per_sqft.png",
        "correlation_matrix.png",
        "outlier_analysis.png"
    ]

    print(
        f"eda_outputs/{i:02d}_{files[i-1]}"
    )