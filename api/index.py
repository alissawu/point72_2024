from flask import Flask, render_template, jsonify, request
import sys
import os

# Add parent directory to path so we can import backend
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend import metrics

app = Flask(__name__, template_folder='../templates', static_folder='../static')

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
    response_data = [
        {"safety": start_station["safety_prior"].values[0]},
        {"safety": end_station["safety_prior"].values[0]},
    ]
    return jsonify(response_data)

@app.route("/test")
def test():
    return "Hello, world!"

# This is the entry point for Vercel
def handler(request):
    return app(request.environ, request.start_response)
