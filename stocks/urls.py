from django.urls import path
from .views import fetch_stock_data
from .backtest import backtest
from .ml_model import predict_future_prices
from .reports import generate_report

urlpatterns = [
    path('fetch/<str:symbol>/', fetch_stock_data, name='fetch_stock_data'),
    path('backtest/<str:symbol>/', backtest, name='backtest'),
    path('predict/<str:symbol>/', predict_future_prices, name='predict_stock_prices'),
    path('report/<str:symbol>/', generate_report, name='generate_report'),
]
