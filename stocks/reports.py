import os
import tempfile
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import StockData, StockPrediction  # Adjust based on your project structure

matplotlib.use('Agg')


def calculate_max_drawdown(historical_data):
    # Calculate the running maximum
    historical_data['running_max'] = historical_data['close_price'].cummax()

    # Calculate the drawdown
    historical_data['drawdown'] = (historical_data['running_max'] - historical_data['close_price']) / historical_data[
        'running_max']

    # Get the maximum drawdown
    max_drawdown = historical_data['drawdown'].max()

    return max_drawdown

def generate_performance_metrics(symbol):
    # Fetch historical and predicted data
    historical_data = pd.DataFrame(list(StockData.objects.filter(symbol=symbol).values()))
    predicted_data = pd.DataFrame(list(StockPrediction.objects.filter(symbol=symbol).values()))

    historical_data.sort_index(ascending=False, inplace=True)

    # Calculate metrics (example: total return, max drawdown)
    total_return = (historical_data['close_price'].iloc[-1] - historical_data['close_price'].iloc[0]) / \
                   historical_data['close_price'].iloc[0]
    max_drawdown = calculate_max_drawdown(historical_data)

    # Calculate win rate: percentage of days with positive returns
    historical_data['daily_return'] = historical_data['close_price'].pct_change()
    win_rate = (historical_data['daily_return'] > 0).sum() / historical_data['daily_return'].count()

    # Calculate average trade return
    average_trade_return = historical_data['daily_return'].mean()

    return total_return, max_drawdown, historical_data, predicted_data, win_rate, average_trade_return


def plot_data(historical_data, predicted_data):
    plt.figure(figsize=(12, 6))
    plt.plot(historical_data['date'], historical_data['close_price'], label='Actual Prices', color='blue')
    plt.plot(predicted_data['date'], predicted_data['predicted_price'], label='Predicted Prices', color='orange')
    plt.title('Actual vs Predicted Stock Prices(2Years)')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # Save plot to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file.name)
    plt.close()

    # Filter for the last month
    historical_data['date'] = pd.to_datetime(historical_data['date'], errors='coerce')
    predicted_data['date'] = pd.to_datetime(predicted_data['date'], errors='coerce')

    # Calculate the last month date as a Timestamp
    last_month_date = historical_data['date'].max() - pd.DateOffset(months=1)

    # Filter for the last month
    last_month_data = historical_data[historical_data['date'] >= last_month_date]
    last_month_predictions = predicted_data[predicted_data['date'] >= last_month_date]

    # Create a figure for the last month data
    plt.figure(figsize=(12, 6))
    plt.plot(last_month_data['date'], last_month_data['close_price'], label='Actual Prices', color='blue')
    plt.plot(last_month_predictions['date'], last_month_predictions['predicted_price'], label='Predicted Prices', color='orange')
    plt.title('Actual vs Predicted Stock Prices (Last Month)')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # Save the last month plot to a temporary file
    temp_file_last_month = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file_last_month.name)
    plt.close()

    return temp_file.name, temp_file_last_month.name


def generate_pdf_report(symbol):
    total_return, max_drawdown, historical_data, predicted_data, win_rate, average_trade_return = generate_performance_metrics(symbol)
    plot_img_path1, plot_img_path2 = plot_data(historical_data, predicted_data)

    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    # Title and Meta Information
    c.drawString(100, 750, f"Performance Report for {symbol}")
    c.drawString(100, 730, f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d')}")

    # Executive Summary
    summary_lines = [
        f"Total Return: {total_return:.2%}",
        f"Max Drawdown: {max_drawdown:.2%}",
        f"Win Rate: {win_rate:.2%}",
        f"Average Trade Return: {average_trade_return:.2%}"
    ]

    for i, line in enumerate(summary_lines):
        c.drawString(100, 700 - (i * 20), line)

    # Add the 2-year plot
    c.drawImage(plot_img_path1, 100, 300, width=400, height=300)  # Adjusted y-position
    c.drawString(100, 190, "Figure 1: Actual vs Predicted Stock Prices (2 Years)")

    # Add the last month plot
    c.drawImage(plot_img_path2, 100, 0, width=400, height=300)  # Adjusted y-position
    c.drawString(100, -10, "Figure 2: Actual vs Predicted Stock Prices (Last Month)")  # Adjusted y-position

    c.save()
    pdf_buffer.seek(0)

    # Clean up temporary image files
    os.remove(plot_img_path1)
    os.remove(plot_img_path2)

    return pdf_buffer


@require_GET
def generate_report(request, symbol):
    try:
        # Generate PDF
        pdf_buffer = generate_pdf_report(symbol)

        # Return as downloadable PDF
        response = JsonResponse({
            "message": "Report generated successfully.",
        })
        response['Content-Disposition'] = f'attachment; filename="{symbol}_report.pdf"'
        response['Content-Type'] = 'application/pdf'
        response.content = pdf_buffer.getvalue()
        return response

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
