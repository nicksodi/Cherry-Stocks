import yfinance as yf
import pandas as pd
import numpy as np
import time
import talib  # Add this import at the top


class TechnicalAnalyzer:
    def __init__(self, ticker, sma_period):
        self.ticker = ticker
        self.sma_period = sma_period
        self.stock_price = None
        self.sma = None
        self.rsi = None
        self.cci = None
        self.macd = None
        self.macd_signal = None
        self.macd_hist = None

    def calculate_macd(self, data):
        """Calculate MACD using TA-Lib"""
        try:
            self.macd, self.macd_signal, self.macd_hist = talib.MACD(
                data['Close'].values,
                fastperiod=12,
                slowperiod=26,
                signalperiod=9
            )
            # Get the latest values
            return {
                'macd': self.macd[-1],
                'signal': self.macd_signal[-1],
                'hist': self.macd_hist[-1]
            }
        except Exception as e:
            raise ValueError(f"MACD calculation failed: {str(e)}")

    def fetch_data(self):
        try:
            # Create a Ticker object
            stock = yf.Ticker(self.ticker)

            # Calculate required period
            # Add 20% buffer for weekends/holidays and to ensure enough data for calculations
            required_days = int(self.sma_period * 1.2)

            # Convert trading days to appropriate period string
            if required_days <= 7:
                period = "1mo"  # Minimum period
            elif required_days <= 30:
                period = "2mo"
            elif required_days <= 90:
                period = "6mo"
            elif required_days <= 180:
                period = "1y"
            else:
                period = "2y"

            # Fetch data with retry mechanism
            for _ in range(3):  # Try up to 3 times
                data = stock.history(
                    period=period,
                    interval="1d",
                    auto_adjust=True
                )

                if not data.empty:
                    break

                time.sleep(1)  # Wait 1 second before retrying

            if data.empty:
                raise ValueError(f"No data found for ticker {self.ticker}")

            # Ensure we have enough data
            min_data_required = max(self.sma_period, 14)  # SMA, RSI periods
            if len(data) < min_data_required:
                raise ValueError(f"Not enough historical data for {self.ticker}. Got {len(data)} days, need {min_data_required}")

            # Take only the required number of rows
            data = data.tail(min_data_required)

            # Calculate metrics
            self.stock_price = float(data['Close'].iloc[-1])
            self.sma = float(data['Close'].rolling(window=self.sma_period).mean().iloc[-1])
            self.rsi = float(self.calculate_rsi(data['Close']))
            self.cci = float(self.calculate_cci(data))

            # Add MACD calculation after other metrics
            macd_values = self.calculate_macd(data)

            # Update verification to include MACD
            if any(pd.isna([self.stock_price, self.sma, self.rsi, self.cci,
                           self.macd, self.macd_signal, self.macd_hist])):
                raise ValueError("Invalid calculations detected")

        except Exception as e:
            raise ValueError(f"Error analyzing {self.ticker}: {str(e)}")

    def calculate_rsi(self, series, period=14):
        try:
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rs = rs.replace([np.inf, -np.inf], np.nan)
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except Exception as e:
            raise ValueError(f"RSI calculation failed: {str(e)}")

    def calculate_cci(self, data, period=20):
        try:
            tp = (data['High'] + data['Low'] + data['Close']) / 3
            sma = tp.rolling(window=period).mean()
            mad = tp.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean())
            cci = (tp - sma) / (0.015 * mad)
            return cci.iloc[-1]
        except Exception as e:
            raise ValueError(f"CCI calculation failed: {str(e)}")

    def is_buy(self):
        try:
            self.fetch_data()
            if any(x is None for x in [self.stock_price, self.sma, self.rsi, self.cci]):
                return False
            return (
                self.stock_price > self.sma
                and self.rsi < 70
                and self.cci < 100
            )
        except Exception as e:
            print(f"Analysis failed: {str(e)}")
            return False

    def get_analysis_details(self):
        """Returns the current values used in the analysis"""
        details = {
            "price": round(self.stock_price, 2) if self.stock_price is not None else None,
            "sma": round(self.sma, 2) if self.sma is not None else None,
            "rsi": round(self.rsi, 2) if self.rsi is not None else None,
            "cci": round(self.cci, 2) if self.cci is not None else None,
            "macd": round(self.macd[-1], 2) if self.macd is not None else None,
            "macd_signal": round(self.macd_signal[-1], 2) if self.macd_signal is not None else None,
            "macd_hist": round(self.macd_hist[-1], 2) if self.macd_hist is not None else None
        }
        return details