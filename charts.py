import plotly.graph_objects as go
import plotly.express as px


def make_radar_chart(scores):
    categories = list(scores.keys())
    values = list(scores.values())

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name="Store Health"
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        margin=dict(l=30, r=30, t=30, b=30),
        height=420
    )
    return fig


def make_issue_severity_chart(scores):
    severity = {
        "Sales Pressure": 100 - scores["Sales"],
        "Staffing Pressure": 100 - scores["Staffing"],
        "Inventory Pressure": 100 - scores["Inventory"],
        "Customer Pressure": 100 - scores["Customers"],
        "Promotion Pressure": 100 - scores["Promotions"],
        "Operational Pressure": 100 - scores["Operations"],
    }
    fig = px.bar(
        x=list(severity.keys()),
        y=list(severity.values()),
        labels={"x": "Area", "y": "Pressure"},
    )
    fig.update_layout(height=420, margin=dict(l=20, r=20, t=30, b=20))
    return fig


def make_priority_map(priority_data):
    fig = px.scatter(
        priority_data,
        x="Effort",
        y="Impact",
        text="Opportunity",
        size="Impact"
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(height=420, margin=dict(l=20, r=20, t=30, b=20))
    return fig


def make_sales_trend_chart(df):
    if df is None or df.empty or "Date" not in df.columns or "Revenue" not in df.columns:
        return None

    grouped = df.groupby("Date", as_index=False)["Revenue"].sum()
    fig = px.line(grouped, x="Date", y="Revenue", markers=True)
    fig.update_layout(height=360, margin=dict(l=20, r=20, t=30, b=20))
    return fig


def make_top_products_chart(df):
    if df is None or df.empty or "Product" not in df.columns or "Revenue" not in df.columns:
        return None

    grouped = df.groupby("Product", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False).head(10)
    fig = px.bar(grouped, x="Product", y="Revenue")
    fig.update_layout(height=360, margin=dict(l=20, r=20, t=30, b=20))
    return fig