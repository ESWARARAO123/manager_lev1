import plotly.graph_objects as go
import plotly.express as px
import json
import pandas as pd

# Load the data
data = {
    "steps": [
        {"phase": "Setup", "step": "System Setup", "details": "Install deps, Check RHEL"}, 
        {"phase": "Development", "step": "Core Dev", "details": "Python + psutil + cgroups"}, 
        {"phase": "Configuration", "step": "Configuration", "details": "Config + systemd"}, 
        {"phase": "Deployment", "step": "Installation", "details": "Deploy + Enable + Perms"}, 
        {"phase": "Testing", "step": "Testing", "details": "Start + Test + Monitor"}, 
        {"phase": "Management", "step": "Management", "details": "CLI + Dashboard + Alerts"}
    ]
}

# Create DataFrame
df = pd.DataFrame(data['steps'])
df['sequence'] = range(1, len(df) + 1)

# Define colors for phases
phase_colors = {
    'Setup': '#1FB8CD',
    'Development': '#DB4545', 
    'Configuration': '#2E8B57',
    'Deployment': '#5D878F',
    'Testing': '#D2BA4C',
    'Management': '#B4413C'
}

# Create the flowchart
fig = go.Figure()

# Add connecting lines with arrows
for i in range(len(df) - 1):
    fig.add_trace(go.Scatter(
        x=[df.iloc[i]['sequence'], df.iloc[i+1]['sequence']], 
        y=[2, 2],
        mode='lines',
        line=dict(color='gray', width=2),
        showlegend=False,
        hoverinfo='skip',
        cliponaxis=False
    ))
    
    # Add arrow annotation
    fig.add_annotation(
        x=df.iloc[i]['sequence'] + 0.5,
        y=2,
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='gray',
        ax=0,
        ay=0
    )

# Add rectangular boxes for each step
box_width = 0.4
box_height = 0.6

for i, row in df.iterrows():
    step_name = row['step'][:15]
    details = row['details'][:15]
    color = phase_colors[row['phase']]
    
    # Add rectangle
    fig.add_shape(
        type="rect",
        x0=row['sequence'] - box_width/2,
        y0=2 - box_height/2,
        x1=row['sequence'] + box_width/2,
        y1=2 + box_height/2,
        fillcolor=color,
        line=dict(color='white', width=2),
    )
    
    # Add step name text
    fig.add_trace(go.Scatter(
        x=[row['sequence']],
        y=[2],
        mode='text',
        text=[step_name],
        textfont=dict(size=10, color='white'),
        showlegend=False,
        hovertemplate=f"<b>{step_name}</b><br>{details}<br><extra></extra>",
        cliponaxis=False
    ))
    
    # Add phase label below
    fig.add_trace(go.Scatter(
        x=[row['sequence']],
        y=[1.2],
        mode='text',
        text=[row['phase']],
        textfont=dict(size=8, color=color),
        showlegend=False,
        hoverinfo='skip',
        cliponaxis=False
    ))
    
    # Add details text below phase
    fig.add_trace(go.Scatter(
        x=[row['sequence']],
        y=[1.0],
        mode='text',
        text=[details],
        textfont=dict(size=7, color='gray'),
        showlegend=False,
        hoverinfo='skip',
        cliponaxis=False
    ))

# Update layout
fig.update_layout(
    title="RHEL Resource Mgr Deploy Flow",
    xaxis=dict(
        tickmode='linear',
        tick0=1,
        dtick=1,
        range=[0.5, 6.5],
        showticklabels=False,
        showgrid=False,
        zeroline=False
    ),
    yaxis=dict(
        range=[0.5, 2.8],
        showticklabels=False,
        showgrid=False,
        zeroline=False
    ),
    showlegend=False,
    plot_bgcolor='white'
)

# Save the chart
fig.write_image("rhel_resource_manager_flowchart.png")