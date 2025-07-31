import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Load the data
df = pd.read_csv('system_resource_monitoring_data.csv')

# Convert timestamp to datetime and extract hour for x-axis formatting
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.strftime('%H:%M')

# Create the line chart
fig = go.Figure()

# Add CPU usage line
fig.add_trace(go.Scatter(
    x=df['hour'],
    y=df['cpu_usage'],
    mode='lines',
    name='CPU',
    line=dict(color='#1FB8CD'),
    cliponaxis=False
))

# Add Memory usage line  
fig.add_trace(go.Scatter(
    x=df['hour'],
    y=df['memory_usage'],
    mode='lines',
    name='Memory',
    line=dict(color='#DB4545'),
    cliponaxis=False
))

# Add horizontal reference lines at 80%
fig.add_hline(y=80, line_dash="dash", line_color="gray", opacity=0.7)

# Update layout
fig.update_layout(
    title="24Hr Resource Monitor",
    xaxis_title="Time (Hours)",
    yaxis_title="Usage %",
    yaxis=dict(range=[0, 100]),
    legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5)
)

# Update x-axis to show fewer tick marks for readability
fig.update_xaxes(
    tickmode='array',
    tickvals=df['hour'][::len(df)//12]  # Show approximately 12 ticks
)

# Save the chart
fig.write_image("system_resource_chart.png")