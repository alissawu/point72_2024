from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("map.html")


@app.route("/live-station-data")
def live_station_data():
    new_str = "taig " + str(random.randint(1, 100))
    data = [
        {
            "station": new_str,
            "escalators": random.randint(0, 100),
            "elevators": random.randint(0, 100),
            "escalators_out": random.randint(0, 100),
            "elevators_out": random.randint(0, 100),
            "ridership_pred": random.randint(0, 100),
            "safety_prior": random.randint(0, 100),
            "safety_pred": "High",
            "latitude": random.uniform(40, 41),
            "longitude": random.uniform(-74, -73),
            "overall": random.randint(0, 100),
        },
    ]
    return jsonify(data)


@app.route("/get-station-data", methods=["POST"])
def get_station_data():
    data = request.json
    start_station = data["start"]
    end_station = data["end"]
    # Dummy data assuming you fetch real data based on station names
    response_data = {
        "start": {"safety": "High", "accessibility": "Wheelchair accessible"},
        "end": {"safety": "Medium", "accessibility": "Not wheelchair accessible"},
    }
    return jsonify(response_data)


if __name__ == "__main__":
    app.run(debug=True)
