# Stock Analyzer

This project is a command-line interface (CLI) program designed to analyze stock data and determine if a stock is a "BUY" based on technical indicators.

## Project Structure

```
stock-analyzer
├── src
│   ├── main.py               # Entry point of the CLI program
│   ├── technical_analyzer.py  # Contains the TechnicalAnalyzer class
│   └── __init__.py           # Marks the directory as a Python package
├── requirements.txt           # Lists the dependencies required for the project
└── README.md                  # Documentation for the project
```

## How to Run the Program

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd stock-analyzer
   ```

2. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Run the CLI program:**
   ```
   python src/main.py
   ```

## Usage

When prompted, enter the company name/ticker and the Simple Moving Average (SMA) value. The program will analyze the stock based on the following criteria:

- If the stock price is above the SMA.
- If the Relative Strength Index (RSI) and Commodity Channel Index (CCI) are not overbought.

The program will then output whether the stock is a "BUY" or not.

## Future Extensions

This project is designed to be extensible. Future classes can be added for fundamental analysis and other types of stock evaluations.