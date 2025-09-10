import yfinance as yf
import pandas as pd
import numpy as np
import time
import talib
from enum import Enum

class SignalStrength(Enum):
    STRONG_BUY = "STRONG BUY"
    BUY = "BUY"
    NEUTRAL = "NEUTRAL"
    SELL = "SELL"
    STRONG_SELL = "STRONG SELL"

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
        self.atr = None

    def analyze_rsi(self, rsi_value):
        if rsi_value < 20:
            return SignalStrength.STRONG_BUY
        elif rsi_value < 30:
            return SignalStrength.BUY
        elif rsi_value > 80:
            return SignalStrength.STRONG_SELL
        elif rsi_value > 70:
            return SignalStrength.SELL
        else:
            return SignalStrength.NEUTRAL

    def analyze_cci(self, cci_value):
        if cci_value < -200:
            return SignalStrength.STRONG_BUY
        elif cci_value < -100:
            return SignalStrength.BUY
        elif cci_value > 200:
            return SignalStrength.STRONG_SELL
        elif cci_value > 100:
            return SignalStrength.SELL
        else:
            return SignalStrength.NEUTRAL

    def fetch_data(self):
        try:
            stock = yf.Ticker(self.ticker)
            required_days = int(self.sma_period * 1.2)

            # Convert trading days to appropriate period string
            if required_days <= 7:
                period = "1mo"
            elif required_days <= 30:
                period = "2mo"
            elif required_days <= 90:
                period = "6mo"
            elif required_days <= 180:
                period = "1y"
            else:
                period = "2y"

            # Fetch data with retry mechanism
            for _ in range(3):
                data = stock.history(period=period, interval="1d", auto_adjust=True)
                if not data.empty:
                    break
                time.sleep(1)

            if data.empty:
                raise ValueError(f"No data found for ticker {self.ticker}")

            min_data_required = max(self.sma_period, 14)
            if len(data) < min_data_required:
                raise ValueError(f"Not enough historical data for {self.ticker}. Got {len(data)} days, need {min_data_required}")

            # Calculate all technical indicators using TA-Lib
            close_prices = data['Close'].values
            high_prices = data['High'].values
            low_prices = data['Low'].values

            # Current price and SMA
            self.stock_price = float(close_prices[-1])
            self.sma = float(talib.SMA(close_prices, timeperiod=self.sma_period)[-1])
            
            # RSI calculation
            self.rsi = float(talib.RSI(close_prices, timeperiod=14)[-1])
            
            # CCI calculation
            self.cci = float(talib.CCI(high_prices, low_prices, close_prices, timeperiod=20)[-1])
            
            # MACD calculation
            self.macd, self.macd_signal, self.macd_hist = talib.MACD(
                close_prices,
                fastperiod=12,
                slowperiod=26,
                signalperiod=9
            )
            
            # ATR calculation (14-period by default)
            self.atr = float(talib.ATR(high_prices, low_prices, close_prices, timeperiod=14)[-1])
            
            # Convert MACD values to float and get latest values
            self.macd = float(self.macd[-1])
            self.macd_signal = float(self.macd_signal[-1])
            self.macd_hist = float(self.macd_hist[-1])

            # Verify calculations
            if any(pd.isna([self.stock_price, self.sma, self.rsi, self.cci, 
                           self.macd, self.macd_signal, self.macd_hist, self.atr])):
                raise ValueError("Invalid calculations detected")

        except Exception as e:
            raise ValueError(f"Error analyzing {self.ticker}: {str(e)}")

    def get_analysis_details(self):
        """Returns the current values used in the analysis with verdicts"""
        if any(x is None for x in [self.stock_price, self.sma, self.rsi, self.cci, self.atr]):
            return None

        rsi_verdict = self.analyze_rsi(self.rsi)
        cci_verdict = self.analyze_cci(self.cci)

        details = {
            "price": round(self.stock_price, 2),
            "sma": round(self.sma, 2),
            "rsi": {
                "value": round(self.rsi, 2),
                "verdict": rsi_verdict.value
            },
            "cci": {
                "value": round(self.cci, 2),
                "verdict": cci_verdict.value
            },
            "macd": round(self.macd, 2),
            "macd_signal": round(self.macd_signal, 2),
            "macd_hist": round(self.macd_hist, 2),
            "atr": round(self.atr, 2),
            "atr_percent": round((self.atr / self.stock_price) * 100, 2)  # ATR as percentage of price
        }
        return details

    def is_buy(self):
        try:
            self.fetch_data()
            if any(x is None for x in [self.stock_price, self.sma, self.rsi, self.cci]):
                return False
                
            rsi_signal = self.analyze_rsi(self.rsi)
            cci_signal = self.analyze_cci(self.cci)
            
            return (
                self.stock_price > self.sma and
                rsi_signal in [SignalStrength.STRONG_BUY, SignalStrength.BUY, SignalStrength.NEUTRAL] and
                cci_signal in [SignalStrength.STRONG_BUY, SignalStrength.BUY, SignalStrength.NEUTRAL]
            )
        except Exception as e:
            print(f"Analysis failed: {str(e)}")
            return False