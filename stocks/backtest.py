import pandas as pd
from .models import StockData
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django_ratelimit.decorators import ratelimit


def moving_average(df, window):
    return df['close_price'].rolling(window=window).mean()


@require_GET
@ratelimit(key='ip', rate='5/m', method='ALL', block=True)
def backtest(request, symbol, initial_investment=1000, buy_ma=50, sell_ma=200):
    # Fetch historical stock data
    data = StockData.objects.filter(symbol=symbol).order_by('date').values()
    df = pd.DataFrame(data)

    # Calculate moving averages
    df['buy_ma'] = moving_average(df, buy_ma)
    df['sell_ma'] = moving_average(df, sell_ma)

    # Initialize variables for backtesting
    capital = initial_investment
    position = 0  # Number of shares held
    total_trades = 0
    max_drawdown = 0
    peak = capital

    # Iterate through the DataFrame to simulate trading
    for i in range(len(df)):
        if df['close_price'].iloc[i] < df['buy_ma'].iloc[i] and capital > df['close_price'].iloc[i]:
            # Buy signal
            shares_to_buy = capital // df['close_price'].iloc[i]
            position += shares_to_buy
            capital -= shares_to_buy * df['close_price'].iloc[i]
            total_trades += 1

        elif df['close_price'].iloc[i] > df['sell_ma'].iloc[i] and position > 0:
            # Sell signal
            capital += position * df['close_price'].iloc[i]
            position = 0
            total_trades += 1

        # Calculate drawdown
        current_balance = capital + position * df['close_price'].iloc[i]
        peak = max(peak, current_balance)
        drawdown = (peak - current_balance) / peak
        max_drawdown = max(max_drawdown, drawdown)

    # Final balance
    final_balance = capital + position * df['close_price'].iloc[-1]

    return JsonResponse({
        "final_balance": final_balance,
        "total_trades": total_trades,
        "total_return": (final_balance - initial_investment) / initial_investment * 100,
        "max_drawdown": max_drawdown * 100,  # Convert to percentage
    })
