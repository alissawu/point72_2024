import requests
import pandas as pd
import statistics
from datetime import datetime, timedelta

manhattan_stops = pd.read_csv("/data/manhattan_stops.csv")
manhattan_unique = manhattan_stops['Stop Name'].unique()

def outages():
    url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fnyct_ene_equipments.json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print("Error fetching data:", e)
        return

    df = pd.json_normalize(data)

    grouped_df = df.groupby(['station', 'equipmenttype', 'isactive']).size().reset_index(name='count')

    pivot_df = grouped_df.pivot_table(index='station',
                                      columns=['equipmenttype', 'isactive'],
                                      values='count',
                                      aggfunc='sum',
                                      fill_value=0)

    pivot_df.columns = ['_'.join(col).strip() for col in pivot_df.columns.values]
    pivot_df.reset_index(inplace=True)

    pivot_df['escalators'] = pivot_df.get('ES_Y', 0) + pivot_df.get('ES_N', 0)
    pivot_df['elevators'] = pivot_df.get('EL_Y', 0) + pivot_df.get('EL_N', 0)

    pivot_df['elevators_out'] = pivot_df.get('ES_N', 0)
    pivot_df['escalators_out'] = pivot_df.get('EL_N', 0)

    columns_to_drop = [col for col in pivot_df.columns if "EL" in col or "ES" in col]
    pivot_df.drop(columns=columns_to_drop, inplace=True)

    pivot_df = pivot_df.loc[pivot_df['station'].isin(manhattan_unique)]

    return pivot_df