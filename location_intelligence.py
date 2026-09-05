import requests
import math


OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def calculate_distance(lat1, lon1, lat2, lon2):

    earth_radius = 6371

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    difference_lat = math.radians(lat2 - lat1)
    difference_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(difference_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(difference_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius * c


def get_coordinates(location):

    try:

        response = requests.get(
            NOMINATIM_URL,
            params={
                "q": f"{location}, Chennai, Tamil Nadu, India",
                "format": "json",
                "limit": 1
            },
            headers={
                "User-Agent": "HomeLens-AI-Project"
            },
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if not data:
            return None, None

        return (
            float(data[0]["lat"]),
            float(data[0]["lon"])
        )

    except Exception as error:

        print("Geocoding error:", error)

        return None, None


def find_nearby_places(
    latitude,
    longitude,
    radius=3000
):

    query = f"""
    [out:json][timeout:30];

    (
        node["amenity"="school"]
        (around:{radius},{latitude},{longitude});

        way["amenity"="school"]
        (around:{radius},{latitude},{longitude});

        node["amenity"="hospital"]
        (around:{radius},{latitude},{longitude});

        way["amenity"="hospital"]
        (around:{radius},{latitude},{longitude});

        node["amenity"="cinema"]
        (around:{radius},{latitude},{longitude});

        way["amenity"="cinema"]
        (around:{radius},{latitude},{longitude});

        node["shop"="supermarket"]
        (around:{radius},{latitude},{longitude});

        way["shop"="supermarket"]
        (around:{radius},{latitude},{longitude});

        node["railway"="station"]
        (around:{radius},{latitude},{longitude});

        node["amenity"="bus_station"]
        (around:{radius},{latitude},{longitude});
    );

    out center tags;
    """

    try:

        response = requests.post(
            OVERPASS_URL,
            data=query,
            timeout=40,
            headers={
                "User-Agent": "HomeLens-AI-Project"
            }
        )

        response.raise_for_status()

        data = response.json()

    except Exception as error:

        print("Overpass error:", error)

        return []

    places = []

    for element in data.get("elements", []):

        tags = element.get("tags", {})

        name = tags.get(
            "name",
            "Unnamed place"
        )

        if "lat" in element:

            place_latitude = element["lat"]
            place_longitude = element["lon"]

        elif "center" in element:

            place_latitude = element["center"]["lat"]
            place_longitude = element["center"]["lon"]

        else:
            continue

        distance = calculate_distance(
            latitude,
            longitude,
            place_latitude,
            place_longitude
        )

        amenity = tags.get("amenity", "")
        shop = tags.get("shop", "")
        railway = tags.get("railway", "")

        if amenity == "school":
            place_type = "School"

        elif amenity == "hospital":
            place_type = "Hospital"

        elif amenity == "cinema":
            place_type = "Theatre"

        elif shop == "supermarket":
            place_type = "Supermarket"

        elif railway == "station":
            place_type = "Transport"

        elif amenity == "bus_station":
            place_type = "Transport"

        else:
            continue

        places.append({
            "name": name,
            "type": place_type,
            "distance_km": round(distance, 2),
            "latitude": place_latitude,
            "longitude": place_longitude
        })

    places.sort(
        key=lambda item: item["distance_km"]
    )

    return places