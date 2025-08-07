# src/data_collector.py

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, date
import warnings
warnings.filterwarnings('ignore')

def download_stock_data(symbol, period='2y', force_refresh=True):
    """
    Downloads the latest historical stock data using yfinance and saves it as a CSV file.
    Always fetches data up to the most recent available date.

    Parameters:
    - symbol (str): The stock ticker symbol, e.g., 'AAPL' for Apple.
    - period (str): How far back to go, default is 2 years ('2y').
    - force_refresh (bool): Always download fresh data, ignore existing files.

    The data is saved as '<symbol>_data.csv' in your project folder.
    """
    print(f"📥 Downloading latest data for {symbol}...")
    
    try:
        # Get current date info for validation
        today = datetime.now().date()
        
        # Download data with extended period to ensure we have recent data
        ticker = yf.Ticker(symbol)
        
        # Try different approaches to get the most recent data
        print(f"  🔄 Fetching {period} of data ending {today}...")
        df = ticker.history(period=period, auto_adjust=True, prepost=True)
        
        if df.empty:
            print(f"  ⚠️  No data returned for {symbol}, trying alternative method...")
            # Try with explicit date range
            start_date = today - timedelta(days=730)  # ~2 years
            df = ticker.history(start=start_date, end=today, auto_adjust=True)
        
        if df.empty:
            raise ValueError(f"No data available for {symbol}")
        
        # Clean and validate the data
        df = df.dropna()
        
        if len(df) < 50:
            print(f"  ⚠️  Warning: Only {len(df)} rows of data for {symbol}")
        
        # Get the latest available date in the data
        latest_date = df.index[-1].date()
        oldest_date = df.index[0].date()
        
        # Check data freshness
        days_behind = (today - latest_date).days
        
        if days_behind == 0:
            freshness_msg = "✅ Current (today's data)"
        elif days_behind == 1:
            freshness_msg = "✅ Fresh (yesterday's data)"
        elif days_behind <= 3:
            freshness_msg = f"🟡 Recent ({days_behind} days behind)"
        else:
            freshness_msg = f"🔴 Outdated ({days_behind} days behind)"
        
        # Save the data
        df.to_csv(f'{symbol}_data.csv')
        
        # Print detailed information
        print(f"  ✅ {symbol}: {len(df)} rows")
        print(f"  📅 Date range: {oldest_date} to {latest_date}")
        print(f"  🔄 Data freshness: {freshness_msg}")
        print(f"  💾 Saved to: {symbol}_data.csv")
        
        return df, latest_date, days_behind
        
    except Exception as e:
        print(f"  ❌ Error downloading {symbol}: {str(e)}")
        return None, None, None

def download_multiple_stocks(symbols, period='2y'):
    """
    Download data for multiple stocks with summary reporting
    
    Parameters:
    - symbols (list): List of stock symbols
    - period (str): Data period to download
    
    Returns:
    - dict: Results summary with success/failure info
    """
    print(f"\n📊 BATCH DATA DOWNLOAD - {len(symbols)} STOCKS")
    print("=" * 60)
    
    results = {
        'successful': [],
        'failed': [],
        'freshness_report': {},
        'summary': {}
    }
    
    for symbol in symbols:
        df, latest_date, days_behind = download_stock_data(symbol, period)
        
        if df is not None:
            results['successful'].append(symbol)
            results['freshness_report'][symbol] = {
                'latest_date': latest_date,
                'days_behind': days_behind,
                'rows': len(df)
            }
        else:
            results['failed'].append(symbol)
    
    # Generate summary
    total_symbols = len(symbols)
    successful_count = len(results['successful'])
    
    print(f"\n📈 DOWNLOAD SUMMARY:")
    print(f"  • Total symbols: {total_symbols}")
    print(f"  • Successful: {successful_count}")
    print(f"  • Failed: {len(results['failed'])}")
    
    if results['failed']:
        print(f"  • Failed symbols: {', '.join(results['failed'])}")
    
    # Data freshness summary
    if results['freshness_report']:
        max_days_behind = max(r['days_behind'] for r in results['freshness_report'].values())
        avg_days_behind = sum(r['days_behind'] for r in results['freshness_report'].values()) / len(results['freshness_report'])
        
        print(f"\n🔄 DATA FRESHNESS:")
        print(f"  • Most current: {max_days_behind} days behind")
        print(f"  • Average: {avg_days_behind:.1f} days behind")
        
        if max_days_behind == 0:
            print(f"  • Status: ✅ All data is current!")
        elif max_days_behind <= 3:
            print(f"  • Status: 🟡 Data is reasonably fresh")
        else:
            print(f"  • Status: 🔴 Some data may be outdated")
    
    results['summary'] = {
        'total': total_symbols,
        'successful': successful_count,
        'failed': len(results['failed']),
        'max_days_behind': max_days_behind if results['freshness_report'] else None
    }
    
    print("=" * 60)
    return results

def validate_data_currency(symbol, max_days_old=5):
    """
    Check if existing data file is current enough
    
    Parameters:
    - symbol (str): Stock symbol
    - max_days_old (int): Maximum acceptable age in days
    
    Returns:
    - bool: True if data is current enough, False if needs refresh
    """
    try:
        df = pd.read_csv(f'{symbol}_data.csv', index_col=0, parse_dates=True)
        latest_date = df.index[-1].date()
        today = datetime.now().date()
        days_old = (today - latest_date).days
        
        return days_old <= max_days_old
    except:
        return False  # File doesn't exist or can't be read

if __name__ == "__main__":
    # Example usage - download current data for key stocks
    key_stocks = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'SPY']
    
    print("🚀 REAL-TIME STOCK DATA COLLECTOR")
    print(f"📅 Today's date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Download multiple stocks
    results = download_multiple_stocks(key_stocks)
    
    # Show final status
    if results['summary']['successful'] > 0:
        print(f"\n🎉 Ready for forecasting with {results['summary']['successful']} stocks!")
    else:
        print(f"\n❌ No data downloaded successfully. Check your internet connection.")