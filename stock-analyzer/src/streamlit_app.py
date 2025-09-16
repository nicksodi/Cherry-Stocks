import streamlit as st
from technical_analyzer import TechnicalAnalyzer

def set_page_config():
    st.set_page_config(
        page_title="Stock Analysis Dashboard",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for better UI
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stock-header {
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
            background-color: #262730;
        }
        .metric-container {
            background-color: #262730;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .small-button {
            width: auto !important;
            padding: 0 1rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

def get_trend_info(trend: str) -> tuple:
    """Get display function and message for trend signals"""
    if trend in ["STRONG BUY", "BUY"]:
        return st.success, "💹"
    elif trend == "HOLD":
        return st.warning, "⚠️"
    else:
        return st.error, "📉"

def get_rsi_status(value: float) -> tuple:
    """Get RSI status and color"""
    if value < 20:
        return "Extremely Oversold", "danger"
    elif value < 30:
        return "Oversold", "warning"
    elif value < 40:
        return "Slightly Oversold", "info"
    elif value < 60:
        return "Neutral", "secondary"
    elif value < 70:
        return "Slightly Overbought", "info"
    elif value < 80:
        return "Overbought", "warning"
    else:
        return "Extremely Overbought", "danger"

def get_volatility_status(atr_percent: float) -> tuple:
    """Get volatility status and color"""
    if atr_percent < 3:
        return "Low Risk", "success"
    elif atr_percent < 6:
        return "Moderate Risk", "warning"
    else:
        return "High Risk", "danger"

def get_atr_multiple_status(atr_multiple: float) -> tuple:
    """Get ATR multiple status and color"""
    if atr_multiple < 1.0:
        return "Low Extension", "normal"
    elif atr_multiple < 2.0:
        return "Moderate Extension", "normal"
    elif atr_multiple < 3.0:
        return "High Extension", "off"
    else:
        return "Extreme Extension", "inverse"

def render_company_header(details):
    """Render company overview section"""
    company = details['company']
    market_cap = company['market_cap']
    daily_change = company['daily_change']
    daily_change_percent = company['daily_change_percent']
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.metric(
            "Current Price",
            f"${company['price']:.2f}",
            f"{daily_change_percent:+.2f}%",
            delta_color="normal" if daily_change_percent > 0 else "inverse"
        )
    
    with col2:
        st.markdown(f"### {company['name']}")  # Add company name
        st.caption(f"${company['price']:.2f}")
    
    with col3:
        cap_status = ("Large Cap" if market_cap >= 50 else 
                     "Mid Cap" if market_cap >= 1 else 
                     "Small Cap")
        st.metric(
            "Market Cap",
            f"${market_cap:.1f}B",
            cap_status,
            # Remove delta_color to remove arrow
        )
    
    with col4:
        atr = details['risk']['volatility']['atr_percent']
        vol_status = ("Low Risk" if atr < 3 else 
                     "Medium Risk" if atr < 6 else 
                     "High Risk")
        st.metric(
            "Volatility",
            f"{atr:.1f}%",
            vol_status,
            # Remove delta_color to remove arrow
        )

def render_technical_indicators(details):
    """Render technical indicators section"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📈 Trend")
        sma_distance = details['trend']['sma_distance_percent']
        atr_multiple = details['trend']['atr_multiple']
        
        # SMA Distance status
        if sma_distance <= 0:
            delta_color = "inverse"
            status = "Bearish"
        else:
            if atr_multiple < 2.0:  # Combine optimal and good entry
                delta_color = "normal"
                status = "Bullish"
            elif atr_multiple < 3.0:
                delta_color = "off"
                status = "Neutral"
            else:
                delta_color = "inverse"
                status = "Bearish"
        
        st.metric(
            "SMA Distance",
            f"{sma_distance:+.1f}%",
            status,
            delta_color=delta_color
        )
        
        # ATR Multiple status
        atr_status = "Bullish" if atr_multiple < 2 else "Bearish"
        atr_color = "normal" if atr_multiple < 2 else "inverse"
        st.metric(
            "ATR Multiple",
            f"{atr_multiple:.1f}x",
            atr_status,
            delta_color=atr_color
        )
    
    with col2:
        st.markdown("#### 🔄 Momentum")
        rsi_value = details['momentum']['rsi']['value']
        
        # RSI with standardized status
        if rsi_value < 30:
            rsi_status = "Bullish"  # Oversold -> Bullish
            rsi_color = "normal"
        elif rsi_value > 70:
            rsi_status = "Bearish"  # Overbought -> Bearish
            rsi_color = "inverse"
        else:
            rsi_status = "Neutral"
            rsi_color = "off"
        
        st.metric(
            "RSI",
            f"{rsi_value:.1f}",
            rsi_status,
            delta_color=rsi_color
        )
        
        # MACD (already using Bullish/Bearish)
        macd = details['momentum']['macd']
        macd_signal = details['momentum']['macd_signal']
        macd_status = "Bullish" if macd > macd_signal else "Bearish"
        macd_color = "normal" if macd > macd_signal else "inverse"
        
        st.metric(
            "MACD",
            f"{macd:.2f}",
            macd_status,
            delta_color=macd_color
        )
    
    with col3:
        st.markdown("#### 📊 Volume")
        volume_ratio = details['risk']['volume']['ratio']
        volume_status = "Bullish" if volume_ratio > 1.1 else "Bearish"
        volume_color = "normal" if volume_ratio > 1.1 else "inverse"
        
        st.metric(
            "Volume Ratio",
            f"{volume_ratio:.1f}x",
            volume_status,
            delta_color=volume_color
        )

def main():
    set_page_config()
    st.title("📊 Stock Technical Analysis")
    
    # Input section with better layout
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            ticker = st.text_input("Enter Stock Ticker", value="AAPL").upper()
        with col2:
            sma_period = st.number_input("SMA Period", min_value=1, value=150)
        with col3:
            st.markdown("##")  # Spacing
            analyze_button = st.button(
                "Analyze",
                type="primary",
                key="analyze_button",
                help="Click to analyze the stock"
            )
    
    if analyze_button:
        try:
            with st.spinner(f"Analyzing {ticker}..."):
                analyzer = TechnicalAnalyzer(ticker, sma_period)
                details = analyzer.get_analysis_details()
                
                # Company Overview
                st.markdown("---")
                render_company_header(details)
                
                # Technical Analysis
                st.markdown("---")
                render_technical_indicators(details)
                
                # Final Verdict
                st.markdown("---")
                is_buy = analyzer.is_buy()
                
                if is_buy:
                    st.success("### Strong Buy Signal Detected")
                    st.caption("Technical indicators suggest a favorable entry point")
                else:
                    st.warning("### Hold Position")
                    st.caption("Wait for better market conditions")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()