from flask import Flask, render_template, jsonify, request
from backend import metrics
import json

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("map.html")


@app.route("/live-station-data")
def live_station_data():

    data = metrics.get_live_data().to_dict("records")
    return jsonify(data)


@app.route("/get-station-data", methods=["POST"])
def get_station_data():
    data = request.json
    start_station = data["start"]
    end_station = data["end"]
    fetched_data = metrics.get_live_data()
    start_station = fetched_data[fetched_data["station"] == start_station]
    end_station = fetched_data[fetched_data["station"] == end_station]
    print(start_station["safety_prior"])
    response_data = [
        {"safety": start_station["safety_prior"].values[0]},
        {"safety": end_station["safety_prior"].values[0]},
    ]
    return jsonify(response_data)


if __name__ == "__main__":
    app.run(debug=True)
