import pandas as pd
import joblib


# ==========================================
# LOAD REAL CHENNAI PROPERTY DATA
# ==========================================

properties = pd.read_csv(
    "data/chennai-properties.csv"
)

print("Real Chennai property data loaded!")
print(f"Total properties: {len(properties)}")


# ==========================================
# LOAD CHENNAI AI MODEL
# ==========================================

model = joblib.load(
    "model/chennai_price_model.pkl"
)

print("Chennai AI price model loaded!")


# ==========================================
# FIND MATCHING PROPERTIES
# ==========================================

def find_matching_properties(
    location,
    min_budget,
    max_budget,
    bedrooms
):

    results = properties.copy()

    results["location"] = (
        results["location"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    results = results[
        results["location"].str.contains(
            location.lower(),
            na=False
        )
    ]

    results = results[
        (results["price_lakhs"] >= min_budget)
        &
        (results["price_lakhs"] <= max_budget)
    ]

    results = results[
        results["bhk"] >= bedrooms
    ]

    return results


# ==========================================
# AI PRICE PREDICTION
# ==========================================

def predict_price(property_data):

    input_data = pd.DataFrame([
        {
            "location": property_data["location"],
            "area_sqft": property_data["area_sqft"],
            "bhk": property_data["bhk"]
        }
    ])

    prediction = model.predict(
        input_data
    )[0]

    return prediction


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print("             HOMELENS AI")
    print("      CHENNAI PROPERTY SEARCH")
    print("==========================================")

    # Buyer requirements
    location = "porur"
    min_budget = 60
    max_budget = 100
    bedrooms = 2

    print()
    print("Buyer Requirements")
    print("------------------------------------------")
    print(f"Location: {location.title()}")
    print(
        f"Budget: ₹{min_budget} - "
        f"₹{max_budget} Lakhs"
    )
    print(f"Minimum BHK: {bedrooms}")

    # Search
    results = find_matching_properties(
        location,
        min_budget,
        max_budget,
        bedrooms
    )

    print()
    print("==========================================")
    print("       REAL CHENNAI PROPERTY MATCHES")
    print("==========================================")

    if results.empty:

        print("No matching properties found.")

    else:

        for index, (_, property_data) in enumerate(
            results.head(6).iterrows(),
            start=1
        ):

            ai_price = predict_price(
                property_data
            )

            listed_price = property_data[
                "price_lakhs"
            ]

            difference = (
                listed_price - ai_price
            )

            print()
            print(f"#{index}")

            print(
                f"Property: "
                f"{property_data['name']}"
            )

            print(
                f"Location: "
                f"{property_data['location'].title()}"
            )

            print(
                f"Area: "
                f"{int(property_data['area_sqft'])} sq.ft"
            )

            print(
                f"BHK: "
                f"{int(property_data['bhk'])}"
            )

            print(
                f"Listed Price: "
                f"₹{listed_price:.2f} Lakhs"
            )

            print(
                f"AI Estimated Price: "
                f"₹{ai_price:.2f} Lakhs"
            )

            print(
                f"Difference: "
                f"₹{abs(difference):.2f} Lakhs"
            )

            print(
                "------------------------------------------"
            )

        print()
        print(
            f"Showing top "
            f"{min(6, len(results))} "
            f"matching properties."
        )