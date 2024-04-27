from .utils import accessibility
import pandas as pd


def get_live_data():
    manhattan_stops = pd.read_csv("backend/utils/data/manhattan_stops.csv")
    manhattan_stops.rename(
        columns={
            "Stop Name": "station",
            "GTFS Longitude": "longitude",
            "GTFS Latitude": "latitude",
        },
        inplace=True,
    )
    accessibility_df = accessibility.outages()
    final_df = pd.merge(
        manhattan_stops, accessibility_df, on="station", how="outer"
    ).fillna(0)
    return final_df


if __name__ == "__main__":
    data = get_live_data()
    print("72 St" in data["station"])
