# Library Setup
from dash import Dash, html, dcc
import plotly.graph_objects as go
import pandas as pd

# Import function from db_service.py
from services.db_service import get_rush_hours_data


# Initialize Dash Application
app = Dash(__name__)
server = app.server  # Required for deployment


# Fetching a data via db_service
df = get_rush_hours_data()


# Reshape data: rows = channel, columns = hour, values = total orders
pivot = df.pivot_table(
    index="channel",          # Y-axis: sales channel
    columns="hour_of_day",    # X-axis: hour of the day
    values="total_order",     # Cell value: number of orders
    aggfunc="sum",
    fill_value=0,             # Hours with no orders show 0
)


# Color scale for each channel (light -> dark = fewer -> more orders)
CHANNEL_COLORS = {
    "Foodpanda": "RdPu",    # Pink
    "Walk-in": "Teal",      # Teal / green-blue
}
channels = ["Foodpanda", "Walk-in"]  # Row order, top to bottom


# Create Plotly Visualization
# One heatmap trace per channel so each channel gets its own color scale
fig = go.Figure()
for i, channel in enumerate(channels):
    fig.add_trace(
        go.Heatmap(
            x=pivot.columns,                     # Hours
            y=channels,                          # Both rows, so the axis shows channel names
            z=[                                  # Fill only this channel's row, leave the other empty
                pivot.loc[c].tolist() if c == channel else [None] * len(pivot.columns)
                for c in channels
            ],
            hoverongaps=False,                   # No hover on the empty row
            colorscale=CHANNEL_COLORS[channel],  # Channel-specific colors
            xgap=3,                              # Gap between columns
            ygap=3,                              # Gap between rows
            texttemplate="%{z}",                 # Show the order count inside each cell
            textfont={"size": 14},               # Size of numbers inside cells
            hovertemplate="%{y} at %{x}<br>Orders: %{z}<extra></extra>",
            colorbar={
                "title": {"text": f"<b>{channel}</b>", "side": "top"},  # Bold label above bar
                "tickfont": {"size": 12, "color": "#555"},
                "thickness": 14,
                "len": 0.45,                     # Each color bar takes under half the height
                "y": 0.75 - i * 0.5,             # Stack color bars: top row, bottom row
            },
        )
    )

# Visual styling
fig.update_layout(
    height=360,                      # Fixed chart height (wide, short ratio fits 2 rows)
    margin={"l": 20, "r": 20, "t": 20, "b": 20},
    font={"family": "Segoe UI, Arial, sans-serif", "size": 14},
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis={
        "title": {"text": "Hour of day", "standoff": 16, "font": {"size": 14, "color": "#555"}},
        "tickfont": {"size": 13, "color": "#444"},   # Hour labels
        "showgrid": False,
    },
    yaxis={
        "title": None,
        "tickfont": {"size": 15, "color": "#222"},   # Channel labels (larger, darker)
        "ticklabelstandoff": 10,                     # Space between labels and cells
        "showgrid": False,
        "type": "category",                      # Show channel names, not numbers
        "categoryorder": "array",
        "categoryarray": channels,               # Fix row order
        "autorange": "reversed",                 # First channel on top
    },
)


# App Layout
app.layout = html.Div(
    style={
        "maxWidth": "1100px",        # Keep content from stretching too wide
        "margin": "0 auto",          # Center the page
        "padding": "40px 30px",      # Space around the page content
        "fontFamily": "Segoe UI, Arial, sans-serif",
    },
    children=[
        html.H1(
            "🧋 Rush Hour: Bubble tea shop Dashboard",  # Page heading
            style={
                "margin": "0 0 10px 0",
                "fontSize": "32px",
                "lineHeight": "1.3",
                "textAlign": "center",       # Center the heading
                "color": "#222",
            },
        ),
        html.P(
            "Analyzing peak rush hours and distribution across sales channels",  # Subtitle
            style={
                "margin": "0 0 32px 0",
                "fontSize": "16px",
                "lineHeight": "1.5",
                "textAlign": "center",       # Center the subtitle
                "color": "#666",
            },
        ),
        dcc.Graph(
            figure=fig,              # Display the heatmap
            config={"displayModeBar": False},  # Hide the Plotly toolbar
        ),
    ],
)


# Run the app locally (debug=True reloads on code changes)
if __name__ == "__main__":
    app.run(debug=True)
