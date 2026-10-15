import pandas as pd
from sklearn.preprocessing import StandardScaler
import torch.nn as nn
import torch

FEATURE_COLUMNS = [
    "lag_1", "lag_2", "lag_3", "lag_6", "lag_12",
    "rolling_3", "rolling_6", "rolling_12",
    "volatility_6", "mom_growth", "yoy_growth", "month"
]

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

    df["month"] = df["ds"].dt.month   

    df = df.dropna().reset_index(drop=True)

    return df


def train_test_split(df: pd.DataFrame, test_size: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = df.iloc[:-test_size]
    test = df.iloc[-test_size:]
    return train, test


def scale_features(train: pd.DataFrame, test: pd.DataFrame):
    scaler = StandardScaler()

    X_train = scaler.fit_transform(train[FEATURE_COLUMNS])
    X_test = scaler.transform(test[FEATURE_COLUMNS])

    y_train = train["total_car_registrations"].values
    y_test = test["total_car_registrations"].values

    return X_train, X_test, y_train, y_test, scaler


def to_tensors(X_train, X_test, y_train, y_test):
    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    X_test_t = torch.tensor(X_test, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.float32).view(-1,1)
    y_test_t = torch.tensor(y_test, dtype=torch.float32).view(-1,1)

    return X_train_t, X_test_t, y_train_t, y_test_t


class ForecastNet(nn.Module):
    def __init__(self, input_size: int):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(16,1) 
        )
