"""
Stock Forecasting Dashboard - Core Package

A comprehensive AI-powered stock market forecasting system with real-time data,
technical analysis, and interactive web dashboard.

Author: Your Name
Email: your.email@example.com
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .data_collector import StockDataCollector
from .forecasting import StockForecaster

__all__ = [
    "StockDataCollector",
    "StockForecaster",
]
