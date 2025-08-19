import plotly.express as px
import pandas as pd

def status_pie(df: pd.DataFrame):
    return px.pie(df, names="IsDelayed", title="On-Time vs Delayed Orders")

def courier_stack(df: pd.DataFrame):
    return px.histogram(df, x="Courier", color="IsDelayed", barmode="stack", title="Courier Performance")

def delay_box_by_courier(df: pd.DataFrame):
    return px.box(df, x="Courier", y="DeliveryDelay_Days", title="Delay Distribution by Courier")

def regional_stack(df: pd.DataFrame):
    return px.histogram(df, x="Region", color="IsDelayed", barmode="stack", title="Regional Performance")

def monthly_orders_trend(df: pd.DataFrame):
    monthly = df.groupby("OrderMonth").agg(Orders=("CustomerID","count")).reset_index()
    return px.line(monthly, x="OrderMonth", y="Orders", markers=True, title="Monthly Orders Trend")

def cost_vs_delay(df: pd.DataFrame):
    return px.scatter(df, x="ShippingCost", y="DeliveryDelay_Days", trendline="ols", 
                      title="Shipping Cost vs Delivery Delay")
