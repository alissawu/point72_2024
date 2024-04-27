from .utils import accessibility, ridership, crime_live_update
import pandas as pd


def get_live_data():
    manhattan_stops = pd.read_csv(
        "backend/utils/data/manhattan_stops_with_precinct.csv"
    )
    manhattan_stops.rename(
        columns={
            "Stop Name": "station",
            "GTFS Longitude": "longitude",
            "GTFS Latitude": "latitude",
        },
        inplace=True,
    )
    accessibility_df = accessibility.outages()
    ridership_df = ridership.ridership()
    ridership_df.rename(columns={"station_complex": "station"})
    crime_df = crime_live_update.calculate_safety_scores()
    merged_df = pd.merge(
        accessibility_df, ridership_df, on="station", how="outer"
    ).fillna(0)
    final_df = pd.merge(manhattan_stops, merged_df, on="station", how="outer").fillna(0)
    final_df["safety_prior"] = final_df["Precinct"].map(crime_df).abs()
    final_df["overall"] = (
        final_df["ridership_pred"].abs() / 20 + final_df["safety_prior"] / 4
    )
    return final_df


if __name__ == "__main__":
    data = get_live_data()
    print("72 St" in data["station"])
