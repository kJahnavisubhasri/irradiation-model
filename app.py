from flask import Flask, render_template, jsonify
import joblib
import numpy as np
import requests
import os
from datetime import datetime

app = Flask(__name__)

model = joblib.load("solar_model.pkl")

API_KEY = os.environ.get("OPENWEATHER_API_KEY")  # safer for deployment

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict/<city>")
def predict(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": data})

        # Extract real values
        temperature = data["main"]["temp"] - 273.15  # Kelvin → Celsius
        pressure = data["main"]["pressure"]
        humidity = data["main"]["humidity"]
        wind_direction = data["wind"].get("deg", 0)

        now = datetime.now()
        hour = now.hour
        day = now.day
        month = now.month

        features = np.array([[temperature,
                              pressure,
                              hour,
                              wind_direction,
                              humidity,
                              day,
                              month]])

        prediction = model.predict(features)[0]

        return jsonify({
            "city": city,
            "temperature": round(temperature, 2),
            "pressure": pressure,
            "humidity": humidity,
            "wind_direction": wind_direction,
            "prediction": round(float(prediction), 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)})
