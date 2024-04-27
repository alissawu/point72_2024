from utils import accessibility, ridership, safety_hist, safety_real
import pandas as pd


def get_live_data():
    manhattan_stops = pd.read_csv("utils/data/manhattan_stops.csv")
    accessibility_df = accessibility.outages()
    print("FUCK")
    ridership_df = ridership.ridership()
    print("SHIT")
    merged_df = pd.merge(
        accessibility_df, ridership_df, on="station", how="outer"
    ).fillna(0)

    manhattan_stops = pd.read_csv("/utils/data/manhattan_stops.csv")
    final_df = pd.merge(merged_df, manhattan_stops, on="station", how="inner")

    return final_df


if __name__ == "__main__":
    print(get_live_data())
