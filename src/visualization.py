# src/visualization.py

import matplotlib.pyplot as plt
import pandas as pd

def plot_forecast(symbol):
    """
    Creates a visualization showing historical stock prices and AI forecast.
    
    Parameters:
    - symbol (str): Stock ticker symbol, e.g., 'AAPL'
    
    Shows a plot with historical data and forecast predictions.
    """
    try:
        # Load historical data
        historical = pd.read_csv(f'{symbol}_data.csv')
        historical['Date'] = pd.to_datetime(historical['Date'], utc=True).dt.tz_localize(None)
        
        # Filter to recent historical data (last 6 months for better visualization)
        historical = historical[historical['Date'] >= '2024-07-01']
        historical = historical[historical['Date'] < '2025-01-01']  # Only actual historical data
        
        # Load forecast data
        forecast = pd.read_csv(f'{symbol}_forecast.csv')
        forecast['ds'] = pd.to_datetime(forecast['ds'])
        
        # Create the plot
        plt.figure(figsize=(15, 8))
        
        # Plot historical data
        plt.plot(historical['Date'], historical['Close'], 
                label='Historical Prices', color='#2E86AB', linewidth=2.5)
        
        # Plot forecast
        plt.plot(forecast['ds'], forecast['TimeGPT'], 
                label='AI Forecast (TimeGPT)', color='#F24236', linewidth=2.5, linestyle='--')
        
        # Plot confidence intervals
        plt.fill_between(forecast['ds'], 
                        forecast['TimeGPT-lo-80'], 
                        forecast['TimeGPT-hi-80'],
                        alpha=0.3, color='#F24236', label='80% Confidence Interval')
        
        plt.fill_between(forecast['ds'], 
                        forecast['TimeGPT-lo-90'], 
                        forecast['TimeGPT-hi-90'],
                        alpha=0.2, color='#F24236', label='90% Confidence Interval')
        
        # Customize the plot
        plt.title(f'{symbol} Stock Price Forecast - AI Powered by TimeGPT', 
                 fontsize=18, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=14, fontweight='bold')
        plt.ylabel('Stock Price ($)', fontsize=14, fontweight='bold')
        plt.legend(fontsize=12, loc='upper left')
        plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        plt.xticks(rotation=45, fontsize=11)
        plt.yticks(fontsize=11)
        
        # Add annotations
        last_price = historical['Close'].iloc[-1]
        first_forecast = forecast['TimeGPT'].iloc[0]
        
        plt.annotate(f'Last Price: ${last_price:.2f}', 
                    xy=(historical['Date'].iloc[-1], last_price),
                    xytext=(10, 10), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7),
                    fontsize=10, fontweight='bold')
        
        plt.annotate(f'Forecast Start: ${first_forecast:.2f}', 
                    xy=(forecast['ds'].iloc[0], first_forecast),
                    xytext=(10, -20), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7),
                    fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(f'{symbol}_forecast_chart.png', dpi=300, bbox_inches='tight')
        
        # Show the plot
        plt.show()
        
        print(f"✅ Displayed forecast visualization for {symbol}")
        print(f"📊 Chart saved as {symbol}_forecast_chart.png")
        print(f"📈 Historical data: {len(historical)} days")
        print(f"🔮 Forecast: {len(forecast)} business days")
        
    except Exception as e:
        print(f"❌ Visualization failed: {str(e)}")

if __name__ == "__main__":
    plot_forecast('AAPL')  # Change to any stock symbol you've forecasted
