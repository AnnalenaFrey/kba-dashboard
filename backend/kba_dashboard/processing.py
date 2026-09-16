import pandas as pd
from pathlib import Path
import numpy as np

from .models.pydantic_models import KBAFile, FZ11Record


MULTI_WORD_BRANDS = [
        "ALFA ROMEO", "ASTON MARTIN", "ROLLS ROYCE", "LAND ROVER",
        "DAF TRUCKS", "MERCEDES BENZ", "BMW I", "MG MOTOR",
        "CUPRA", "OPEL/VAUXHALL"
    ]

def extract_brand_and_model(model_series: str) -> tuple[str | None, str | None]:

    if pd.isna(model_series):
        return None, None
    
    text = str(model_series).strip().upper()
    
    # Check for multi word brands first
    for brand in MULTI_WORD_BRANDS:
        if text == brand or text.startswith((brand + " ")):
            # From the end of the brand name to the end of the string is the model name
            model = text[len(brand):].strip()
            return brand, model or None
    
    # If no multi word brand is found, split the string once at the first whitespace
    # e.g. "DACIA SPRING" becomes ("DACIA", "SPRING")
    parts = text.split(maxsplit=1)

    # Check that parts is not empty
    if not parts:
        return None, None

    # Standard case: First word of the string is considered to be the brand name
    brand = parts[0]

    # Small fix for a common typo in the excel files
    if brand == "MECEDES":
        brand = "MERCEDES"

    # Second part of the string is considered to be the model name
    # Only if the string is longer than 1 word, otherwise the model name is None
    model = parts[1].strip() if len(parts) > 1 else None
    
    return brand, model

def read_excel(file: KBAFile) -> list[FZ11Record]:

    xls = pd.ExcelFile(Path(file.storage_location), engine="openpyxl")
    sheet_name = next(
        (s for s in xls.sheet_names if "fz11.1" in s.replace(" ", "").lower()),
        None
    )
    if sheet_name is None:
        raise ValueError(f"Could not find FZ11.1-Sheet in {file.filename}")


    df_raw = pd.read_excel(xls, sheet_name=sheet_name, skiprows=9, header=None, engine="openpyxl")
    df = df_raw.iloc[:, [1, 2, 4, 7]]
    df = df.rename(columns={1: "segment", 2: "model_series", 4: "car_registrations", 7: "commercial_share"})

    # Fill all segment rows with the segment name since
    # only the first row has the segment, and the others are empty
    df["segment"] = df["segment"].ffill()
    df["car_registrations"] = pd.to_numeric(df["car_registrations"], errors="coerce")
    df["commercial_share"] = pd.to_numeric(df["commercial_share"], errors="coerce")

    # Drop rows where either car_registrations or _model_series is None
    # Corresponds to footer rows / empty rows
    df = df.dropna(subset=["car_registrations", "model_series"])

    # Remove rows containing aggregates over a segment / model_series
    df = df[
        ~df["segment"].str.contains("zusammen|insgesamt", case=False, na=False)
        & ~df["model_series"].str.contains("zusammen|insgesamt", case=False, na=False)
    ]

    df["brand"], df["model"] = zip(*df["model_series"].apply(extract_brand_and_model))

    df["year"] = file.year
    df["month"] = file.month
    df["raw_file_id"] = file.id

    # Ensure that any Nan set during the zip process is replaced with None
    df = df.replace({np.nan: None})

    return [FZ11Record(**row) for row in df.to_dict(orient="records")]

