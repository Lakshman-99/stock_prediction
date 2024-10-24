from django.test import TestCase
from .models import StockData


class BacktestTests(TestCase):
    def setUp(self):
        # Set up test data
        StockData.objects.create(symbol='AAPL', date='2023-01-01', open_price=150, close_price=148, high_price=155, low_price=145, volume=10000)
        StockData.objects.create(symbol='AAPL', date='2023-01-02', open_price=148, close_price=151, high_price=152, low_price=147, volume=15000)
        # Add more test data as needed

    def test_backtest(self):
        response = self.client.get('/stocks/backtest/AAPL/', {'initial_investment': 1000, 'buy_ma': 50, 'sell_ma': 200})
        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        print(response_data)

        # Assert that the response contains expected keys
        self.assertIn('final_balance', response_data)
        self.assertIn('total_trades', response_data)
        self.assertIn('total_return', response_data)
        self.assertIn('max_drawdown', response_data)

        # Check specific expected outcomes (these will depend on your logic)
        self.assertGreaterEqual(response_data['final_balance'], 0)
        self.assertIsInstance(response_data['total_trades'], int)
        self.assertIsInstance(response_data['total_return'], float)
        self.assertIsInstance(response_data['max_drawdown'], int)
