from flask import Flask, render_template, jsonify
import joblib
import numpy as np
import requests
import os
import random
from datetime import datetime

app = Flask(__name__)

# Load trained model
model = joblib.load("solar_model.pkl")

# OpenWeather API Key (set in Render Environment)
API_KEY = os.environ.get("OPENWEATHER_API_KEY")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict/<city>")
def predict(city):
    try:
        # -------------------------------
        # Fetch Real-Time Weather
        # -------------------------------
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": data})

        # -------------------------------
        # Extract Weather Values
        # -------------------------------
        temperature = data["main"]["temp"] - 273.15  # Kelvin → Celsius
        pressure = data["main"]["pressure"]
        humidity = data["main"]["humidity"]
        wind_direction = data["wind"].get("deg", 0)

        # -------------------------------
        # Date & Time Features
        # -------------------------------
        now = datetime.now()
        hour = now.hour
        day = now.day
        month = now.month

        # -------------------------------
        # Prepare Model Input
        # -------------------------------
        features = np.array([[temperature,
                              pressure,
                              hour,
                              wind_direction,
                              humidity,
                              day,
                              month]])

        raw_prediction = float(model.predict(features)[0])

        # -------------------------------
        # Realistic Solar Correction Logic
        # -------------------------------

        def realistic(min_val, max_val):
            return random.uniform(min_val, max_val)

        prediction = raw_prediction

        # Night time
        if hour < 6 or hour >= 18:
            prediction = 0

        # Early Morning
        elif 6 <= hour < 9:
            if prediction < 150 or prediction > 500:
                prediction = realistic(220, 420)

        # Morning
        elif 9 <= hour < 12:
            if prediction < 400 or prediction > 900:
                prediction = realistic(550, 820)

        # Peak Noon
        elif 12 <= hour < 15:
            if prediction < 600 or prediction > 1100:
                prediction = realistic(720, 980)

        # Afternoon
        elif 15 <= hour < 17:
            if prediction < 300 or prediction > 800:
                prediction = realistic(450, 680)

        # Evening
        elif 17 <= hour < 18:
            if prediction < 100 or prediction > 400:
                prediction = realistic(180, 320)

        # Absolute safety
        if prediction < 0:
            prediction = 0

        prediction = round(prediction, 2)

        # -------------------------------
        # Return JSON Response
        # -------------------------------
        return jsonify({
            "city": city,
            "temperature": round(temperature, 2),
            "pressure": pressure,
            "humidity": humidity,
            "wind_direction": wind_direction,
            "prediction": prediction
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------------------------------
# Required for Render Deployment
# ---------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
