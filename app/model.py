import os
import polars as pl
import lightgbm as lgb
import numpy as np
from datetime import datetime
from dateutil import parser

# Global for Dash
predicted_values = []
actual_values = []
time_ticks = []

model = lgb.Booster(model_file='app/lightgbm_power_model_2.txt')

def transform_datetime_column(pl_df):
    dt_series = pl_df['Datetime'].to_list()
    dt_objects = [parser.parse(dt) for dt in dt_series]

    months = [dt.month for dt in dt_objects]
    minutes = [dt.hour * 60 + dt.minute for dt in dt_objects]

    month_sin = [np.sin(2 * np.pi * m / 12) for m in months]
    month_cos = [np.cos(2 * np.pi * m / 12) for m in months]
    time_sin = [np.sin(2 * np.pi * t / 1440) for t in minutes]
    time_cos = [np.cos(2 * np.pi * t / 1440) for t in minutes]

    pl_df = pl_df.with_columns([
        pl.Series('Month_sin', month_sin),
        pl.Series('Month_cos', month_cos),
        pl.Series('Time_sin', time_sin),
        pl.Series('Time_cos', time_cos)
    ])
    return pl_df.drop('Datetime'), [dt.strftime("%H:%M") for dt in dt_objects]

def load_and_predict(date):
    file_path = f"app/test/{date}.csv"
    if not os.path.exists(file_path):
        return False

    df = pl.read_csv(file_path)
    y_true = df["PowerConsumption"]
    X = df.drop("PowerConsumption")

    X_transformed, time_labels = transform_datetime_column(X)
    X_transformed = X_transformed.to_pandas()[[
        'Month_sin', 'Month_cos', 'Time_sin', 'Time_cos',
        'Temperature', 'Humidity', 'WindSpeed',
        'GeneralDiffuseFlows', 'DiffuseFlows'
    ]]

    predicted = model.predict(X_transformed)

    # Store for Dash
    predicted_values.clear()
    actual_values.clear()
    time_ticks.clear()

    predicted_values.extend(predicted)
    actual_values.extend(y_true)
    time_ticks.extend(time_labels)
    return True