import streamlit as st
import pandas as pd
from technical_analyzer import TechnicalAnalyzer

def create_metric_container(label, value, delta=None, suffix=""):
    st.metric(
        label=label,
        value=f"{value:,.2f}{suffix}",
        delta=f"{delta:,.2f}%" if delta is not None else None,
        delta_color="normal"
    )

def main():
    # Configure the page
    st.set_page_config(
        page_title="Stock Analysis Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Title and description
    st.title("Stock Technical Analysis Dashboard")
    st.markdown("---")

    # Input section with improved layout
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        ticker = st.text_input("Enter Stock Ticker", value="AAPL").upper()
    with col2:
        sma_period = st.number_input("SMA Period", min_value=1, value=20)
    with col3:
        st.markdown("##")  # Spacing
        analyze_button = st.button("Analyze Stock", type="primary", use_container_width=True)

    if analyze_button:
        with st.spinner(f"Analyzing {ticker}..."):
            try:
                analyzer = TechnicalAnalyzer(ticker, sma_period)
                is_buy = analyzer.is_buy()
                details = analyzer.get_analysis_details()

                if details:
                    # Price Analysis Section
                    st.subheader("💰 Price Analysis")
                    price_cols = st.columns(4)
                    
                    with price_cols[0]:
                        create_metric_container("Current Price", details['price'], suffix="$")
                    with price_cols[1]:
                        create_metric_container(f"SMA ({sma_period})", details['sma'], suffix="$")
                    with price_cols[2]:
                        price_vs_sma = ((details['price']/details['sma'])-1)*100
                        create_metric_container("Price vs SMA", price_vs_sma, suffix="%")
                    with price_cols[3]:
                        create_metric_container("ATR", details['atr'], details['atr_percent'], suffix="$")

                    # Technical Indicators
                    st.markdown("---")
                    st.subheader("📊 Technical Indicators")
                    
                    tech_cols = st.columns(3)
                    with tech_cols[0]:
                        st.info(f"""
                        **RSI Analysis**
                        - Value: {details['rsi']['value']:.2f}
                        - Signal: {details['rsi']['verdict']}
                        """)
                    
                    with tech_cols[1]:
                        st.info(f"""
                        **CCI Analysis**
                        - Value: {details['cci']['value']:.2f}
                        - Signal: {details['cci']['verdict']}
                        """)
                    
                    with tech_cols[2]:
                        st.info(f"""
                        **MACD Analysis**
                        - MACD: {details['macd']:.2f}
                        - Signal: {details['macd_signal']:.2f}
                        - Histogram: {details['macd_hist']:.2f}
                        """)

                    # Final Verdict
                    st.markdown("---")
                    st.subheader("🎯 Final Analysis")
                    
                    if is_buy:
                        st.success(f"""
                        ### STRONG BUY SIGNAL
                        The technical analysis suggests a buying opportunity for {ticker}.
                        """)
                    else:
                        st.error(f"""
                        ### HOLD/SELL SIGNAL
                        The technical analysis suggests waiting for a better entry point for {ticker}.
                        """)

                else:
                    st.error(f"Failed to analyze {ticker}. Please verify the ticker symbol and try again.")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()