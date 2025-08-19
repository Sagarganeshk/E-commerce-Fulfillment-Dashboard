import pandas as pd

def load_data(path: str) -> pd.DataFrame:
    """Load the CSV dataset with date parsing."""
    return pd.read_csv(path, parse_dates=["OrderDate", "ShipDate", "DeliveryDate"])

def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleanup: trim strings and fill nulls."""
    for col in ["CustomerID", "Region", "Courier", "Status"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().fillna("Unknown")
    if "ShippingCost" in df.columns:
        df["ShippingCost"] = df["ShippingCost"].fillna(df["ShippingCost"].median())
    if "OrderValue" in df.columns:
        df["OrderValue"] = df["OrderValue"].fillna(df["OrderValue"].median())
    return df

def add_delivery_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add delivery KPIs like delay days, flags, and month."""
    df["DeliveryDelay_Days"] = (df["DeliveryDate"] - df["ShipDate"]).dt.days
    df["IsDelayed"] = df["DeliveryDelay_Days"] > 0
    df["OrderMonth"] = df["OrderDate"].dt.to_period("M").astype(str)
    return df

def prepare_processed_csv(input_path: str, output_path: str) -> pd.DataFrame:
    """Full pipeline: load → clean → feature engineering → save."""
    df = load_data(input_path)
    df = clean_columns(df)
    df = add_delivery_features(df)
    df.to_csv(output_path, index=False)
    return df
