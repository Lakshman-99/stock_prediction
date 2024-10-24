import os
import pickle

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django_ratelimit.decorators import ratelimit
from .models import StockData, StockPrediction  # Adjust imports as needed


@require_GET
@ratelimit(key='ip', rate='5/m', method='ALL', block=True)
def predict_future_prices(request, symbol='AAPL'):
    try:
        # Load historical data from the database
        historical_data = pd.DataFrame(
            list(StockData.objects.filter(symbol=symbol).values())
        )
        historical_data.set_index('date', inplace=True)

        if historical_data.empty:
            return JsonResponse({"error": "No historical data available for this symbol."}, status=404)

        # Load the trained model and scaler from the pickle file
        model_file = f'ml_models/{symbol}_model.pkl'

        if not os.path.exists(model_file):
            return JsonResponse({"error": f"Model for {symbol} not found."}, status=404)

        with open(model_file, 'rb') as f:
            model = pickle.load(f)

        predict_days = 30

        X_predict = np.array(historical_data.drop(['symbol', 'id'], axis=1))[-predict_days:]
        linear_model_predict_prediction = model.predict(X_predict)

        #adjustments
        historical_data = historical_data.sort_index()

        last_actual_price = historical_data['close_price'].iloc[-1]  # This will now give the most recent value
        first_forecast_value = linear_model_predict_prediction[0]

        adjustment = last_actual_price - first_forecast_value
        adjusted_forecast = linear_model_predict_prediction + adjustment

        last_actual_index = historical_data.index[-1]
        forecast_index = pd.date_range(start=last_actual_index + pd.Timedelta(days=1), periods=len(linear_model_predict_prediction))

        # Store predictions in the database
        for date, predicted_price in zip(forecast_index, adjusted_forecast):
            StockPrediction.objects.update_or_create(
                symbol=symbol,
                date=date,
                defaults={'predicted_price': float(predicted_price)},
            )

        return JsonResponse({"message": f"Predictions for {symbol} stored successfully."})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
