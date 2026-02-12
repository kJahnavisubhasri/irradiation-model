from flask import Flask, render_template, request, jsonify
import requests
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# -----------------------------
# City + Area Mapping
# -----------------------------
LOCATIONS = {
    "Nellore": {
        "coords": (14.4426, 79.9865),
        "areas": ["Stonehousepet", "Vedayapalem", "Magunta Layout", "Balaji Nagar"]
    },
    "Chennai": {
        "coords": (13.0827, 80.2707),
        "areas": ["T Nagar", "Anna Nagar", "Velachery", "Tambaram"]
    },
    "Hyderabad": {
        "coords": (17.3850, 78.4867),
        "areas": ["Gachibowli", "Madhapur", "Kukatpally", "Ameerpet"]
    },
    "Bangalore": {
        "coords": (12.9716, 77.5946),
        "areas": ["Whitefield", "Indiranagar", "Electronic City", "Yelahanka"]
    },
    "Vijayawada": {
        "coords": (16.5062, 80.6480),
        "areas": ["Benz Circle", "Patamata", "Poranki", "Governorpet"]
    },
    "Visakhapatnam": {
        "coords": (17.6868, 83.2185),
        "areas": ["MVP Colony", "Gajuwaka", "Seethammadhara", "Rushikonda"]
    },
    "Tirupati": {
        "coords": (13.6288, 79.4192),
        "areas": ["Mangalam", "RC Road", "Renigunta"]
    },
    "Guntur": {
        "coords": (16.3067, 80.4365),
        "areas": ["Brodipet", "Lakshmipuram", "Pattabhipuram"]
    }
}

# -----------------------------
# Solar shaping function
# -----------------------------
def solar_profile(hour):
    curve = max(0, -((hour - 12) ** 2) + 36)
    base = curve * 25
    noise = random.uniform(-30, 30)
    return round(max(0, base + noise), 2)

# -----------------------------
@app.route("/")
def home():
    return render_template("index.html", locations=LOCATIONS)

# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    city = data["city"]
    date = data["date"]
    time = data["time"]

    lat, lon = LOCATIONS[city]["coords"]

    # Get 48-hour hourly data from Open-Meteo
    api_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m"
        f"&forecast_days=2"
        f"&timezone=Asia/Kolkata"
    )

    response = requests.get(api_url)
    weather = response.json()

    hours = weather["hourly"]["time"]
    temps = weather["hourly"]["temperature_2m"]

    selected_datetime = f"{date}T{time}"
    if selected_datetime in hours:
        index = hours.index(selected_datetime)
        temperature = temps[index]
    else:
        index = 0
        temperature = temps[0]

    hour = int(time.split(":")[0])
    prediction = solar_profile(hour)

    # last 24 hours for chart
    now = datetime.now()
    past_24_labels = []
    past_24_temps = []

    for i in range(24):
        dt = now - timedelta(hours=23 - i)
        label = dt.strftime("%H:00")
        past_24_labels.append(label)

    past_24_temps = temps[:24]

    return jsonify({
        "prediction": prediction,
        "temperature": temperature,
        "chart_labels": past_24_labels,
        "chart_data": past_24_temps
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
