import yfinance as yf
import pandas as pd
import numpy as np
import talib as ta
from typing import Tuple, Dict, Any
from enum import Enum

class TrendStrength(Enum):
    STRONG_BUY = "STRONG BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"

class RSIZone(Enum):
    VERY_LOW = "VERY LOW"
    LOW = "LOW"
    NEUTRAL = "NEUTRAL"
    HIGH = "HIGH"
    VERY_HIGH = "VERY HIGH"

class VolatilityLevel(Enum):
    LOW = "LOW VOLATILITY"
    MEDIUM = "MEDIUM VOLATILITY"
    HIGH = "HIGH VOLATILITY"

class MarketCapSize(Enum):
    LARGE = "LARGE CAP"
    MID = "MID CAP"
    SMALL = "SMALL CAP"

class TechnicalAnalyzer:
    def __init__(self, ticker: str, sma_period: int = 150, lookback_days: int = 200):
        self.ticker = ticker
        self.ticker_info = yf.Ticker(ticker).info
        self.sma_period = sma_period
        self.lookback_days = lookback_days
        self.data = self._fetch_data()
        self._calculate_indicators()

    def _fetch_data(self) -> pd.DataFrame:
        """Fetch historical data for analysis"""
        ticker = yf.Ticker(self.ticker)
        df = ticker.history(period=f"{self.lookback_days}d")
        if df.empty:
            raise ValueError(f"No data found for ticker {self.ticker}")
        return df

    def _calculate_indicators(self) -> None:
        """Calculate all technical indicators"""
        # Calculate SMA and its slope
        self.data['SMA'] = ta.SMA(self.data['Close'], timeperiod=self.sma_period)
        self.data['SMA_Slope'] = self.data['SMA'].diff(5)  # 5-day slope

        # Calculate MACD
        self.data['MACD'], self.data['MACD_Signal'], self.data['MACD_Hist'] = ta.MACD(
            self.data['Close'], fastperiod=12, slowperiod=26, signalperiod=9
        )

        # Calculate RSI
        self.data['RSI'] = ta.RSI(self.data['Close'], timeperiod=14)

        # Calculate ATR
        self.data['ATR'] = ta.ATR(self.data['High'], self.data['Low'], self.data['Close'], timeperiod=14)

        # Calculate Volume MA
        self.data['Volume_MA20'] = ta.SMA(self.data['Volume'], timeperiod=20)

    def check_market_cap(self) -> Tuple[MarketCapSize, float]:
        """Analyze market cap size"""
        market_cap = self.ticker_info.get('marketCap', 0)
        cap_billions = market_cap / 1e9
        
        if cap_billions >= 50:
            return MarketCapSize.LARGE, cap_billions
        elif cap_billions >= 1:
            return MarketCapSize.MID, cap_billions
        else:
            return MarketCapSize.SMALL, cap_billions

    def check_sma_verdict(self) -> Tuple[TrendStrength, float, float]:
        """
        Check price position relative to SMA using ATR multiples
        Returns: (trend_strength, percentage_above_sma, atr_multiple)
        """
        current_price = self.data['Close'].iloc[-1]
        current_sma = self.data['SMA'].iloc[-1]
        current_atr = self.data['ATR'].iloc[-1]
        sma_slope = self.data['SMA_Slope'].iloc[-1]
        
        # Calculate traditional percentage
        percentage_above_sma = ((current_price / current_sma) - 1) * 100
        
        # Calculate ATR multiple
        distance_from_sma = abs(current_price - current_sma)
        atr_multiple = distance_from_sma / current_atr
        
        if sma_slope <= 0:
            return TrendStrength.HOLD, percentage_above_sma, atr_multiple
        
        # Determine trend strength based on both percentage and ATR multiple
        if percentage_above_sma > 0:  # Price above SMA
            if atr_multiple < 1.0:  # Very close to SMA
                return TrendStrength.STRONG_BUY, percentage_above_sma, atr_multiple
            elif atr_multiple < 2.0:  # Moderately extended
                return TrendStrength.BUY, percentage_above_sma, atr_multiple
            elif atr_multiple < 3.0:  # Starting to extend
                return TrendStrength.HOLD, percentage_above_sma, atr_multiple
            else:  # Too extended
                return TrendStrength.SELL, percentage_above_sma, atr_multiple
        else:  # Price below SMA
            return TrendStrength.HOLD, percentage_above_sma, atr_multiple

    def check_macd_verdict(self) -> Tuple[bool, Dict[str, float]]:
        """
        Check MACD for bullish signals
        Returns: (verdict, macd_values)
        """
        macd = self.data['MACD'].iloc[-1]
        signal = self.data['MACD_Signal'].iloc[-1]
        hist = self.data['MACD_Hist'].iloc[-1]
        prev_hist = self.data['MACD_Hist'].iloc[-2]
        
        # Bullish crossover or positive divergence
        crossover = prev_hist < 0 and hist > 0
        positive_divergence = macd > signal and macd > 0
        
        verdict = crossover or positive_divergence
        values = {'macd': macd, 'signal': signal, 'histogram': hist}
        
        return verdict, values

    def check_rsi_verdict(self) -> Tuple[RSIZone, float]:
        """
        Categorize RSI into zones
        Returns: (rsi_zone, rsi_value)
        """
        current_rsi = self.data['RSI'].iloc[-1]
        
        if current_rsi < 20:
            return RSIZone.VERY_LOW, current_rsi
        elif 20 <= current_rsi < 40:
            return RSIZone.LOW, current_rsi
        elif 40 <= current_rsi < 60:
            return RSIZone.NEUTRAL, current_rsi
        elif 60 <= current_rsi < 90:
            return RSIZone.HIGH, current_rsi
        else:
            return RSIZone.VERY_HIGH, current_rsi

    def check_volatility(self) -> Tuple[VolatilityLevel, float]:
        """
        Analyze ATR as percentage of price
        Returns: (volatility_level, atr_percentage)
        """
        current_price = self.data['Close'].iloc[-1]
        current_atr = self.data['ATR'].iloc[-1]
        atr_percentage = (current_atr / current_price) * 100
        
        if atr_percentage < 3:
            return VolatilityLevel.LOW, atr_percentage
        elif 6 <= atr_percentage <= 10:
            return VolatilityLevel.MEDIUM, atr_percentage
        else:
            return VolatilityLevel.HIGH, atr_percentage

    def check_volume_verdict(self) -> Tuple[bool, float]:
        """
        Check if volume is above 10% of average
        Returns: (verdict, volume_ratio)
        """
        current_volume = self.data['Volume'].iloc[-1]
        avg_volume = self.data['Volume_MA20'].iloc[-1]
        
        volume_ratio = current_volume / avg_volume
        verdict = volume_ratio > 1.1  # Volume should be 10% above average
        
        return verdict, volume_ratio

    def get_daily_movement(self) -> Tuple[float, float]:
        """Calculate daily price movement and percentage"""
        current_price = self.data['Close'].iloc[-1]
        prev_price = self.data['Close'].iloc[-2]
        change = current_price - prev_price
        change_percent = (change / prev_price) * 100
        return change, change_percent

    def get_analysis_details(self) -> Dict[str, Any]:
        """Get all analysis details for display"""
        current_price = self.data['Close'].iloc[-1]
        market_cap_size, market_cap = self.check_market_cap()
        daily_change, daily_change_percent = self.get_daily_movement()
        
        sma_strength, sma_percentage, atr_multiple = self.check_sma_verdict()
        macd_verdict, macd_values = self.check_macd_verdict()
        rsi_zone, rsi_value = self.check_rsi_verdict()
        volatility_level, atr_percentage = self.check_volatility()
        volume_verdict, volume_ratio = self.check_volume_verdict()
        
        return {
            'company': {
                'name': self.ticker_info.get('longName', self.ticker),
                'market_cap': market_cap,
                'market_cap_category': market_cap_size.value,
                'price': current_price,
                'daily_change': daily_change,
                'daily_change_percent': daily_change_percent
            },
            'trend': {
                'sma': self.data['SMA'].iloc[-1],
                'sma_distance_percent': sma_percentage,
                'sma_strength': sma_strength.value,
                'atr_multiple': atr_multiple
            },
            'momentum': {
                'macd': macd_values['macd'],
                'macd_signal': macd_values['signal'],
                'macd_hist': macd_values['histogram'],
                'macd_verdict': macd_verdict,
                'rsi': {
                    'value': rsi_value,
                    'zone': rsi_zone.value
                }
            },
            'risk': {
                'volatility': {
                    'level': volatility_level.value,
                    'atr_percent': atr_percentage
                },
                'volume': {
                    'ratio': volume_ratio,
                    'verdict': volume_verdict
                }
            }
        }

    def is_buy(self) -> bool:
        """Combine all verdicts into final decision"""
        sma_strength, _, _ = self.check_sma_verdict()  # Add the missing underscore for atr_multiple
        macd_verdict, _ = self.check_macd_verdict()
        rsi_zone, _ = self.check_rsi_verdict()
        volume_verdict, _ = self.check_volume_verdict()
        
        # Must be in STRONG_BUY or BUY zone for SMA
        if sma_strength not in [TrendStrength.STRONG_BUY, TrendStrength.BUY, TrendStrength.HOLD]:
            return False
        
        # RSI should be in LOW or NEUTRAL zone
        rsi_good = rsi_zone in [RSIZone.VERY_LOW, RSIZone.LOW, RSIZone.NEUTRAL]
        
        # Need at least 2 out of 3 confirmations
        confirmations = sum([macd_verdict, rsi_good, volume_verdict])
        
        return confirmations >= 2