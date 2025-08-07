# src/models/model_evaluator.py

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List

class ModelEvaluator:
    """
    Comprehensive model evaluation framework for forecasting performance
    """
    
    def __init__(self):
        self.metrics_history = []
    
    def calculate_metrics(self, actual: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
        """
        Calculate comprehensive forecasting metrics
        
        Args:
            actual: Array of actual values
            predicted: Array of predicted values
            
        Returns:
            Dictionary with various performance metrics
        """
        # Remove any NaN values
        mask = ~(np.isnan(actual) | np.isnan(predicted))
        actual_clean = actual[mask]
        predicted_clean = predicted[mask]
        
        if len(actual_clean) == 0:
            return {"error": "No valid data points for evaluation"}
        
        # Basic regression metrics
        mae = mean_absolute_error(actual_clean, predicted_clean)
        rmse = np.sqrt(mean_squared_error(actual_clean, predicted_clean))
        r2 = r2_score(actual_clean, predicted_clean)
        
        # Mean Absolute Percentage Error
        mape = np.mean(np.abs((actual_clean - predicted_clean) / actual_clean)) * 100
        
        # Directional Accuracy (for time series)
        directional_accuracy = 0
        if len(actual_clean) > 1:
            actual_diff = np.diff(actual_clean)
            predicted_diff = np.diff(predicted_clean)
            directional_accuracy = np.mean(
                (actual_diff > 0) == (predicted_diff > 0)
            ) * 100
        
        # Additional metrics
        mean_actual = np.mean(actual_clean)
        mean_predicted = np.mean(predicted_clean)
        bias = mean_predicted - mean_actual
        
        # Normalized metrics
        rmse_normalized = rmse / mean_actual * 100
        mae_normalized = mae / mean_actual * 100
        
        metrics = {
            'MAE': round(mae, 4),
            'RMSE': round(rmse, 4),
            'R²': round(r2, 4),
            'MAPE': round(mape, 2),
            'Directional_Accuracy': round(directional_accuracy, 2),
            'Bias': round(bias, 4),
            'RMSE_Normalized': round(rmse_normalized, 2),
            'MAE_Normalized': round(mae_normalized, 2),
            'Data_Points': len(actual_clean)
        }
        
        return metrics
    
    def evaluate_forecast_quality(self, metrics: Dict[str, float]) -> str:
        """
        Provide qualitative assessment of forecast quality
        
        Args:
            metrics: Dictionary of calculated metrics
            
        Returns:
            String describing forecast quality
        """
        mape = metrics.get('MAPE', 100)
        directional_acc = metrics.get('Directional_Accuracy', 0)
        r2 = metrics.get('R²', 0)
        
        if mape < 5 and directional_acc > 75 and r2 > 0.7:
            return "🟢 Excellent - High accuracy and strong predictive power"
        elif mape < 10 and directional_acc > 65 and r2 > 0.5:
            return "🟡 Good - Acceptable accuracy for most applications"
        elif mape < 20 and directional_acc > 55:
            return "🟠 Fair - Moderate accuracy, use with caution"
        else:
            return "🔴 Poor - Low accuracy, consider model improvements"
    
    def cross_validate_forecast(self, 
                              data: pd.DataFrame, 
                              forecaster, 
                              n_splits: int = 5,
                              horizon: int = 7) -> Dict[str, List[float]]:
        """
        Perform time series cross-validation
        
        Args:
            data: Historical data DataFrame with 'ds' and 'y' columns
            forecaster: TimeGPT forecaster instance
            n_splits: Number of cross-validation splits
            horizon: Forecast horizon for each split
            
        Returns:
            Dictionary with lists of metrics for each split
        """
        print(f"🔄 Performing {n_splits}-fold time series cross-validation...")
        
        cv_metrics = {
            'MAE': [], 'RMSE': [], 'MAPE': [], 
            'Directional_Accuracy': [], 'R²': []
        }
        
        # Calculate split size
        total_size = len(data)
        test_size = horizon
        min_train_size = 30  # Minimum training size
        
        for i in range(n_splits):
            # Calculate split indices
            split_end = total_size - (n_splits - i - 1) * test_size
            split_start = max(0, split_end - test_size - min_train_size)
            
            if split_start >= split_end - test_size:
                print(f"⚠️  Skipping split {i+1} - insufficient data")
                continue
            
            # Split data
            train_data = data.iloc[split_start:split_end-test_size].copy()
            test_data = data.iloc[split_end-test_size:split_end].copy()
            
            try:
                # Generate forecast
                forecast = forecaster.forecast(train_data, horizon=test_size)
                
                # Calculate metrics
                actual = test_data['y'].values
                predicted = forecast['TimeGPT'].values[:len(actual)]
                
                split_metrics = self.calculate_metrics(actual, predicted)
                
                # Store metrics
                for key in cv_metrics:
                    if key in split_metrics:
                        cv_metrics[key].append(split_metrics[key])
                
                print(f"✅ Split {i+1}/{n_splits} completed - MAPE: {split_metrics.get('MAPE', 0):.2f}%")
                
            except Exception as e:
                print(f"❌ Split {i+1} failed: {str(e)}")
        
        return cv_metrics
    
    def generate_performance_report(self, 
                                  symbol: str,
                                  metrics: Dict[str, float],
                                  cv_metrics: Dict[str, List[float]] = None) -> str:
        """
        Generate comprehensive performance report
        
        Args:
            symbol: Stock symbol
            metrics: Single forecast metrics
            cv_metrics: Cross-validation metrics (optional)
            
        Returns:
            Formatted performance report string
        """
        report = f"\n📊 PERFORMANCE REPORT - {symbol}\n"
        report += "=" * 50 + "\n\n"
        
        # Single forecast metrics
        report += "🎯 Single Forecast Metrics:\n"
        report += f"  • MAE (Mean Absolute Error): ${metrics.get('MAE', 0):.2f}\n"
        report += f"  • RMSE (Root Mean Square Error): ${metrics.get('RMSE', 0):.2f}\n"
        report += f"  • MAPE (Mean Absolute Percentage Error): {metrics.get('MAPE', 0):.2f}%\n"
        report += f"  • R² (Coefficient of Determination): {metrics.get('R²', 0):.3f}\n"
        report += f"  • Directional Accuracy: {metrics.get('Directional_Accuracy', 0):.2f}%\n"
        report += f"  • Bias: ${metrics.get('Bias', 0):.2f}\n\n"
        
        # Quality assessment
        quality = self.evaluate_forecast_quality(metrics)
        report += f"🏆 Overall Quality: {quality}\n\n"
        
        # Cross-validation results
        if cv_metrics and any(cv_metrics.values()):
            report += "🔄 Cross-Validation Results:\n"
            for metric, values in cv_metrics.items():
                if values:
                    mean_val = np.mean(values)
                    std_val = np.std(values)
                    if metric == 'MAPE' or metric == 'Directional_Accuracy':
                        report += f"  • {metric}: {mean_val:.2f}% (±{std_val:.2f}%)\n"
                    else:
                        report += f"  • {metric}: {mean_val:.4f} (±{std_val:.4f})\n"
            report += "\n"
        
        # Recommendations
        report += "💡 Recommendations:\n"
        if metrics.get('MAPE', 100) > 15:
            report += "  • Consider using longer historical data for training\n"
        if metrics.get('Directional_Accuracy', 0) < 60:
            report += "  • Model struggles with direction prediction - review data quality\n"
        if metrics.get('R²', 0) < 0.5:
            report += "  • Low explanatory power - consider additional features\n"
        if metrics.get('MAPE', 100) < 10 and metrics.get('Directional_Accuracy', 0) > 70:
            report += "  • ✅ Model performs well - suitable for decision making\n"
        
        return report
