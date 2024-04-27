import pandas as pd
import pickle
from .ridership_model import generate_data

manhattan_stops = pd.read_csv("utils/data/manhattan_stops.csv")
manhattan_unique = manhattan_stops["Stop Name"].unique()

with open("models.pickle", "rb") as handle:
    models = pickle.load(handle)


def predict(coef, history):
    yhat = coef[0]
    for i in range(1, len(coef)):
        yhat += coef[i] * history[-i]
    return yhat


def ridership():
    ridership_pred = {}
    consolidated_data = generate_data(3)
    print("balls")
    for station in consolidated_data["station_complex"].unique():
        station_df = consolidated_data[consolidated_data["station_complex"] == station]
        station_df = station_df.sort_values("transit_timestamp")
        station_df["transit_timestamp"] = pd.to_datetime(
            station_df["transit_timestamp"]
        )
        station_df = station_df.dropna(subset=["ridership"])
        station_df.reset_index(inplace=True, drop=True)

        coef = models[station]
        prediction = predict(coef, station_df["ridership"].values)
        ridership_pred[station] = prediction

        return pd.DataFrame(
            list(ridership_pred.items()), columns=["station", "ridership_pred"]
        )
