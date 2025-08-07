# src/visualization/results_plotter.py

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

class ResultsPlotter:
    """
    Advanced interactive visualization system for stock forecasts
    """
    
    def __init__(self):
        self.colors = {
            'historical': '#2E86AB',
            'forecast': '#F24236',
            'confidence_80': 'rgba(242, 66, 54, 0.3)',
            'confidence_90': 'rgba(242, 66, 54, 0.2)',
            'grid': 'rgba(128, 128, 128, 0.2)',
            'background': 'white'
        }
    
    def plot_forecast_results(self, 
                            historical_data: pd.DataFrame, 
                            forecast_data: pd.DataFrame, 
                            symbol: str,
                            save_html: bool = True) -> go.Figure:
        """
        Create interactive forecast visualization with subplots
        
        Args:
            historical_data: DataFrame with 'ds' and 'y' columns
            forecast_data: DataFrame with forecast results
            symbol: Stock symbol
            save_html: Whether to save as HTML file
            
        Returns:
            Plotly Figure object
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(
                f'{symbol} Stock Price Forecast - AI Powered by TimeGPT',
                'Prediction Intervals & Confidence Bands'
            ),
            vertical_spacing=0.12,
            row_heights=[0.7, 0.3]
        )
        
        # Main forecast plot
        self._add_main_forecast_traces(fig, historical_data, forecast_data, symbol)
        
        # Confidence intervals plot
        self._add_confidence_interval_plot(fig, forecast_data, symbol)
        
        # Update layout
        self._update_layout(fig, symbol)
        
        if save_html:
            fig.write_html(f"{symbol}_interactive_forecast.html")
            print(f"💾 Interactive chart saved as {symbol}_interactive_forecast.html")
        
        return fig
    
    def _add_main_forecast_traces(self, 
                                fig: go.Figure, 
                                historical: pd.DataFrame, 
                                forecast: pd.DataFrame, 
                                symbol: str):
        """Add main forecast traces to the figure"""
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=historical['ds'],
            y=historical['y'],
            name='Historical Prices',
            line=dict(color=self.colors['historical'], width=2.5),
            hovertemplate='<b>Historical</b><br>' +
                         'Date: %{x}<br>' +
                         'Price: $%{y:.2f}<br>' +
                         '<extra></extra>',
            showlegend=True
        ), row=1, col=1)
        
        # Forecast line
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['TimeGPT'],
            name='AI Forecast',
            line=dict(color=self.colors['forecast'], width=3, dash='dash'),
            hovertemplate='<b>AI Forecast</b><br>' +
                         'Date: %{x}<br>' +
                         'Predicted Price: $%{y:.2f}<br>' +
                         '<extra></extra>',
            showlegend=True
        ), row=1, col=1)
        
        # 90% Confidence interval (outer)
        if 'TimeGPT-hi-90' in forecast.columns:
            fig.add_trace(go.Scatter(
                x=forecast['ds'],
                y=forecast['TimeGPT-hi-90'],
                fill=None,
                mode='lines',
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False,
                hoverinfo='skip'
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=forecast['ds'],
                y=forecast['TimeGPT-lo-90'],
                fill='tonexty',
                fillcolor=self.colors['confidence_90'],
                mode='lines',
                line=dict(color='rgba(0,0,0,0)'),
                name='90% Confidence',
                hovertemplate='<b>90% Confidence Interval</b><br>' +
                             'Upper: $%{customdata[0]:.2f}<br>' +
                             'Lower: $%{y:.2f}<br>' +
                             '<extra></extra>',
                customdata=forecast['TimeGPT-hi-90'].values.reshape(-1, 1)
            ), row=1, col=1)
        
        # 80% Confidence interval (inner)
        if 'TimeGPT-hi-80' in forecast.columns:
            fig.add_trace(go.Scatter(
                x=forecast['ds'],
                y=forecast['TimeGPT-hi-80'],
                fill=None,
                mode='lines',
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False,
                hoverinfo='skip'
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=forecast['ds'],
                y=forecast['TimeGPT-lo-80'],
                fill='tonexty',
                fillcolor=self.colors['confidence_80'],
                mode='lines',
                line=dict(color='rgba(0,0,0,0)'),
                name='80% Confidence',
                hovertemplate='<b>80% Confidence Interval</b><br>' +
                             'Upper: $%{customdata[0]:.2f}<br>' +
                             'Lower: $%{y:.2f}<br>' +
                             '<extra></extra>',
                customdata=forecast['TimeGPT-hi-80'].values.reshape(-1, 1)
            ), row=1, col=1)
    
    def _add_confidence_interval_plot(self, 
                                    fig: go.Figure, 
                                    forecast: pd.DataFrame, 
                                    symbol: str):
        """Add confidence interval analysis to second subplot"""
        
        if 'TimeGPT-hi-80' in forecast.columns and 'TimeGPT-lo-80' in forecast.columns:
            # Calculate confidence interval widths
            ci_80_width = forecast['TimeGPT-hi-80'] - forecast['TimeGPT-lo-80']
            ci_90_width = forecast['TimeGPT-hi-90'] - forecast['TimeGPT-lo-90'] if 'TimeGPT-hi-90' in forecast.columns else None
            
            # Plot confidence interval widths
            fig.add_trace(go.Scatter(
                x=forecast['ds'],
                y=ci_80_width,
                name='80% CI Width',
                line=dict(color='orange', width=2),
                hovertemplate='<b>80% Confidence Width</b><br>' +
                             'Date: %{x}<br>' +
                             'Width: $%{y:.2f}<br>' +
                             '<extra></extra>'
            ), row=2, col=1)
            
            if ci_90_width is not None:
                fig.add_trace(go.Scatter(
                    x=forecast['ds'],
                    y=ci_90_width,
                    name='90% CI Width',
                    line=dict(color='red', width=2),
                    hovertemplate='<b>90% Confidence Width</b><br>' +
                                 'Date: %{x}<br>' +
                                 'Width: $%{y:.2f}<br>' +
                                 '<extra></extra>'
                ), row=2, col=1)
    
    def _update_layout(self, fig: go.Figure, symbol: str):
        """Update figure layout with professional styling"""
        
        fig.update_layout(
            title=dict(
                text=f"<b>{symbol} Stock Forecast Analysis</b><br><sub>Interactive AI-Powered Prediction Dashboard</sub>",
                x=0.5,
                font=dict(size=20, color='#2C3E50')
            ),
            plot_bgcolor=self.colors['background'],
            paper_bgcolor=self.colors['background'],
            font=dict(family="Arial, sans-serif", size=12, color='#2C3E50'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.2)',
                borderwidth=1
            ),
            hovermode='x unified',
            height=800
        )
        
        # Update axes
        fig.update_xaxes(
            title_text="Date",
            showgrid=True,
            gridwidth=1,
            gridcolor=self.colors['grid'],
            showline=True,
            linewidth=1,
            linecolor='rgba(0,0,0,0.3)'
        )
        
        fig.update_yaxes(
            title_text="Stock Price ($)",
            showgrid=True,
            gridwidth=1,
            gridcolor=self.colors['grid'],
            showline=True,
            linewidth=1,
            linecolor='rgba(0,0,0,0.3)',
            row=1, col=1
        )
        
        fig.update_yaxes(
            title_text="Confidence Interval Width ($)",
            showgrid=True,
            gridwidth=1,
            gridcolor=self.colors['grid'],
            showline=True,
            linewidth=1,
            linecolor='rgba(0,0,0,0.3)',
            row=2, col=1
        )
    
    def create_multi_stock_dashboard(self, 
                                   results: Dict[str, Tuple[pd.DataFrame, pd.DataFrame]],
                                   save_html: bool = True) -> go.Figure:
        """
        Create a comprehensive dashboard for multiple stocks
        
        Args:
            results: Dictionary with symbol as key and (historical, forecast) tuple as value
            save_html: Whether to save as HTML file
            
        Returns:
            Plotly Figure object
        """
        symbols = list(results.keys())
        n_stocks = len(symbols)
        
        # Create subplots grid
        rows = (n_stocks + 1) // 2  # 2 columns
        cols = 2
        
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=[f"{symbol} Forecast" for symbol in symbols],
            vertical_spacing=0.08,
            horizontal_spacing=0.08
        )
        
        for idx, symbol in enumerate(symbols):
            row = (idx // 2) + 1
            col = (idx % 2) + 1
            
            historical, forecast = results[symbol]
            
            # Add historical data
            fig.add_trace(go.Scatter(
                x=historical['ds'],
                y=historical['y'],
                name=f'{symbol} Historical',
                line=dict(color=self.colors['historical'], width=2),
                showlegend=(idx == 0)  # Only show legend for first stock
            ), row=row, col=col)
            
            # Add forecast
            fig.add_trace(go.Scatter(
                x=forecast['ds'],
                y=forecast['TimeGPT'],
                name=f'{symbol} Forecast',
                line=dict(color=self.colors['forecast'], width=2, dash='dash'),
                showlegend=(idx == 0)
            ), row=row, col=col)
            
            # Add confidence intervals if available
            if 'TimeGPT-hi-80' in forecast.columns:
                fig.add_trace(go.Scatter(
                    x=forecast['ds'],
                    y=forecast['TimeGPT-hi-80'],
                    fill=None,
                    mode='lines',
                    line=dict(color='rgba(0,0,0,0)'),
                    showlegend=False,
                    hoverinfo='skip'
                ), row=row, col=col)
                
                fig.add_trace(go.Scatter(
                    x=forecast['ds'],
                    y=forecast['TimeGPT-lo-80'],
                    fill='tonexty',
                    fillcolor=self.colors['confidence_80'],
                    mode='lines',
                    line=dict(color='rgba(0,0,0,0)'),
                    name='80% Confidence' if idx == 0 else None,
                    showlegend=(idx == 0)
                ), row=row, col=col)
        
        # Update layout
        fig.update_layout(
            title=dict(
                text="<b>Multi-Stock AI Forecast Dashboard</b><br><sub>TimeGPT Predictions Across Portfolio</sub>",
                x=0.5,
                font=dict(size=24, color='#2C3E50')
            ),
            plot_bgcolor=self.colors['background'],
            paper_bgcolor=self.colors['background'],
            font=dict(family="Arial, sans-serif", size=10, color='#2C3E50'),
            height=300 * rows,
            hovermode='x unified'
        )
        
        # Update all axes
        fig.update_xaxes(showgrid=True, gridcolor=self.colors['grid'])
        fig.update_yaxes(showgrid=True, gridcolor=self.colors['grid'], title_text="Price ($)")
        
        if save_html:
            fig.write_html("multi_stock_dashboard.html")
            print(f"💾 Multi-stock dashboard saved as multi_stock_dashboard.html")
        
        return fig
    
    def create_performance_comparison(self, 
                                    performance_data: Dict[str, Dict[str, float]],
                                    save_html: bool = True) -> go.Figure:
        """
        Create interactive performance comparison chart
        
        Args:
            performance_data: Dict with symbol as key and metrics dict as value
            save_html: Whether to save as HTML file
            
        Returns:
            Plotly Figure object
        """
        symbols = list(performance_data.keys())
        metrics = ['MAPE', 'Directional_Accuracy', 'R²']
        
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('MAPE (%)', 'Directional Accuracy (%)', 'R² Score'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
        )
        
        for i, metric in enumerate(metrics):
            values = [performance_data[symbol].get(metric, 0) for symbol in symbols]
            
            # Color coding based on performance
            colors = []
            for val in values:
                if metric == 'MAPE':
                    colors.append('green' if val < 10 else 'orange' if val < 20 else 'red')
                elif metric == 'Directional_Accuracy':
                    colors.append('green' if val > 70 else 'orange' if val > 60 else 'red')
                else:  # R²
                    colors.append('green' if val > 0.6 else 'orange' if val > 0.4 else 'red')
            
            fig.add_trace(go.Bar(
                x=symbols,
                y=values,
                name=metric,
                marker_color=colors,
                text=[f'{v:.2f}' for v in values],
                textposition='auto',
                showlegend=False
            ), row=1, col=i+1)
        
        fig.update_layout(
            title="<b>Model Performance Comparison Across Stocks</b>",
            height=500,
            showlegend=False
        )
        
        if save_html:
            fig.write_html("performance_comparison.html")
            print(f"💾 Performance comparison saved as performance_comparison.html")
        
        return fig
