import pandas as pd
import requests
import numpy as np
from datetime import datetime, timedelta
from statsmodels.tsa.ar_model import AutoReg
import pickle

# Reads in stations in Manhattan
manhattan_stops = pd.read_csv("/data/manhattan_stops.csv")
manhattan_unique = manhattan_stops['Stop Name'].unique()

# Function takes in timeframe as input and outputs the most recently available data of the length of the provided timeframe
def generate_data(timeframe):
  current_time = datetime.now()

  # Iterates backwards from current time and finds the first available dataset (first nonempty dataset)
  while True:
    current_time = current_time - timedelta(hours=1)
    formatted_time = current_time.strftime('%Y-%m-%dT%H:00:00')
    url = "https://data.ny.gov/resource/wujg-7c2s.json?$where=transit_timestamp >= '" + formatted_time + "'"
    response = requests.get(url)
    data = response.json()
    df_sub = pd.DataFrame.from_dict(data)
    if len(df_sub) > 0:
      break

  # Stacks the dataframes for the most recently available data for the timeframe given
  for j in range(timeframe):
    current_time = current_time - timedelta(hours=1)
    formatted_time = current_time.strftime('%Y-%m-%dT%H:00:00')
    url = "https://data.ny.gov/resource/wujg-7c2s.json?$where=transit_timestamp >= '" + formatted_time + "'"
    response = requests.get(url)
    data = response.json()
    df_temp = pd.DataFrame.from_dict(data)
    df_sub = pd.concat([df_sub, df_temp], axis=0)

  # Filters dataframe
  filtered_df = df_sub[['station_complex', 'ridership', 'transfers', 'transit_timestamp']]

  # Splits stations accordingly 
  expanded_data = filtered_df.drop('station_complex', axis=1).join(
          filtered_df['station_complex'].str.split('/').explode('station_complex').reset_index(drop=True)
      )
  expanded_data['station_complex'] = expanded_data['station_complex'].str.replace(r'\s*\([^)]+\)', '', regex=True)
  expanded_data['ridership'] = pd.to_numeric(expanded_data['ridership'], errors='coerce')
  expanded_data['transfers'] = pd.to_numeric(expanded_data['transfers'], errors='coerce')
  expanded_data = expanded_data.dropna(subset=['ridership', 'transfers'])

  # Finds sum of ridership for stations with multiple entries
  consolidated_data = expanded_data.groupby(['transit_timestamp', 'station_complex']).agg({
      'ridership': 'sum',
      'transfers': 'sum'
  }).reset_index()

  consolidated_data = consolidated_data.loc[pivot_df['station_complex'].isin(manhattan_unique)]

  return consolidated_data

with open("models.pickle", "rb") as handle:
    models = pickle.load(handle)

# Function defines method to use autoregression model to predict ridership value
def predict(coef, history):
    yhat = coef[0]
    for i in range(1, len(coef)):
        yhat += coef[i] * history[-i]
    return yhat

# Function uses autoregression model on most recent data to predict ridership at each station based on most recently available 12 hours of data
def ridership():
  ridership_pred = {}
  consolidated_data = generate_data(12)

  for station in consolidated_data['station'].unique():
      station_df = consolidated_data[consolidated_data['station_complex'] == station]
      station_df = station_df.sort_values('transit_timestamp')
      station_df['transit_timestamp'] = pd.to_datetime(station_df['transit_timestamp'])
      station_df = station_df.dropna(subset=['ridership'])
      station_df.reset_index(inplace=True, drop=True)
      # Completes calculation for station based on model coefficients and stores prediction
      coef = models[station]
      prediction = predict(coef, station_df['ridership'].values)
      ridership_pred[station] = prediction

      return pd.DataFrame(list(ridership_pred.items()), columns=['station', 'ridership_pred'])
