from flask import Flask, render_template, request
import pandas as pd
import joblib

from location_intelligence import (
    get_coordinates,
    find_nearby_places
)


app = Flask(__name__)


# =========================================================
# LOAD PROPERTY DATA
# =========================================================

properties = pd.read_csv(
    "data/chennai-properties.csv"
)

properties["location"] = (
    properties["location"]
    .fillna("")
    .astype(str)
)


# =========================================================
# LOAD AI MODEL
# =========================================================

model = joblib.load(
    "model/chennai_price_model.pkl"
)

print("\n========================================")
print("AI MODEL LOADED")
print("MODEL TYPE:", type(model))

if hasattr(model, "feature_names_in_"):
    print(
        "MODEL FEATURES:",
        model.feature_names_in_
    )

print("========================================\n")


locations = sorted(
    properties["location"]
    .dropna()
    .unique()
    .tolist()
)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# BUYER
# =========================================================

@app.route("/buyer")
def buyer():

    return render_template(
        "buyer.html",
        locations=locations
    )


# =========================================================
# FILTER PAGE
# =========================================================

@app.route("/filter", methods=["POST"])
def filter_page():

    location = request.form.get(
        "location",
        ""
    ).strip()

    return render_template(
        "filter.html",
        location=location,
        locations=locations
    )


# =========================================================
# SEARCH
# =========================================================

@app.route("/search", methods=["POST"])
def search():

    location = request.form.get(
        "location",
        ""
    ).strip()


    try:
        min_budget = float(
            request.form.get(
                "min_budget",
                0
            )
        )
    except:
        min_budget = 0


    try:
        max_budget = float(
            request.form.get(
                "max_budget",
                999999
            )
        )
    except:
        max_budget = 999999


    try:
        bhk = int(
            request.form.get(
                "bhk",
                1
            )
        )
    except:
        bhk = 1


    try:
        min_area = float(
            request.form.get(
                "min_area",
                0
            )
        )
    except:
        min_area = 0


    # =====================================================
    # FILTER PROPERTIES
    # =====================================================

    results = properties.copy()


    if location:

        results = results[
            results["location"]
            .str.lower()
            .str.contains(
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
        results["bhk"] >= bhk
    ]


    results = results[
        results["area_sqft"] >= min_area
    ]


    # =====================================================
    # AI PREDICTION
    # =====================================================

    if not results.empty:

        model_input = results[
            [
                "location",
                "area_sqft",
                "bhk"
            ]
        ].copy()


        print("\n========================================")
        print("SEARCH")
        print("========================================")

        print("MODEL INPUT:")
        print(model_input)

        print(
            "INPUT COLUMNS:",
            model_input.columns.tolist()
        )


        # -------------------------------------------------
        # PREDICT
        # -------------------------------------------------

        try:

            predictions = model.predict(
                model_input
            )

        except Exception as error:

            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("AI MODEL ERROR")
            print(error)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

            return (
                f"""
                <h2>AI Prediction Error</h2>
                <p>{error}</p>
                <p>Check the VS Code terminal for details.</p>
                """,
                500
            )


        print("\nAI PREDICTIONS:")
        print(predictions)


        # -------------------------------------------------
        # SAVE AI PRICE
        # -------------------------------------------------

        results["ai_price"] = [
            round(
                float(value),
                2
            )
            for value in predictions
        ]


        # -------------------------------------------------
        # PRICE DIFFERENCE
        # -------------------------------------------------

        results["price_difference"] = (
            results["price_lakhs"]
            -
            results["ai_price"]
        ).round(2)


        # -------------------------------------------------
        # ORIGINAL DATASET INDEX
        # -------------------------------------------------

        results["dataset_id"] = (
            results.index
        )


        # -------------------------------------------------
        # SORT BY AI PRICE DIFFERENCE
        # -------------------------------------------------

        results["difference_abs"] = (
            results["price_difference"]
            .abs()
        )


        results = results.sort_values(
            "difference_abs"
        )


        results = results.drop(
            columns=[
                "difference_abs"
            ]
        )


        print("\nFINAL RESULTS:")

        print(
            results[
                [
                    "name",
                    "price_lakhs",
                    "ai_price",
                    "price_difference",
                    "dataset_id"
                ]
            ]
        )

        print("========================================\n")


    # =====================================================
    # NO RESULTS
    # =====================================================

    else:

        results["ai_price"] = []
        results["price_difference"] = []
        results["dataset_id"] = []


    # =====================================================
    # RESULTS PAGE
    # =====================================================

    return render_template(
        "results.html",

        properties=results.to_dict(
            "records"
        ),

        location=location,

        min_budget=min_budget,

        max_budget=max_budget,

        bhk=bhk,

        min_area=min_area
    )


# =========================================================
# PROPERTY DETAILS
# =========================================================

@app.route("/property/<int:property_index>")
def property_details(property_index):

    # =====================================================
    # CHECK INDEX
    # =====================================================

    if (
        property_index < 0
        or property_index >= len(properties)
    ):

        return render_template(
            "property.html",

            property=None,

            nearby_places=[],

            latitude=None,

            longitude=None,

            error="Property not found."
        ), 404


    # =====================================================
    # GET PROPERTY
    # =====================================================

    property_data = (
        properties
        .iloc[property_index]
        .to_dict()
    )


    # =====================================================
    # AI MODEL INPUT
    # =====================================================

    model_input = pd.DataFrame(
        [[
            property_data["location"],
            property_data["area_sqft"],
            property_data["bhk"]
        ]],

        columns=[
            "location",
            "area_sqft",
            "bhk"
        ]
    )


    print("\n========================================")
    print("PROPERTY DETAILS")
    print("========================================")

    print(
        "PROPERTY:",
        property_data.get(
            "name",
            "Unknown"
        )
    )

    print("MODEL INPUT:")
    print(model_input)


    # =====================================================
    # AI PREDICTION
    # =====================================================

    try:

        prediction = model.predict(
            model_input
        )

    except Exception as error:

        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("PROPERTY AI MODEL ERROR")
        print(error)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

        return (
            f"""
            <h2>AI Prediction Error</h2>
            <p>{error}</p>
            <p>Check the VS Code terminal.</p>
            """,
            500
        )


    print(
        "RAW PREDICTION:",
        prediction
    )


    ai_price = float(
        prediction[0]
    )


    # =====================================================
    # SAVE AI PRICE
    # =====================================================

    property_data["ai_price"] = round(
        ai_price,
        2
    )


    # =====================================================
    # PRICE DIFFERENCE
    # =====================================================

    property_data["price_difference"] = round(
        float(
            property_data["price_lakhs"]
            -
            property_data["ai_price"]
        ),
        2
    )


    property_data["dataset_id"] = (
        property_index
    )


    print(
        "ASKING PRICE:",
        property_data["price_lakhs"],
        "L"
    )

    print(
        "AI PRICE:",
        property_data["ai_price"],
        "L"
    )

    print(
        "PRICE DIFFERENCE:",
        property_data["price_difference"],
        "L"
    )


    # =====================================================
    # LOCATION INTELLIGENCE
    # =====================================================

    location = property_data["location"]


    latitude = None
    longitude = None

    nearby_places = []


    try:

        latitude, longitude = (
            get_coordinates(
                location
            )
        )


        if (
            latitude is not None
            and longitude is not None
        ):

            print(
                "LOCATION:",
                location
            )

            print(
                "COORDINATES:",
                latitude,
                longitude
            )


            nearby_places = (
                find_nearby_places(
                    latitude,
                    longitude,
                    radius=3000
                )
            )


            print(
                "NEARBY PLACES:",
                len(nearby_places)
            )


        else:

            print(
                "COORDINATES NOT FOUND"
            )


    except Exception as error:

        print(
            "LOCATION INTELLIGENCE ERROR:",
            error
        )


    print("========================================\n")


    # =====================================================
    # PROPERTY PAGE
    # =====================================================

    return render_template(
        "property.html",

        property=property_data,

        nearby_places=nearby_places,

        latitude=latitude,

        longitude=longitude
    )


# =========================================================
# SELLER
# =========================================================

@app.route("/seller")
def seller():

    return render_template(
        "seller.html",
        locations=locations
    )


# =========================================================
# SELLER VALUATION
# =========================================================

@app.route("/valuate", methods=["POST"])
def valuate():

    property_name = request.form.get(
        "property_name",
        "My Property"
    ).strip()


    location = request.form.get(
        "location",
        ""
    ).strip()


    try:

        area = float(
            request.form.get(
                "area",
                0
            )
        )

    except:

        area = 0


    try:

        bhk = int(
            request.form.get(
                "bhk",
                1
            )
        )

    except:

        bhk = 1


    try:

        bathrooms = int(
            request.form.get(
                "bathrooms",
                0
            )
        )

    except:

        bathrooms = 0


    # =====================================================
    # VALIDATION
    # =====================================================

    if (
        not location
        or area <= 0
        or bhk <= 0
    ):

        return (
            "Please enter valid property details.",
            400
        )


    # =====================================================
    # MODEL INPUT
    # =====================================================

    model_input = pd.DataFrame(
        [[
            location,
            area,
            bhk
        ]],

        columns=[
            "location",
            "area_sqft",
            "bhk"
        ]
    )


    print("\n========================================")
    print("SELLER VALUATION")
    print("========================================")

    print("MODEL INPUT:")
    print(model_input)


    # =====================================================
    # AI PREDICTION
    # =====================================================

    try:

        prediction = model.predict(
            model_input
        )

    except Exception as error:

        print(
            "SELLER AI MODEL ERROR:",
            error
        )

        return (
            f"""
            <h2>AI Prediction Error</h2>
            <p>{error}</p>
            """,
            500
        )


    print(
        "RAW PREDICTION:",
        prediction
    )


    ai_price = round(
        float(prediction[0]),
        2
    )


    print(
        "AI PRICE:",
        ai_price,
        "L"
    )

    print("========================================\n")


    # =====================================================
    # VALUATION PAGE
    # =====================================================

    return render_template(
        "valuation.html",

        property_name=property_name,

        location=location,

        area=area,

        bhk=bhk,

        bathrooms=bathrooms,

        ai_price=ai_price
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )