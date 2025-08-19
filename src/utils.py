import pandas as pd

def ensure_required_columns(df: pd.DataFrame) -> None:
    """Raise error if required columns missing."""
    required = ["OrderID","CustomerID","OrderDate","ShipDate","DeliveryDate",
                "Region","Courier","ShippingCost","OrderValue"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
