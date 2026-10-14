import pandas as pd

from ..database import PostgresAdapter


async def get_historical_data(db: PostgresAdapter) -> pd.DataFrame:
    data = await db.get_time_series_all_time()
    df = pd.DataFrame(data)
    df["ds"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))

    return df