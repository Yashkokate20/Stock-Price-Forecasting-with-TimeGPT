# flask_stock_server.py - Backend server for integrated dashboard

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class StockAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('NIXTLA_API_KEY')
    
    def get_stock_info(self, symbol):
        """Get basic stock information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'USD')
            }
        except:
            return {
                'name': symbol,
                'sector': 'Unknown',
                'industry': 'Unknown',
                'market_cap': 0,
                'currency': 'USD'
            }
    
    def download_and_analyze(self, symbol, period='6mo'):
        """Download and analyze stock data"""
        try:
            print(f"Analyzing {symbol}...")
            
            # Download data
            ticker = yf.Ticker(symbol.upper())
            data = ticker.history(period=period, interval='1d')
            
            if data.empty:
                return None
            
            # Get stock info
            stock_info = self.get_stock_info(symbol.upper())
            
            # Prepare data
            df = data.reset_index()
            df = df.rename(columns={'Date': 'ds', 'Close': 'y'})
            df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
            
            # Filter to current date
            today = datetime.now().date()
            df = df[df['ds'].dt.date <= today]
            
            # Get recent data for analysis
            recent_data = df.tail(30).copy()
            
            return {
                'data': recent_data,
                'full_data': df,
                'info': stock_info,
                'symbol': symbol.upper()
            }
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {str(e)}")
            return None
    
    def calculate_technical_indicators(self, data):
        """Calculate technical indicators"""
        df = data.copy()
        
        # Price-based indicators
        df['returns'] = df['y'].pct_change()
        df['volatility'] = df['returns'].rolling(window=10).std()
        df['sma_5'] = df['y'].rolling(window=5).mean()
        df['sma_20'] = df['y'].rolling(window=20).mean()
        
        # RSI calculation
        df['rsi'] = self.calculate_rsi(df['y'], 14)
        
        # Trend analysis
        recent_trend = df['returns'].tail(10).mean()
        overall_volatility = df['returns'].std()
        
        return {
            'recent_trend': recent_trend,
            'volatility': overall_volatility,
            'current_price': df['y'].iloc[-1],
            'sma_5': df['sma_5'].iloc[-1],
            'sma_20': df['sma_20'].iloc[-1],
            'rsi': df['rsi'].iloc[-1] if not pd.isna(df['rsi'].iloc[-1]) else 50
        }
    
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_forecast(self, data, indicators, horizon=14):
        """Generate intelligent forecast"""
        try:
            # Base parameters
            current_price = indicators['current_price']
            trend = indicators['recent_trend']
            volatility = indicators['volatility']
            rsi = indicators['rsi']
            
            # Adjust trend based on technical indicators
            if rsi > 70:  # Overbought
                trend_adjustment = -0.3
            elif rsi < 30:  # Oversold
                trend_adjustment = 0.3
            else:
                trend_adjustment = 0
            
            # Moving average signal
            if indicators['sma_5'] > indicators['sma_20']:
                ma_signal = 0.1  # Bullish
            else:
                ma_signal = -0.1  # Bearish
            
            # Combine signals
            adjusted_trend = trend + (trend_adjustment * abs(trend)) + (ma_signal * abs(trend))
            
            # Generate forecast
            forecast_dates = []
            forecast_prices = []
            forecast_hi_80 = []
            forecast_lo_80 = []
            
            last_date = data['ds'].iloc[-1]
            price = current_price
            
            # Set random seed for reproducible results
            np.random.seed(hash(data['ds'].iloc[-1].strftime('%Y%m%d')) % 2**32)
            
            for i in range(horizon):
                # Next business day
                last_date += timedelta(days=1)
                while last_date.weekday() >= 5:  # Skip weekends
                    last_date += timedelta(days=1)
                
                # Price evolution with mean reversion
                daily_return = np.random.normal(adjusted_trend, volatility)
                
                # Add mean reversion
                if i > 3:
                    mean_reversion = (indicators['sma_20'] - price) * 0.05
                    daily_return += mean_reversion / price
                
                # Apply return
                price *= (1 + daily_return)
                
                # Calculate confidence intervals
                cumulative_vol = volatility * np.sqrt(i + 1)
                price_std = price * cumulative_vol
                
                forecast_dates.append(last_date.strftime('%Y-%m-%d'))
                forecast_prices.append(price)
                forecast_hi_80.append(price + 1.28 * price_std)
                forecast_lo_80.append(price - 1.28 * price_std)
            
            return {
                'dates': forecast_dates,
                'prices': forecast_prices,
                'upper_band': forecast_hi_80,
                'lower_band': forecast_lo_80,
                'target_price': forecast_prices[-1]
            }
            
        except Exception as e:
            print(f"Forecast generation failed: {str(e)}")
            return None

analyzer = StockAnalyzer()

@app.route('/')
def index():
    """Serve the integrated dashboard"""
    with open('integrated_stock_dashboard.html', 'r') as f:
        return f.read()

@app.route('/analyze/<symbol>')
def analyze_stock(symbol):
    """Analyze a stock and return results"""
    try:
        # Download and analyze stock data
        stock_data = analyzer.download_and_analyze(symbol)
        if not stock_data:
            return jsonify({'error': f'Could not find data for {symbol}'}), 404
        
        # Calculate technical indicators
        indicators = analyzer.calculate_technical_indicators(stock_data['data'])
        
        # Generate forecast
        forecast = analyzer.generate_forecast(stock_data['data'], indicators, 14)
        if not forecast:
            return jsonify({'error': 'Failed to generate forecast'}), 500
        
        # Prepare historical data for chart
        historical_data = stock_data['data'].tail(30)
        historical_dates = [d.strftime('%Y-%m-%d') for d in historical_data['ds']]
        historical_prices = historical_data['y'].tolist()
        
        # Calculate price change
        current_price = indicators['current_price']
        target_price = forecast['target_price']
        price_change = ((target_price - current_price) / current_price) * 100
        
        # Determine trend signal
        if indicators['rsi'] > 70:
            rsi_signal = 'Overbought'
        elif indicators['rsi'] < 30:
            rsi_signal = 'Oversold'
        else:
            rsi_signal = 'Neutral'
        
        trend_direction = 'Bullish' if indicators['sma_5'] > indicators['sma_20'] else 'Bearish'
        
        result = {
            'symbol': symbol.upper(),
            'name': stock_data['info']['name'],
            'sector': stock_data['info']['sector'],
            'current_price': round(current_price, 2),
            'target_price': round(target_price, 2),
            'price_change_percent': round(price_change, 1),
            'rsi': round(indicators['rsi'], 1),
            'rsi_signal': rsi_signal,
            'trend': trend_direction,
            'volatility': round(indicators['volatility'] * 100, 1),
            'historical': {
                'dates': historical_dates,
                'prices': [round(p, 2) for p in historical_prices]
            },
            'forecast': {
                'dates': forecast['dates'],
                'prices': [round(p, 2) for p in forecast['prices']],
                'upper_band': [round(p, 2) for p in forecast['upper_band']],
                'lower_band': [round(p, 2) for p in forecast['lower_band']]
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 Starting Integrated Stock Predictor Server...")
    print("📅 Server Date:", datetime.now().strftime('%A, %B %d, %Y'))
    print("🌐 Open your browser to: http://localhost:5000")
    print("💡 Enter any stock symbol to get real-time predictions!")
    print("-" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
