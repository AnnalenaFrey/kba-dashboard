import asyncio
from prophet import Prophet
import pandas as pd
import datetime

from ..database import PostgresAdapter
from ..models.pydantic_models import FZ11Forecast



async def prophet_forecast(db: PostgresAdapter):

    data = await db.get_time_series_all_time()

    for entry in data:
        entry["ds"] = datetime.datetime(entry["year"], entry["month"], 1)

    df = pd.DataFrame(data)
    df = df.rename(columns={"total_car_registrations": "y"})

    m = Prophet()
    m.fit(df)

    future = m.make_future_dataframe(periods=3, freq="MS")
    forecast = m.predict(future)

    future_only = forecast.tail(3)
    
    return future_only


def build_forecast_records(data: pd.DataFrame, method: str) -> list[FZ11Forecast]:

    records = [
        FZ11Forecast(
            year=row["ds"].year,
            month=row["ds"].month,
            method=method,
            yhat=row["yhat"],
            yhat_lower=row["yhat_lower"],
            yhat_upper=row["yhat_upper"],
        )
        for row in data.to_dict(orient="records")
    ]

    return records

async def save_forecast_records(records: list[FZ11Forecast], db: PostgresAdapter):
    await db.save_forecasts(forecasts=records)

