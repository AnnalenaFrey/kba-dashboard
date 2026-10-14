import pandas as pd



def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("ds").reset_index(drop=True)

    for lag in [1, 2, 3, 6, 12]:
        df[f"lag_{lag}"] = df["total_car_registrations"].shift(lag)

    df["rolling_3"] = df["total_car_registrations"].shift(1).rolling(3).mean()
    df["rolling_6"] = df["total_car_registrations"].shift(1).rolling(6).mean()
    df["rolling_12"] = df["total_car_registrations"].shift(1).rolling(12).mean()

    df["volatility_6"] = df["total_car_registrations"].shift(1).rolling(6).std()

    df["mom_growth"] = df["lag_1"] / df["lag_2"] - 1
    df["yoy_growth"] = df["lag_1"] / df["lag_12"] - 1    

    df = df.dropna().reset_index(drop=True)

    return df


def train_test_split(df: pd.DataFrame, test_size: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = df.iloc[:-test_size]
    test = df.iloc[test_size:]
    return train, test


