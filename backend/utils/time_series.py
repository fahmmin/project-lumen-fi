"""
PROJECT LUMEN - Time Series Forecasting Utilities
Simple forecasting models for spending predictions
"""

from typing import List, Tuple, Dict
import numpy as np
from datetime import datetime, date, timedelta
from backend.utils.logger import logger


class TimeSeriesForecaster:
    """Simple time-series forecasting for spending predictions"""

    @staticmethod
    def moving_average(values: List[float], window: int = 3) -> float:
        """
        Calculate moving average

        Args:
            values: Historical values
            window: Window size

        Returns:
            Moving average
        """
        if not values:
            return 0.0

        if len(values) < window:
            window = len(values)

        recent = values[-window:]
        return np.mean(recent)

    @staticmethod
    def simple_forecast(values: List[float], periods: int = 1) -> Tuple[float, Tuple[float, float]]:
        """
        Simple forecast using moving average with trend

        Args:
            values: Historical values
            periods: Number of periods to forecast (default: 1)

        Returns:
            (predicted_value, (lower_bound, upper_bound))
        """
        if not values or len(values) < 2:
            return 0.0, (0.0, 0.0)

        # Calculate trend
        n = len(values)
        x = np.arange(n)
        y = np.array(values)

        # Simple linear regression for trend
        mean_x = np.mean(x)
        mean_y = np.mean(y)
        slope = np.sum((x - mean_x) * (y - mean_y)) / np.sum((x - mean_x) ** 2)
        intercept = mean_y - slope * mean_x

        # Forecast
        forecast_value = slope * (n + periods - 1) + intercept

        # Calculate confidence interval based on historical variance
        std_dev = np.std(values)
        confidence_margin = 1.96 * std_dev  # 95% confidence

        lower_bound = max(0, forecast_value - confidence_margin)
        upper_bound = forecast_value + confidence_margin

        return float(forecast_value), (float(lower_bound), float(upper_bound))

    @staticmethod
    def detect_seasonality(values: List[float], dates: List[date]) -> Dict:
        """
        Detect seasonal patterns

        Args:
            values: Historical values
            dates: Corresponding dates

        Returns:
            Seasonality info
        """
        if not values or len(values) < 12:
            return {"seasonal": False}

        # Group by month
        monthly_avg = {}
        for val, dt in zip(values, dates):
            month = dt.month
            if month not in monthly_avg:
                monthly_avg[month] = []
            monthly_avg[month].append(val)

        # Calculate average per month
        month_averages = {
            month: np.mean(vals) for month, vals in monthly_avg.items()
        }

        # Check variance across months
        overall_avg = np.mean(values)
        variance = np.var(list(month_averages.values()))

        # If variance is high, likely seasonal
        seasonal = variance > (overall_avg * 0.1)

        return {
            "seasonal": seasonal,
            "monthly_averages": month_averages,
            "variance": float(variance),
            "highest_month": max(month_averages, key=month_averages.get) if seasonal else None
        }

    @staticmethod
    def predict_category_spending(
        historical_data: List[Dict],
        category: str,
        months_ahead: int = 1
    ) -> Dict:
        """
        Predict spending for a specific category

        Args:
            historical_data: List of {date, amount, category} dicts
            category: Category to predict
            months_ahead: Months to forecast

        Returns:
            Prediction with confidence interval
        """
        # Filter by category
        category_data = [
            item for item in historical_data
            if item.get('category') == category
        ]

        if not category_data:
            return {
                "category": category,
                "predicted_amount": 0.0,
                "confidence_interval": (0.0, 0.0),
                "data_points": 0
            }

        # Sort by date
        category_data.sort(key=lambda x: x['date'])

        # Extract values
        amounts = [item['amount'] for item in category_data]

        # Forecast
        predicted, (lower, upper) = TimeSeriesForecaster.simple_forecast(
            amounts,
            periods=months_ahead
        )

        return {
            "category": category,
            "predicted_amount": predicted,
            "confidence_interval": (lower, upper),
            "data_points": len(amounts),
            "historical_average": np.mean(amounts),
            "trend": "increasing" if predicted > np.mean(amounts) else "decreasing"
        }

    @staticmethod
    def calculate_volatility(values: List[float]) -> float:
        """
        Calculate spending volatility (coefficient of variation)

        Args:
            values: Historical spending values

        Returns:
            Volatility score (0-1, higher = more volatile)
        """
        if not values or len(values) < 2:
            return 0.0

        mean = np.mean(values)
        std = np.std(values)

        if mean == 0:
            return 0.0

        # Coefficient of variation
        cv = std / mean

        # Normalize to 0-1 scale (cap at 1.0)
        return min(cv, 1.0)
