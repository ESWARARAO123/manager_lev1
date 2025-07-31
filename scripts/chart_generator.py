#!/usr/bin/env python3.12
"""
Chart generation utilities for RHEL Resource Manager
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any

class ChartGenerator:
    """Generate various charts and visualizations"""
    
    @staticmethod
    def create_architecture_flowchart(data: Dict[str, Any], output_file: str = "rhel_architecture_flowchart.png"):
        """Create architecture flowchart"""
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
        for i, component in enumerate(reversed(data.get('components', []))):
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
        fig.write_image(output_file)
        return output_file
    
    @staticmethod
    def create_resource_flowchart(data: Dict[str, Any], output_file: str = "rhel_resource_manager_flowchart.png"):
        """Create resource manager deployment flowchart"""
        # Create DataFrame
        df = pd.DataFrame(data.get('steps', []))
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
            color = phase_colors.get(row['phase'], '#666666')
            
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
        fig.write_image(output_file)
        return output_file
    
    @staticmethod
    def create_resource_monitoring_chart(data_file: str, output_file: str = "system_resource_chart.png"):
        """Create resource monitoring chart from CSV data"""
        # Load the data
        df = pd.read_csv(data_file)
        
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
        fig.write_image(output_file)
        return output_file 