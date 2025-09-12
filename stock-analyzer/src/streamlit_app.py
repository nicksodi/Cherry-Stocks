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
            delta_color="normal"
        )
    with col2:
        cap_color = "success" if market_cap >= 50 else "warning" if market_cap >= 1 else "error"
        st.markdown(f"### ${market_cap:.1f}B")
        st.markdown(f'<p style="color: {"green" if market_cap >= 50 else "orange" if market_cap >= 1 else "red"};">{company["market_cap_category"]}</p>', unsafe_allow_html=True)
    with col3:
        atr = details['risk']['volatility']['atr_percent']
        atr_color = "green" if atr < 3 else "orange" if atr < 6 else "red"
        st.markdown(f"### {atr:.1f}%")
        st.markdown(f'<p style="color: {atr_color};">{details["risk"]["volatility"]["level"]}</p>', unsafe_allow_html=True)

def render_technical_indicators(details):
    """Render technical indicators section"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📈 Trend")
        sma_distance = details['trend']['sma_distance_percent']
        sma_color = "normal" if sma_distance < 10 else "off" if sma_distance < 15 else "inverse"
        with st.container():
            st.metric(
                "SMA Distance",
                f"{sma_distance:+.1f}%",
                "Optimal Zone" if sma_distance < 10 else "Caution Zone" if sma_distance < 15 else "Danger Zone",
                delta_color=sma_color
            )
    
    with col2:
        st.markdown("#### 🔄 Momentum")
        rsi_value = details['momentum']['rsi']['value']
        rsi_status = ("Oversold" if rsi_value < 30 else 
                     "Overbought" if rsi_value > 70 else 
                     "Neutral")
        rsi_color = "off" if 30 <= rsi_value <= 70 else "inverse"
        
        with st.container():
            st.metric(
                "RSI",
                f"{rsi_value:.1f}",
                rsi_status,
                delta_color=rsi_color
            )
            
            macd = details['momentum']['macd']
            macd_signal = details['momentum']['macd_signal']
            macd_color = "normal" if macd > macd_signal else "inverse"
            st.metric(
                "MACD",
                f"{macd:.2f}",
                "Bullish" if macd > macd_signal else "Bearish",
                delta_color=macd_color
            )
    
    with col3:
        st.markdown("#### ⚡ Risk Metrics")
        volume_ratio = details['risk']['volume']['ratio']
        volume_status = "Above Average" if volume_ratio > 1.1 else "Below Average"
        volume_color = "normal" if volume_ratio > 1.1 else "inverse"
        
        with st.container():
            st.metric(
                "Volume",
                f"{volume_ratio:.1f}x",
                volume_status,
                delta_color=volume_color
            )
            
            volatility = details['risk']['volatility']['atr_percent']
            vol_status = ("Low Risk" if volatility < 3 else 
                         "Medium Risk" if volatility < 6 else 
                         "High Risk")
            vol_color = "normal" if volatility < 3 else "off" if volatility < 6 else "inverse"
            st.metric(
                "Volatility",
                f"{volatility:.1f}%",
                vol_status,
                delta_color=vol_color
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