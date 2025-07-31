import plotly.graph_objects as go
import plotly.express as px
import json

# Parse the data
data = {"components": [{"layer": "Data Collection", "tools": ["/proc filesystem", "psutil library", "systemd API"]}, {"layer": "Resource Management", "tools": ["cgroups", "systemd units", "resource limits"]}, {"layer": "Monitoring", "tools": ["real-time monitoring", "alerting system", "logging"]}, {"layer": "Control Interface", "tools": ["web dashboard", "CLI commands", "REST API"]}]}

# Create a figure
fig = go.Figure()

# Define colors for each layer
colors = ['#1FB8CD', '#DB4545', '#2E8B57', '#5D878F']

# Define positions for layers (y-coordinates, top to bottom flow)
layer_y_positions = [3, 2, 1, 0]
layer_names = ["Control Interface", "Monitoring", "Resource Management", "Data Collection"]

# Add layer boxes and tools
y_positions = []
x_positions = []
labels = []
node_colors = []

# Create nodes for each layer and their tools
for i, component in enumerate(reversed(data['components'])):  # Reverse to match top-down flow
    layer = component['layer']
    tools = component['tools']
    
    # Main layer node
    y_positions.append(layer_y_positions[i])
    x_positions.append(0)
    labels.append(layer)
    node_colors.append(colors[i])
    
    # Tool nodes for each layer
    for j, tool in enumerate(tools):
        y_positions.append(layer_y_positions[i])
        x_positions.append((j + 1) * 1.5)
        labels.append(tool[:15])  # Limit to 15 characters
        node_colors.append(colors[i])

# Add connection arrows between layers
for i in range(len(layer_y_positions) - 1):
    fig.add_annotation(
        x=0, y=layer_y_positions[i] - 0.3,
        ax=0, ay=layer_y_positions[i+1] + 0.3,
        xref="x", yref="y",
        axref="x", ayref="y",
        arrowhead=2,
        arrowsize=1.5,
        arrowwidth=2,
        arrowcolor="#666666",
        showarrow=True
    )

# Create the scatter plot
fig.add_trace(go.Scatter(
    x=x_positions,
    y=y_positions,
    mode='markers+text',
    marker=dict(
        size=20,
        color=node_colors,
        line=dict(width=2, color='white')
    ),
    text=labels,
    textposition="middle center",
    textfont=dict(size=10, color='white'),
    hovertemplate='%{text}<extra></extra>',
    showlegend=False
))

# Update layout
fig.update_layout(
    title="RHEL CPU Memory Resource Manager",
    xaxis=dict(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        range=[-1, 5]
    ),
    yaxis=dict(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        range=[-0.5, 3.5]
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)

# Save the chart
fig.write_image("rhel_architecture_flowchart.png")