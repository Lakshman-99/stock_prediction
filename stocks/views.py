# views.py

import os
import numpy as np
import requests
import pandas as pd
import pickle
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django_ratelimit.decorators import ratelimit
from .models import StockData  # Adjust import based on your project


# Helper function to fetch data from API or cache
def get_stock_data(symbol, start_date, end_date):
    # API request URL
    url = (f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}'
           f'&apikey={os.getenv("ALPHA_VANTAGE_API_KEY")}&outputsize=full')

    response = requests.get(url)
    if response.status_code == 429:
        raise Exception("Rate limit exceeded.")
    response.raise_for_status()

    data = response.json().get('Time Series (Daily)', {})
    stock_data = [
        {
            'date': datetime.strptime(date, '%Y-%m-%d').date(),
            'open_price': float(stats['1. open']),
            'close_price': float(stats['4. close']),
            'high_price': float(stats['2. high']),
            'low_price': float(stats['3. low']),
            'volume': int(stats['5. volume']),
        }
        for date, stats in data.items()
        if start_date.date() <= datetime.strptime(date, '%Y-%m-%d').date() <= end_date.date()
    ]

    return stock_data


# Celery task for model training
def train_model_task(symbol, stock_data):
    df = pd.DataFrame(stock_data)

    # Save data to the database
    for _, row in df.iterrows():
        StockData.objects.update_or_create(
            symbol=symbol,
            date=row['date'],
            defaults={
                'open_price': row['open_price'],
                'close_price': row['close_price'],
                'high_price': row['high_price'],
                'low_price': row['low_price'],
                'volume': row['volume'],
            },
        )

    df.set_index('date', inplace=True)

    # Prepare data for training
    predict_days = 30
    df['Prediction'] = df['close_price'].shift(-predict_days)

    X = np.array(df.drop(['Prediction'], axis=1))
    X = X[:-predict_days]  # Size up to the prediction days

    y = np.array(df['Prediction'])
    y = y[:-predict_days]  # Actual prices

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Training the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Save the model to a .pkl file
    model_dir = 'ml_models'
    os.makedirs(model_dir, exist_ok=True)
    file_name = os.path.join(model_dir, f'{symbol}_model.pkl')

    with open(file_name, 'wb') as f:
        pickle.dump(model, f)


# Django view to handle stock data fetching and model training
@require_GET
@ratelimit(key='ip', rate='5/m', method='ALL', block=True)
def fetch_stock_data(request, symbol='AAPL'):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)

        # Fetch stock data from cache or API
        stock_data = get_stock_data(symbol, start_date, end_date)

        if not stock_data:
            return JsonResponse({"error": "No data found for the specified period."}, status=404)

        # Trigger model training
        train_model_task(symbol, stock_data)

        return JsonResponse({"message": f"Data fetched and model trained for {symbol}."})

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Network error: {str(e)}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
