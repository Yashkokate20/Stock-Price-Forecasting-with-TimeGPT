# setup_dashboard.py - Setup script for the live dashboard

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_api_key():
    """Check if NIXTLA_API_KEY is set"""
    api_key = os.getenv('NIXTLA_API_KEY')
    return api_key is not None and api_key.strip() != ''

def main():
    print("🚀 Setting up Live Stock Predictor Dashboard")
    print("=" * 60)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("❌ Python 3.7+ required. Please upgrade Python.")
        return
    
    # Required packages
    packages = [
        'flask',
        'flask-cors',
        'yfinance',
        'pandas',
        'numpy',
        'plotly'
    ]
    
    print(f"\n📦 Installing required packages...")
    failed_packages = []
    
    for package in packages:
        print(f"  Installing {package}...", end=" ")
        if install_package(package):
            print("✅")
        else:
            print("❌")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n❌ Failed to install: {', '.join(failed_packages)}")
        print("Please install them manually using:")
        for package in failed_packages:
            print(f"  pip install {package}")
        return
    
    print(f"\n✅ All packages installed successfully!")
    
    # Check API key
    print(f"\n🔑 Checking API key...")
    if check_api_key():
        print("✅ NIXTLA_API_KEY is set")
    else:
        print("❌ NIXTLA_API_KEY not found")
        print("Please set your API key:")
        print("  Windows: $env:NIXTLA_API_KEY='your_key_here'")
        print("  Linux/Mac: export NIXTLA_API_KEY='your_key_here'")
    
    # Check files
    print(f"\n📁 Checking files...")
    required_files = [
        'flask_stock_server.py',
        'live_stock_dashboard.html'
    ]
    
    all_files_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} not found")
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ Some required files are missing")
        return
    
    print(f"\n🎉 Setup complete!")
    print(f"\n🚀 To start the live dashboard:")
    print(f"  1. Run: python flask_stock_server.py")
    print(f"  2. Open browser to: http://localhost:5000")
    print(f"  3. Or open: live_stock_dashboard.html")
    print(f"\n💡 Enter any stock symbol to get real-time predictions!")

if __name__ == "__main__":
    main()
