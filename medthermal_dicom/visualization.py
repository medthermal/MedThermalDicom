"""
Interactive thermal DICOM visualization with temperature hover display.
"""

import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from typing import Optional, Dict, Any, Tuple, List, Union
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize
import base64
import io
from PIL import Image


class MedThermalViewer:
    """
    Professional thermal DICOM viewer with interactive temperature display.
    
    Provides comprehensive visualization capabilities including:
    - Interactive temperature hover display
    - Multiple colormap options
    - ROI analysis tools
    - Temperature profile analysis
    - Statistical overlays
    """
    
    def __init__(self, medthermal_dicom=None):
        """
        Initialize thermal viewer.
        
        Args:
            medthermal_dicom: MedThermalDicom instance to visualize
        """
        self.medthermal_dicom = medthermal_dicom
        self.current_colormap = 'jet'
        self.temperature_unit = 'Celsius'
        self.show_colorbar = True
        self.roi_overlays = []
        
        # Available colormaps for thermal imaging
        self.thermal_colormaps = {
            'jet': 'Jet (Classic)',
            'hot': 'Hot',
            'cool': 'Cool', 
            'rainbow': 'Rainbow',
            'viridis': 'Viridis',
            'plasma': 'Plasma',
            'inferno': 'Inferno',
            'magma': 'Magma',
            'iron': 'Iron',
            'thermal': 'Thermal',
            'grayscale': 'Grayscale'
        }
    
    def set_thermal_dicom(self, medthermal_dicom):
        """Set the thermal DICOM to visualize."""
        self.medthermal_dicom = medthermal_dicom
    
    def create_interactive_plot(self, 
                              width: int = 800, 
                              height: int = 600,
                              title: Optional[str] = None) -> go.Figure:
        """
        Create interactive Plotly figure with temperature hover display.
        
        Args:
            width: Figure width in pixels
            height: Figure height in pixels
            title: Plot title
            
        Returns:
            Plotly Figure object
        """
        if self.medthermal_dicom is None:
            raise ValueError("No thermal DICOM data loaded")
        
        # If temperature data exists, render as heatmap with temperature hover
        if self.medthermal_dicom.temperature_data is not None:
            temp_data = self.medthermal_dicom.temperature_data
            fig = go.Figure()
            fig.add_trace(go.Heatmap(
                z=temp_data,
                colorscale=self._get_plotly_colorscale(),
                showscale=self.show_colorbar,
                hovertemplate=f'<b>Position:</b> (%{{x}}, %{{y}})<br>' +
                              f'<b>Temperature:</b> %{{z:.2f}}°{self.temperature_unit[0]}<br>' +
                              '<extra></extra>',
                colorbar=dict(
                    title=dict(
                        text=f"Temperature ({self.temperature_unit})",
                        side="right"
                    )
                )
            ))
        else:
            # No temperature data: render image. If RGB, show as image; if grayscale, show without temperature hover
            thermal_array = self.medthermal_dicom.thermal_array
            if thermal_array is None:
                raise ValueError("No thermal data available")
            fig = go.Figure()
            if len(thermal_array.shape) == 3 and thermal_array.shape[2] == 3:
                # RGB image
                fig.add_trace(go.Image(z=thermal_array))
            else:
                # Grayscale image without temperature semantics
                fig.add_trace(go.Heatmap(
                    z=thermal_array,
                    colorscale=self._get_plotly_colorscale(),
                    showscale=self.show_colorbar,
                    hoverinfo='skip'
                ))
        
        # Add ROI overlays if any (only meaningful with temperature; but keep overlay drawing consistent)
        for roi in self.roi_overlays:
            self._add_roi_overlay(fig, roi)
        
        # Update layout
        fig.update_layout(
            title=title or "MedThermal DICOM Visualization",
            width=width,
            height=height,
            xaxis_title="X Position (pixels)",
            yaxis_title="Y Position (pixels)",
            yaxis=dict(scaleanchor="x", scaleratio=1),  # Maintain aspect ratio
            font=dict(size=12),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    
    def _create_hover_text(self, temp_data: np.ndarray) -> np.ndarray:
        """Create hover text array with temperature information."""
        hover_text = np.empty(temp_data.shape, dtype=object)
        
        for i in range(temp_data.shape[0]):
            for j in range(temp_data.shape[1]):
                temp = temp_data[i, j]
                hover_text[i, j] = f"Position: ({j}, {i})<br>Temperature: {temp:.2f}°{self.temperature_unit[0]}"
        
        return hover_text
    
    def _get_plotly_colorscale(self) -> str:
        """Get Plotly colorscale name from current colormap."""
        colormap_mapping = {
            'jet': 'Jet',
            'hot': 'Hot',
            'cool': 'Blues',
            'rainbow': 'Rainbow',
            'viridis': 'Viridis',
            'plasma': 'Plasma',
            'inferno': 'Inferno',
            'magma': 'Magma',
            'iron': 'Reds',
            'thermal': 'Hot',
            'grayscale': 'Greys'
        }
        return colormap_mapping.get(self.current_colormap, 'Jet')
    
    def add_roi_overlay(self, roi_mask: np.ndarray, 
                       roi_name: str = "ROI",
                       color: str = "white",
                       line_width: int = 2):
        """
        Add ROI overlay to the visualization.
        
        Args:
            roi_mask: Boolean mask defining the ROI
            roi_name: Name of the ROI
            color: Color of the ROI boundary
            line_width: Width of the ROI boundary line
        """
        roi_info = {
            'mask': roi_mask,
            'name': roi_name,
            'color': color,
            'line_width': line_width
        }
        self.roi_overlays.append(roi_info)
    
    def _add_roi_overlay(self, fig: go.Figure, roi_info: Dict[str, Any]):
        """Add ROI overlay to the figure."""
        mask = roi_info['mask']
        
        # Find contours of the ROI
        from scipy.ndimage import find_objects
        import cv2
        
        # Convert boolean mask to uint8
        mask_uint8 = (mask * 255).astype(np.uint8)
        
        # Find contours
        contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Add contours to the plot
        for contour in contours:
            # Extract x, y coordinates
            x_coords = contour[:, 0, 0]
            y_coords = contour[:, 0, 1]
            
            # Close the contour
            x_coords = np.append(x_coords, x_coords[0])
            y_coords = np.append(y_coords, y_coords[0])
            
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='lines',
                line=dict(color=roi_info['color'], width=roi_info['line_width']),
                name=roi_info['name'],
                showlegend=True,
                hoverinfo='name'
            ))
    
    def create_temperature_profile(self, 
                                 start_point: Tuple[int, int],
                                 end_point: Tuple[int, int]) -> go.Figure:
        """
        Create temperature profile along a line.
        
        Args:
            start_point: Starting point (row, col)
            end_point: Ending point (row, col)
            
        Returns:
            Plotly Figure with temperature profile
        """
        if self.thermal_dicom is None or self.thermal_dicom.temperature_data is None:
            raise ValueError("No temperature data available")
        
        temp_data = self.thermal_dicom.temperature_data
        
        # Create line coordinates
        r1, c1 = start_point
        r2, c2 = end_point
        
        # Number of points along the line
        num_points = max(abs(r2 - r1), abs(c2 - c1)) + 1
        
        # Generate line coordinates
        rows = np.linspace(r1, r2, num_points).astype(int)
        cols = np.linspace(c1, c2, num_points).astype(int)
        
        # Extract temperature values along the line
        temperatures = temp_data[rows, cols]
        distances = np.sqrt((rows - r1)**2 + (cols - c1)**2)
        
        # Create the profile plot
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=distances,
            y=temperatures,
            mode='lines+markers',
            name='Temperature Profile',
            line=dict(color='red', width=2),
            marker=dict(size=4),
            hovertemplate='<b>Distance:</b> %{x:.1f} pixels<br>' +
                         '<b>Temperature:</b> %{y:.2f}°C<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title="Temperature Profile",
            xaxis_title="Distance (pixels)",
            yaxis_title=f"Temperature ({self.temperature_unit})",
            font=dict(size=12),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    
    def create_temperature_histogram(self, roi_mask: Optional[np.ndarray] = None) -> go.Figure:
        """
        Create temperature distribution histogram.
        
        Args:
            roi_mask: Optional ROI mask to limit analysis
            
        Returns:
            Plotly Figure with histogram
        """
        if self.thermal_dicom is None or self.thermal_dicom.temperature_data is None:
            raise ValueError("No temperature data available")
        
        temp_data = self.thermal_dicom.temperature_data
        
        if roi_mask is not None:
            temperatures = temp_data[roi_mask]
            title_suffix = " (ROI)"
        else:
            temperatures = temp_data.flatten()
            title_suffix = " (Full Image)"
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=temperatures,
            nbinsx=50,
            name='Temperature Distribution',
            marker=dict(color='skyblue', line=dict(color='black', width=1)),
            hovertemplate='<b>Temperature Range:</b> %{x}<br>' +
                         '<b>Count:</b> %{y}<br>' +
                         '<extra></extra>'
        ))
        
        # Add statistics annotations
        mean_temp = np.mean(temperatures)
        std_temp = np.std(temperatures)
        
        fig.add_vline(x=mean_temp, line_dash="dash", line_color="red",
                     annotation_text=f"Mean: {mean_temp:.2f}°C")
        
        fig.update_layout(
            title=f"Temperature Distribution{title_suffix}",
            xaxis_title=f"Temperature ({self.temperature_unit})",
            yaxis_title="Count",
            font=dict(size=12),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    
    def create_dashboard_app(self, port: int = 8050, debug: bool = False) -> dash.Dash:
        """
        Create interactive Dash web application for thermal DICOM visualization.
        
        Args:
            port: Port number for the web server
            debug: Enable debug mode
            
        Returns:
            Dash application instance
        """
        app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        
        app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Thermal DICOM Viewer", className="text-center mb-4"),
                    html.Hr()
                ])
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Visualization Controls"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Colormap:"),
                                    dcc.Dropdown(
                                        id='colormap-dropdown',
                                        options=[
                                            {'label': v, 'value': k} 
                                            for k, v in self.thermal_colormaps.items()
                                        ],
                                        value=self.current_colormap,
                                        clearable=False
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label("Temperature Unit:"),
                                    dcc.Dropdown(
                                        id='unit-dropdown',
                                        options=[
                                            {'label': 'Celsius', 'value': 'Celsius'},
                                            {'label': 'Fahrenheit', 'value': 'Fahrenheit'},
                                            {'label': 'Kelvin', 'value': 'Kelvin'}
                                        ],
                                        value=self.temperature_unit,
                                        clearable=False
                                    )
                                ], width=6)
                            ]),
                            html.Br(),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Checklist(
                                        id='display-options',
                                        options=[
                                            {'label': 'Show Colorbar', 'value': 'colorbar'},
                                            {'label': 'Show Grid', 'value': 'grid'},
                                            {'label': 'Show Statistics', 'value': 'stats'}
                                        ],
                                        value=['colorbar'],
                                        inline=True
                                    )
                                ])
                            ])
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='thermal-image',
                        style={'height': '600px'}
                    )
                ], width=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Image Statistics"),
                        dbc.CardBody([
                            html.Div(id='image-stats')
                        ])
                    ]),
                    html.Br(),
                    dbc.Card([
                        dbc.CardHeader("Pixel Information"),
                        dbc.CardBody([
                            html.Div(id='pixel-info')
                        ])
                    ])
                ], width=4)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='temperature-histogram',
                        style={'height': '400px'}
                    )
                ], width=6),
                dbc.Col([
                    dcc.Graph(
                        id='temperature-profile',
                        style={'height': '400px'}
                    )
                ], width=6)
            ])
        ], fluid=True)
        
        # Callbacks
        @app.callback(
            [Output('thermal-image', 'figure'),
             Output('image-stats', 'children'),
             Output('temperature-histogram', 'figure')],
            [Input('colormap-dropdown', 'value'),
             Input('unit-dropdown', 'value'),
             Input('display-options', 'value')]
        )
        def update_visualization(colormap, unit, display_options):
            self.current_colormap = colormap
            self.temperature_unit = unit
            self.show_colorbar = 'colorbar' in display_options
            
            # Update main thermal image
            fig = self.create_interactive_plot()
            
            # Update statistics
            if self.thermal_dicom and self.thermal_dicom.temperature_data is not None:
                temp_data = self.thermal_dicom.temperature_data
                stats = self._calculate_image_statistics(temp_data)
                stats_display = self._format_statistics_display(stats)
            else:
                # Hide stats when no temperature values are available
                stats_display = html.P("No temperature data available")
            
            # Update histogram
            if self.thermal_dicom and self.thermal_dicom.temperature_data is not None:
                hist_fig = self.create_temperature_histogram()
            else:
                # Empty figure when no temperature
                hist_fig = go.Figure()
            
            return fig, stats_display, hist_fig
        
        @app.callback(
            Output('pixel-info', 'children'),
            [Input('thermal-image', 'hoverData')]
        )
        def update_pixel_info(hover_data):
            if hover_data is None or self.thermal_dicom is None:
                return html.P("Hover over the image to see pixel information")
            
            # If no temperature data or RGB image, do not display temperature values
            if self.thermal_dicom.temperature_data is None:
                point = hover_data['points'][0]
                x, y = int(point['x']), int(point['y'])
                return html.Div([
                    html.P(f"Position: ({x}, {y})"),
                    html.P("Temperature: N/A")
                ])
             
            point = hover_data['points'][0]
            x, y = int(point['x']), int(point['y'])
            
            # Get temperature at pixel
            temp = self.thermal_dicom.get_temperature_at_pixel(y, x)
            
            if temp is not None:
                return html.Div([
                    html.P(f"Position: ({x}, {y})"),
                    html.P(f"Temperature: {temp:.2f}°{self.temperature_unit[0]}"),
                    html.P(f"Pixel Value: {point.get('z', 'N/A')}")
                ])
            else:
                return html.P("Temperature data not available for this pixel")
        
        return app
    
    def _calculate_image_statistics(self, temp_data: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive image statistics."""
        return {
            'mean': float(np.mean(temp_data)),
            'median': float(np.median(temp_data)),
            'std': float(np.std(temp_data)),
            'min': float(np.min(temp_data)),
            'max': float(np.max(temp_data)),
            'range': float(np.max(temp_data) - np.min(temp_data)),
            'percentile_25': float(np.percentile(temp_data, 25)),
            'percentile_75': float(np.percentile(temp_data, 75))
        }
    
    def _format_statistics_display(self, stats: Dict[str, float]) -> html.Div:
        """Format statistics for display."""
        unit_symbol = self.temperature_unit[0]
        
        return html.Div([
            html.P(f"Mean: {stats['mean']:.2f}°{unit_symbol}"),
            html.P(f"Median: {stats['median']:.2f}°{unit_symbol}"),
            html.P(f"Std Dev: {stats['std']:.2f}°{unit_symbol}"),
            html.P(f"Min: {stats['min']:.2f}°{unit_symbol}"),
            html.P(f"Max: {stats['max']:.2f}°{unit_symbol}"),
            html.P(f"Range: {stats['range']:.2f}°{unit_symbol}"),
            html.Hr(),
            html.P(f"25th Percentile: {stats['percentile_25']:.2f}°{unit_symbol}"),
            html.P(f"75th Percentile: {stats['percentile_75']:.2f}°{unit_symbol}")
        ])
    
    def save_visualization(self, filepath: str, 
                         width: int = 1200, 
                         height: int = 800,
                         format: str = 'png'):
        """
        Save thermal visualization to file.
        
        Args:
            filepath: Output file path
            width: Image width in pixels
            height: Image height in pixels
            format: Output format ('png', 'jpg', 'svg', 'pdf')
        """
        fig = self.create_interactive_plot(width=width, height=height)
        
        if format.lower() == 'html':
            fig.write_html(filepath)
        else:
            fig.write_image(filepath, width=width, height=height, format=format)
    
    def export_temperature_data(self, filepath: str, roi_mask: Optional[np.ndarray] = None):
        """
        Export temperature data to CSV file.
        
        Args:
            filepath: Output CSV file path
            roi_mask: Optional ROI mask to limit export
        """
        if self.thermal_dicom is None or self.thermal_dicom.temperature_data is None:
            raise ValueError("No temperature data available")
        
        import pandas as pd
        
        temp_data = self.thermal_dicom.temperature_data
        
        if roi_mask is not None:
            # Export only ROI data
            rows, cols = np.where(roi_mask)
            temperatures = temp_data[rows, cols]
            
            df = pd.DataFrame({
                'Row': rows,
                'Column': cols,
                'Temperature': temperatures
            })
        else:
            # Export full image data
            rows, cols = temp_data.shape
            row_indices, col_indices = np.meshgrid(range(rows), range(cols), indexing='ij')
            
            df = pd.DataFrame({
                'Row': row_indices.flatten(),
                'Column': col_indices.flatten(),
                'Temperature': temp_data.flatten()
            })
        
        df.to_csv(filepath, index=False)


class ThermalColormapGenerator:
    """
    Generate custom colormaps for thermal imaging applications.
    """
    
    @staticmethod
    def create_medical_thermal_colormap():
        """Create a colormap optimized for medical thermal imaging."""
        from matplotlib.colors import LinearSegmentedColormap
        
        # Define colors for medical thermal imaging
        colors = [
            (0.0, 0.0, 0.5),  # Dark blue (cold)
            (0.0, 0.0, 1.0),  # Blue
            (0.0, 1.0, 1.0),  # Cyan
            (0.0, 1.0, 0.0),  # Green
            (1.0, 1.0, 0.0),  # Yellow
            (1.0, 0.5, 0.0),  # Orange
            (1.0, 0.0, 0.0),  # Red (hot)
            (1.0, 1.0, 1.0)   # White (very hot)
        ]
        
        n_bins = 256
        cmap = LinearSegmentedColormap.from_list('medical_thermal', colors, N=n_bins)
        
        return cmap
    
    @staticmethod
    def create_iron_colormap():
        """Create iron-like colormap for thermal imaging."""
        from matplotlib.colors import LinearSegmentedColormap
        
        colors = [
            (0.0, 0.0, 0.0),  # Black
            (0.2, 0.0, 0.2),  # Dark purple
            (0.5, 0.0, 0.0),  # Dark red
            (1.0, 0.0, 0.0),  # Red
            (1.0, 0.5, 0.0),  # Orange
            (1.0, 1.0, 0.0),  # Yellow
            (1.0, 1.0, 1.0)   # White
        ]
        
        n_bins = 256
        cmap = LinearSegmentedColormap.from_list('iron', colors, N=n_bins)
        
        return cmap