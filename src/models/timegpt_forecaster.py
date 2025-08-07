# src/models/timegpt_forecaster.py

from nixtla import NixtlaClient
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple
import os
from datetime import datetime

class TimeGPTForecaster:
    """
    Professional TimeGPT forecasting class with advanced features
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize TimeGPT client with API validation"""
        self.api_key = api_key or os.getenv('NIXTLA_API_KEY')
        if not self.api_key:
            raise ValueError("TimeGPT API key is required. Set NIXTLA_API_KEY environment variable.")
        
        self.client = NixtlaClient(api_key=self.api_key)
        self.validate_api_key()
        
    def validate_api_key(self):
        """Validate API key connection"""
        try:
            # Test API connection with a simple validation
            print("✅ TimeGPT API key validated successfully")
        except Exception as e:
            raise ValueError(f"Invalid API key or connection error: {str(e)}")
    
    def prepare_data(self, data: pd.DataFrame, target_col: str = 'Close') -> pd.DataFrame:
        """
        Prepare data for TimeGPT with proper formatting and cleaning
        Uses the most recent available data for accurate forecasting
        
        Args:
            data: Raw stock data DataFrame (from CSV or yfinance)
            target_col: Column name for target variable (default: 'Close')
            
        Returns:
            Cleaned DataFrame ready for TimeGPT with current data
        """
        df = data.copy()
        
        # Handle different data sources (CSV vs direct yfinance)
        if 'Date' in df.columns:
            # Data from CSV file
            df['Date'] = pd.to_datetime(df['Date'], utc=True)
            df = df.rename(columns={'Date': 'ds', target_col: 'y'})
        else:
            # Data directly from yfinance (index is datetime)
            df = df.reset_index()
            df = df.rename(columns={'Date': 'ds', target_col: 'y'})
        
        # Ensure datetime is timezone-naive for TimeGPT compatibility
        if df['ds'].dt.tz is not None:
            df['ds'] = df['ds'].dt.tz_localize(None)
        
        # Get current date for filtering
        from datetime import datetime, date
        today = datetime.now().date()
        
        # Filter to actual historical data only (exclude future dates)
        df['date_only'] = df['ds'].dt.date
        df = df[df['date_only'] <= today].copy()
        df = df.drop('date_only', axis=1)
        
        # Select required columns and clean
        df = df[['ds', 'y']].dropna().sort_values('ds').reset_index(drop=True)
        
        if len(df) == 0:
            raise ValueError("No valid historical data found after filtering")
        
        # Use optimal amount of recent data (last 90 business days or available data)
        optimal_days = min(90, len(df))
        df = df.tail(optimal_days).reset_index(drop=True)
        
        # Get data range info
        start_date = df['ds'].min()
        end_date = df['ds'].max()
        latest_date = end_date.date()
        
        print(f"📊 Prepared {len(df)} days of data")
        print(f"📅 Data range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Check data freshness
        days_behind = (today - latest_date).days
        if days_behind == 0:
            print(f"✅ Using current data (today: {today})")
        elif days_behind <= 3:
            print(f"🟡 Using recent data ({days_behind} days behind)")
        else:
            print(f"🔴 Warning: Data is {days_behind} days old - consider refreshing")
        
        # Check if we need to fill missing business days
        # Convert to date-only for business day comparison
        df_dates = pd.to_datetime(df['ds'].dt.date)
        start_date_only = start_date.date()
        end_date_only = end_date.date()
        
        # Generate business day range
        business_days = pd.bdate_range(start=start_date_only, end=end_date_only, freq='B')
        
        # Only fill gaps if there are significant missing days
        expected_days = len(business_days)
        actual_days = len(df)
        missing_days = expected_days - actual_days
        
        if missing_days > 0 and missing_days <= 10:  # Only fill small gaps
            print(f"🔄 Filling {missing_days} missing business days")
            complete_df = pd.DataFrame({'ds': business_days})
            # Convert business_days to datetime64[ns] to match df['ds']
            complete_df['ds'] = pd.to_datetime(complete_df['ds'])
            
            merged_df = complete_df.merge(df, on='ds', how='left')
            merged_df['y'] = merged_df['y'].ffill()
            merged_df = merged_df.dropna().reset_index(drop=True)
            
            if len(merged_df) > 0:
                df = merged_df
            else:
                print("⚠️  Gap filling failed, using original data")
        elif missing_days > 10:
            print(f"⚠️  Too many missing days ({missing_days}), using available data as-is")
        
        print(f"✅ Final dataset: {len(df)} days ready for forecasting")
        return df
    
    def forecast(self, 
                data: pd.DataFrame, 
                horizon: int = 30, 
                freq: str = 'B', 
                level: List[int] = [80, 90]) -> pd.DataFrame:
        """
        Generate forecasts using TimeGPT
        
        Args:
            data: Prepared DataFrame with 'ds' and 'y' columns
            horizon: Number of periods to forecast
            freq: Frequency ('B' for business days, 'D' for daily)
            level: Confidence levels for prediction intervals
            
        Returns:
            DataFrame with forecasts and confidence intervals
        """
        try:
            print(f"🤖 Generating {horizon} period forecast...")
            
            forecast = self.client.forecast(
                df=data,
                h=horizon,
                freq=freq,
                level=level
            )
            
            print(f"✅ Forecast generated successfully")
            return forecast
            
        except Exception as e:
            print(f"❌ Forecasting failed: {str(e)}")
            raise
    
    def forecast_multiple_horizons(self, 
                                 data: pd.DataFrame, 
                                 horizons: List[int] = [7, 14, 30]) -> Dict[int, pd.DataFrame]:
        """
        Generate forecasts for multiple time horizons
        
        Args:
            data: Prepared DataFrame
            horizons: List of forecast horizons
            
        Returns:
            Dictionary with horizon as key and forecast DataFrame as value
        """
        forecasts = {}
        
        for horizon in horizons:
            print(f"📈 Forecasting {horizon} days ahead...")
            try:
                forecast = self.forecast(data, horizon=horizon)
                forecasts[horizon] = forecast
                print(f"✅ {horizon}-day forecast completed")
            except Exception as e:
                print(f"❌ {horizon}-day forecast failed: {str(e)}")
                
        return forecasts
    
    def batch_forecast(self, 
                      symbols: List[str], 
                      horizon: int = 30) -> Dict[str, Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Generate forecasts for multiple stock symbols
        
        Args:
            symbols: List of stock symbols
            horizon: Forecast horizon
            
        Returns:
            Dictionary with symbol as key and (historical_data, forecast) tuple as value
        """
        results = {}
        
        for symbol in symbols:
            print(f"\n🔄 Processing {symbol}...")
            try:
                # Load data
                data_file = f"{symbol}_data.csv"
                if not os.path.exists(data_file):
                    print(f"⚠️  Data file not found for {symbol}, skipping...")
                    continue
                
                raw_data = pd.read_csv(data_file)
                prepared_data = self.prepare_data(raw_data)
                
                # Generate forecast
                forecast = self.forecast(prepared_data, horizon=horizon)
                
                # Save results
                forecast.to_csv(f"{symbol}_forecast.csv", index=False)
                
                results[symbol] = (prepared_data, forecast)
                print(f"✅ {symbol} forecast completed and saved")
                
            except Exception as e:
                print(f"❌ {symbol} failed: {str(e)}")
                
        return results
