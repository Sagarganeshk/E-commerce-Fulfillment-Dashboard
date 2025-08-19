import pandas as pd

def kpis(df: pd.DataFrame) -> dict:
    """Return main KPIs."""
    return {
        "Total Orders": len(df),
        "On-Time Rate (%)": round((~df["IsDelayed"]).mean() * 100, 2),
        "Avg Delay (days)": round(df["DeliveryDelay_Days"].mean(), 2),
        "Avg Shipping Cost": round(df["ShippingCost"].mean(), 2),
        "Avg Order Value": round(df["OrderValue"].mean(), 2)
    }

def rate_by_group(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """On-time vs delayed rates grouped by column."""
    return df.groupby(group_col)["IsDelayed"].mean().reset_index(name="DelayRate")

def avg_delay_by_group(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Average delay days by group."""
    return df.groupby(group_col)["DeliveryDelay_Days"].mean().reset_index()

def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Orders & on-time rate by month."""
    monthly = df.groupby("OrderMonth").agg(
        Orders=("CustomerID", "count"),
        OnTimeRate=("IsDelayed", lambda x: round((~x).mean() * 100, 2))
    ).reset_index()
    return monthly
