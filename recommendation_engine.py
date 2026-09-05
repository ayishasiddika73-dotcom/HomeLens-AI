import pandas as pd
import numpy as np


# =========================================================
# HOMELENS AI - PROPERTY RECOMMENDATION ENGINE
# =========================================================


class PropertyRecommendationEngine:

    def __init__(
        self,
        properties,
        price_model
    ):

        self.properties = properties.copy()
        self.price_model = price_model

        # Clean location values

        self.properties["location"] = (
            self.properties["location"]
            .astype(str)
            .str.strip()
            .str.lower()
        )


    # =====================================================
    # CALCULATE AI PRICE
    # =====================================================

    def predict_prices(
        self,
        properties
    ):

        model_input = properties[
            [
                "area_sqft",
                "bhk",
                "location"
            ]
        ].copy()

        predictions = (
            self.price_model
            .predict(model_input)
        )

        return np.round(
            predictions,
            2
        )


    # =====================================================
    # LOCATION MATCH
    # =====================================================

    def location_score(
        self,
        property_location,
        requested_location
    ):

        property_location = str(
            property_location
        ).lower().strip()

        requested_location = str(
            requested_location
        ).lower().strip()


        if not requested_location:

            return 50


        if property_location == requested_location:

            return 100


        if requested_location in property_location:

            return 90


        if property_location in requested_location:

            return 85


        return 0


    # =====================================================
    # BUDGET SCORE
    # =====================================================

    def budget_score(
        self,
        price,
        min_budget,
        max_budget
    ):

        if min_budget <= price <= max_budget:

            return 100


        # Slightly above budget

        if price > max_budget:

            difference = (
                price - max_budget
            )

            percentage = (
                difference /
                max_budget
            ) * 100

            if percentage <= 5:

                return 80

            elif percentage <= 10:

                return 60

            elif percentage <= 20:

                return 30

            else:

                return 0


        # Below minimum budget

        difference = (
            min_budget - price
        )

        percentage = (
            difference /
            min_budget
        ) * 100


        if percentage <= 10:

            return 85


        return 70


    # =====================================================
    # BHK SCORE
    # =====================================================

    def bhk_score(
        self,
        property_bhk,
        required_bhk
    ):

        if required_bhk is None:

            return 50


        property_bhk = float(
            property_bhk
        )

        required_bhk = float(
            required_bhk
        )


        if property_bhk == required_bhk:

            return 100


        # One extra BHK

        if property_bhk == required_bhk + 1:

            return 85


        # More than required

        if property_bhk > required_bhk:

            return 70


        # Smaller than requested

        difference = (
            required_bhk -
            property_bhk
        )


        if difference == 1:

            return 40


        return 0


    # =====================================================
    # AREA SCORE
    # =====================================================

    def area_score(
        self,
        property_area,
        minimum_area
    ):

        if not minimum_area:

            return 70


        property_area = float(
            property_area
        )

        minimum_area = float(
            minimum_area
        )


        if property_area >= minimum_area:

            return 100


        difference = (
            minimum_area -
            property_area
        )

        percentage = (
            difference /
            minimum_area
        ) * 100


        if percentage <= 5:

            return 90

        elif percentage <= 10:

            return 75

        elif percentage <= 20:

            return 50

        else:

            return 20


    # =====================================================
    # VALUE SCORE
    # =====================================================

    def value_score(
        self,
        listed_price,
        ai_price
    ):

        if ai_price <= 0:

            return 50


        difference = (
            listed_price -
            ai_price
        )

        percentage = abs(
            difference /
            ai_price
        ) * 100


        # Listed price close to AI estimate

        if percentage <= 5:

            return 100

        elif percentage <= 10:

            return 90

        elif percentage <= 15:

            return 75

        elif percentage <= 25:

            return 55

        else:

            return 30


    # =====================================================
    # VERDICT
    # =====================================================

    def verdict(
        self,
        score
    ):

        if score >= 90:

            return "Excellent Match"

        elif score >= 80:

            return "Strong Match"

        elif score >= 70:

            return "Good Match"

        elif score >= 60:

            return "Moderate Match"

        elif score >= 40:

            return "Weak Match"

        else:

            return "Poor Match"


    # =====================================================
    # MAIN RECOMMENDATION FUNCTION
    # =====================================================

    def recommend(
        self,
        location="",
        min_budget=0,
        max_budget=999999,
        bhk=None,
        minimum_area=0,
        top_n=10
    ):

        results = self.properties.copy()


        # =================================================
        # LOCATION FILTER
        # =================================================

        location = str(
            location
        ).strip().lower()


        if location:

            results = results[
                results["location"]
                .str.contains(
                    location,
                    na=False
                )
            ]


        # =================================================
        # IF NO PROPERTIES
        # =================================================

        if results.empty:

            return pd.DataFrame()


        # =================================================
        # AI PRICE PREDICTION
        # =================================================

        results["ai_price"] = (
            self.predict_prices(
                results
            )
        )


        # =================================================
        # CALCULATE PRICE DIFFERENCE
        # =================================================

        results["price_difference"] = (
            results["price_lakhs"]
            -
            results["ai_price"]
        ).round(2)


        # =================================================
        # CALCULATE INDIVIDUAL SCORES
        # =================================================

        results["location_score"] = results[
            "location"
        ].apply(
            lambda x:
            self.location_score(
                x,
                location
            )
        )


        results["budget_score"] = results[
            "price_lakhs"
        ].apply(
            lambda x:
            self.budget_score(
                x,
                min_budget,
                max_budget
            )
        )


        results["bhk_score"] = results[
            "bhk"
        ].apply(
            lambda x:
            self.bhk_score(
                x,
                bhk
            )
        )


        results["area_score"] = results[
            "area_sqft"
        ].apply(
            lambda x:
            self.area_score(
                x,
                minimum_area
            )
        )


        results["value_score"] = results.apply(
            lambda row:
            self.value_score(
                row["price_lakhs"],
                row["ai_price"]
            ),
            axis=1
        )


        # =================================================
        # FINAL WEIGHTED MATCH SCORE
        # =================================================

        results["match_score"] = (

            results["location_score"] * 0.25

            +

            results["budget_score"] * 0.25

            +

            results["bhk_score"] * 0.20

            +

            results["area_score"] * 0.15

            +

            results["value_score"] * 0.15

        )


        results["match_score"] = (
            results["match_score"]
            .round(1)
        )


        # =================================================
        # AI VERDICT
        # =================================================

        results["ai_verdict"] = (
            results["match_score"]
            .apply(
                self.verdict
            )
        )


        # =================================================
        # SORT BEST MATCH FIRST
        # =================================================

        results = results.sort_values(
            "match_score",
            ascending=False
        )


        # =================================================
        # RETURN TOP RESULTS
        # =================================================

        return results.head(
            top_n
        )


# =========================================================
# TEST FUNCTION
# =========================================================

if __name__ == "__main__":

    import joblib


    print("=" * 60)
    print("HOMELENS AI - RECOMMENDATION ENGINE TEST")
    print("=" * 60)


    # Load properties

    properties = pd.read_csv(
        "data/chennai-properties.csv"
    )


    # Load professional model

    model = joblib.load(
        "model/chennai_price_model_professional.pkl"
    )


    # Create engine

    engine = PropertyRecommendationEngine(
        properties,
        model
    )


    # Test recommendation

    recommendations = engine.recommend(

        location="porur",

        min_budget=50,

        max_budget=150,

        bhk=2,

        minimum_area=900,

        top_n=10

    )


    if recommendations.empty:

        print(
            "\nNo matching properties found."
        )

    else:

        print(
            "\nTOP RECOMMENDED PROPERTIES"
        )

        print("=" * 60)


        display_columns = [

            "name",

            "location",

            "price_lakhs",

            "area_sqft",

            "bhk",

            "ai_price",

            "price_difference",

            "match_score",

            "ai_verdict"

        ]


        print(
            recommendations[
                display_columns
            ].to_string(
                index=False
            )
        )


    print("\n")
    print("=" * 60)
    print("RECOMMENDATION ENGINE TEST COMPLETED")
    print("=" * 60)