"""
Setup configuration for Stock Forecasting Dashboard
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="stock-forecasting-dashboard",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered stock market forecasting system with web dashboard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/stock-forecasting-dashboard",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/stock-forecasting-dashboard/issues",
        "Documentation": "https://github.com/yourusername/stock-forecasting-dashboard#readme",
        "Source Code": "https://github.com/yourusername/stock-forecasting-dashboard",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "notebooks": [
            "jupyter>=1.0.0",
            "notebook>=6.5.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "stock-dashboard=flask_stock_server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.md"],
    },
    keywords=[
        "stock market",
        "forecasting",
        "machine learning",
        "financial analysis",
        "web dashboard",
        "time series",
        "artificial intelligence",
        "trading",
        "investment",
    ],
)
