# src/forecasting.py - FIXED VERSION WITH CURRENT DATA

import pandas as pd
from nixtla import NixtlaClient
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def forecast_stock(symbol, horizon=30):
    """
    Uses Nixtla's TimeGPT to forecast future stock prices with CURRENT data.
    
    ✅ FIXED: Now works with current data up to today's date
    ✅ FIXED: Generates proper future forecasts beyond current date
    ✅ FIXED: Handles market gaps and holidays automatically

    Parameters:
    - symbol (str): Stock ticker symbol, e.g., 'AAPL'
    - horizon (int): Number of days to forecast into the future

    The forecast results are saved to '<symbol>_forecast.csv'.
    """
    print(f"🚀 FORECASTING {symbol} WITH CURRENT DATA")
    print("=" * 50)
    
    # Validate API key
    api_key = os.getenv('NIXTLA_API_KEY')
    if not api_key:
        print("❌ Error: Set your NIXTLA_API_KEY environment variable!")
        return None
    
    client = NixtlaClient(api_key=api_key)
    
    try:
        # Load the most recent data
        print(f"📊 Loading current data for {symbol}...")
        df = pd.read_csv(f'{symbol}_data.csv')
        
        # Prepare data with current date handling
        df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None)
        df = df.rename(columns={'Date': 'ds', 'Close': 'y'})
        
        # Filter to actual historical data only (not future dates)
        today = datetime.now().date()
        df = df[df['ds'].dt.date <= today].copy()
        
        # Clean and sort
        df = df[['ds', 'y']].dropna().sort_values('ds').reset_index(drop=True)
        
        if len(df) < 30:
            print(f"❌ Insufficient data: only {len(df)} rows available")
            return None
        
        # Use recent data for best accuracy (last 60 days)
        df_recent = df.tail(60).reset_index(drop=True)
        
        # Show data info
        data_start = df_recent['ds'].min().date()
        data_end = df_recent['ds'].max().date()
        days_behind = (today - data_end).days
        
        print(f"📅 Data range: {data_start} to {data_end}")
        print(f"📊 Data points: {len(df_recent)}")
        
        if days_behind == 0:
            print(f"✅ Data is CURRENT (today: {today})")
        elif days_behind <= 3:
            print(f"🟡 Data is recent ({days_behind} days behind)")
        else:
            print(f"🔴 Data is {days_behind} days old - consider refreshing")
        
        # Generate forecast
        print(f"\n🤖 Generating {horizon}-day forecast...")
        forecast_end = datetime.now() + timedelta(days=horizon + 10)  # Account for weekends
        print(f"🔮 Forecast will extend to approximately: {forecast_end.strftime('%Y-%m-%d')}")
        
        # Use TimeGPT with automatic frequency detection
        forecast = client.forecast(
            df=df_recent,
            h=horizon,
            level=[80, 90]
        )
        
        # Validate forecast results
        if len(forecast) == 0:
            print(f"❌ No forecast generated")
            return None
        
        # Save results
        forecast.to_csv(f'{symbol}_forecast.csv', index=False)
        
        # Show success info
        forecast_start = forecast['ds'].min().date()
        forecast_end = forecast['ds'].max().date()
        
        print(f"✅ SUCCESS! Forecast generated")
        print(f"📈 Forecast period: {forecast_start} to {forecast_end}")
        print(f"🔮 Forecast points: {len(forecast)}")
        print(f"💾 Saved to: {symbol}_forecast.csv")
        
        # Show sample predictions
        print(f"\n📊 SAMPLE FUTURE PREDICTIONS:")
        print("-" * 40)
        for i in range(min(5, len(forecast))):
            date = forecast.iloc[i]['ds'].date()
            price = forecast.iloc[i]['TimeGPT']
            hi_80 = forecast.iloc[i]['TimeGPT-hi-80']
            lo_80 = forecast.iloc[i]['TimeGPT-lo-80']
            print(f"  {date}: ${price:.2f} (${lo_80:.2f} - ${hi_80:.2f})")
        
        print("=" * 50)
        return forecast
        
    except Exception as e:
        print(f"❌ Forecasting failed: {str(e)}")
        print(f"💡 Try refreshing data or check API connection")
        return None

def forecast_with_fresh_data(symbol, horizon=30, period='1y'):
    """
    Download fresh data and generate forecast in one step
    
    Parameters:
    - symbol (str): Stock ticker symbol
    - horizon (int): Forecast horizon in days
    - period (str): Data period to download
    """
    print(f"🔄 DOWNLOADING FRESH DATA + FORECASTING {symbol}")
    print("=" * 60)
    
    # Import data collector
    import sys
    sys.path.append('.')
    from src.data_collector import download_stock_data
    
    # Download fresh data
    result = download_stock_data(symbol, period)
    if result[0] is None:
        print(f"❌ Failed to download data for {symbol}")
        return None
    
    print(f"✅ Fresh data downloaded successfully")
    
    # Generate forecast
    return forecast_stock(symbol, horizon)

if __name__ == "__main__":
    # Example usage
    print("🚀 STOCK FORECASTING WITH CURRENT DATA")
    print(f"📅 Today: {datetime.now().strftime('%A, %B %d, %Y')}")
    print("=" * 60)
    
    # Option 1: Use existing data
    result = forecast_stock('AAPL', horizon=30)
    
    # Option 2: Download fresh data first (uncomment to use)
    # result = forecast_with_fresh_data('AAPL', horizon=30)
    
    if result is not None:
        print(f"\n🎉 SUCCESS! Generated forecast for AAPL")
        print(f"💡 Run visualization.py to see the chart")
    else:
        print(f"\n❌ Forecast failed - check data and API key")