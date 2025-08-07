# Contributing to Stock Forecasting Dashboard

First off, thank you for considering contributing to this project! It's people like you that make this project great.

## 🤝 How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to see if the problem has already been reported. When you are creating a bug report, please include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed and what behavior you expected
- Include screenshots if applicable
- Include your environment details (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- Use a clear and descriptive title
- Provide a step-by-step description of the suggested enhancement
- Provide specific examples to demonstrate the steps
- Describe the current behavior and explain which behavior you expected
- Explain why this enhancement would be useful

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## 🛠️ Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Setting Up Development Environment

1. **Clone your fork of the repository**
   ```bash
   git clone https://github.com/yourusername/stock-forecasting-dashboard.git
   cd stock-forecasting-dashboard
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Set up pre-commit hooks (optional but recommended)**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

5. **Set up environment variables**
   ```bash
   export NIXTLA_API_KEY="your_api_key_here"
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_forecasting.py
```

### Code Style

This project follows PEP 8 style guidelines. We use the following tools:

- **Black** for code formatting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

## 📝 Coding Standards

### Python Code Style

- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions small and focused
- Use meaningful variable names

### Documentation

- Update README.md if you change functionality
- Add docstrings to new functions and classes
- Update type hints
- Add examples for new features

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:
```
Add real-time data validation feature

- Implement data freshness checking
- Add error handling for missing data
- Update tests for new validation logic

Fixes #123
```

## 🧪 Testing Guidelines

### Writing Tests

- Write tests for all new features
- Ensure existing tests pass
- Aim for high test coverage
- Use descriptive test names
- Test both happy path and error cases

### Test Structure

```python
def test_function_name_should_do_something():
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_result
```

## 📚 Documentation

### Code Documentation

- All public functions should have docstrings
- Use Google-style docstrings
- Include type hints
- Provide examples in docstrings when helpful

Example:
```python
def calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """Calculate Relative Strength Index (RSI).
    
    Args:
        prices: Series of stock prices
        window: Period for RSI calculation (default: 14)
        
    Returns:
        Series of RSI values (0-100)
        
    Example:
        >>> prices = pd.Series([100, 102, 98, 105, 103])
        >>> rsi = calculate_rsi(prices, window=4)
        >>> print(rsi.iloc[-1])
        65.4
    """
```

## 🏷️ Issue Labels

We use the following labels to categorize issues:

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `question` - Further information is requested

## 🎯 Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- **Model improvements**: Better forecasting algorithms
- **Performance optimization**: Faster data processing
- **Error handling**: More robust error management
- **Testing**: Increase test coverage

### Medium Priority
- **Documentation**: Improve README, add tutorials
- **Visualization**: Better charts and dashboards
- **API improvements**: Cleaner interfaces
- **Configuration**: Better configuration management

### Nice to Have
- **Mobile responsiveness**: Better mobile UI
- **Internationalization**: Multi-language support
- **Deployment**: Docker, cloud deployment guides
- **Monitoring**: Application performance monitoring

## 💡 Getting Help

If you need help, you can:

- Check existing issues and discussions
- Create a new issue with the `question` label
- Reach out to maintainers directly

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributor graphs

---

**Thank you for contributing to make this project better!** 🚀

*This document is adapted from the open-source contribution guidelines and best practices.*
