import lightgbm as lgb
import polars as pl
import numpy as np
from dateutil import parser

model = lgb.Booster(model_file='lightgbm_power_model_2.txt')

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

    return pl_df.drop('Datetime'), dt_objects

def run_prediction(features, actual, selected_date, shared):
    pl_df = pl.DataFrame([features])
    pl_df, dt_objects = transform_datetime_column(pl_df)
    time_str = dt_objects[0].strftime("%H:%M")

    X = pl_df.to_pandas()[[
        'Month_sin', 'Month_cos', 'Time_sin', 'Time_cos',
        'Temperature', 'Humidity', 'WindSpeed',
        'GeneralDiffuseFlows', 'DiffuseFlows'
    ]]

    predicted = model.predict(X)[0]

    shared["predicted_values"].append(predicted)
    shared["actual_values"].append(actual)
    shared["timestamps"].append(time_str)
    shared["selected_date"] = selected_date
