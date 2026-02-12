from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)

MODEL_PATH = "solar_model.pkl"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("solar_model.pkl not found!")

model = joblib.load(MODEL_PATH)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        temperature = float(data["temperature"])
        pressure = float(data["pressure"])
        humidity = float(data["humidity"])
        wind_direction = float(data["wind_direction"])

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
            "prediction": round(float(prediction), 2),
            "hour": hour,
            "day": day,
            "month": month
        })

    except Exception as e:
        return jsonify({"error": str(e)})
    



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


