# Django Financial Backend

This project is a Django-based API for financial data, hosted on AWS EC2. It provides endpoints for fetching stock data, making predictions, running backtests, and generating reports.

## Live API

You can access the live API at: [http://18.117.140.7:8000/](http://18.117.140.7:8000/)

### Available APIs

- **Fetch Stock Data**:  
  `GET /stocks/fetch/<SYMBOL>`  
  Example: [Fetch AAPL Data](http://18.117.140.7:8000/stocks/fetch/AAPL)

- **Predict Stock Price**:  
  `GET /stocks/predict/<SYMBOL>`  
  Example: [Predict AAPL Price](http://18.117.140.7:8000/stocks/predict/AAPL)

- **Backtest Strategy**:  
  `GET /stocks/backtest/<SYMBOL>/?initial_investment=<int>&buy_ma=<int>&sell_ma=<int>`  
  Example: [Backtest AAPL Strategy](http://18.117.140.7:8000/stocks/backtest/AAPL/?initial_investment=1000&buy_ma=50&sell_ma=200)

- **Generate Stock Report**:  
  `GET /stocks/report/<SYMBOL>`  
  Example: [Generate AAPL Report](http://18.117.140.7:8000/stocks/report/AAPL)

## Setting Up Locally

### Prerequisites

Before you start, make sure you have the following installed on your machine:

- **Python 3.9+**: The programming language used to build this application.
- **Docker**: A platform that enables you to build, run, and manage containers.
- **Docker Compose**: A tool for defining and running multi-container Docker applications.

### Clone the Repository

Begin by cloning the repository to your local machine:

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

## Create a .env File

In the root of the project directory, create a file named `.env`. This file will store environment variables that the application needs to run. Add the following variables:

```env
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_NAME=your_database_name
DATABASE_HOST=your_database_host
```

## Important
Make sure to replace the placeholder values with your actual credentials. This configuration is crucial for connecting to external services like the Alpha Vantage API and your database.

## Docker Commands

To build and run your Docker container locally:

1. **Build the Docker image**:

   ```bash
   docker build -t financial-backend .
   ```

2. **Run the container**:

   ```bash
   docker run -p 8000:8000 financial-backend
   ```

After running the above commands, the application should start, and you can access it at [http://localhost:8000](http://localhost:8000).

## Accessing the API Locally

With the application running, you can access the API endpoints. Here’s how to use them:

### Fetch Stock Data

Use the following endpoint to get stock data:

## Accessing the API Locally

With the application running, you can access the API endpoints. Here’s how to use them:

- **Fetch Stock Data**:  
  Use the following endpoint to get stock data:  
  `GET http://localhost:8000/stocks/fetch/<SYMBOL>`

- **Predict Stock Price**:  
  Access the prediction endpoint:  
  `GET http://localhost:8000/stocks/predict/<SYMBOL>`

- **Backtest Strategy**:  
  To run a backtest, use this endpoint:  
  `GET http://localhost:8000/stocks/backtest/<SYMBOL>/?initial_investment=<int>&buy_ma=<int>&sell_ma=<int>`

- **Generate Stock Report**:  
  Generate a report using:  
  `GET http://localhost:8000/stocks/report/<SYMBOL>`

## Conclusion

By following these steps, you should have a fully operational local setup of the Django Financial Backend. If you have any questions about any of the steps or concepts, feel free to ask for clarification. Understanding how to set up and configure your environment is essential for smooth development and deployment.
