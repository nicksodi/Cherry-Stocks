from technical_analyzer import TechnicalAnalyzer
from colorama import init, Fore, Style

# Initialize colorama
init()

# Define symbols and colors
CHECK_MARK = f"{Fore.GREEN}✓{Style.RESET_ALL}"
CROSS_MARK = f"{Fore.RED}✗{Style.RESET_ALL}"
ARROW_UP = f"{Fore.GREEN}↑{Style.RESET_ALL}"
ARROW_DOWN = f"{Fore.RED}↓{Style.RESET_ALL}"

def get_indicator_status(name, value, thresholds):
    """Returns formatted string with indicator status"""
    if name == "price_vs_sma":
        status = value > thresholds
        symbol = ARROW_UP if status else ARROW_DOWN
        return f"{value:.2f} {symbol}"
    else:
        status = value < thresholds
        symbol = CHECK_MARK if status else CROSS_MARK
        return f"{value:.2f} {symbol}"

def main():
    try:
        ticker = input("Enter company ticker (e.g., AAPL): ").strip().upper()
        sma_period = int(input("Enter SMA period (e.g., 20): ").strip())
        
        print(f"\n{Fore.CYAN}Analyzing {ticker}...{Style.RESET_ALL}")
        analyzer = TechnicalAnalyzer(ticker, sma_period)
        is_buy = analyzer.is_buy()
        details = analyzer.get_analysis_details()
        
        if all(v is not None for v in details.values()):
            print(f"\n{'='*50}")
            print(f"{Fore.YELLOW}Analysis for {ticker}{Style.RESET_ALL}")
            print(f"{'='*50}")
            
            # Price and SMA comparison
            price_vs_sma = details['price'] / details['sma'] - 1  # Percentage difference
            print(f"Current Price: ${details['price']:.2f}")
            print(f"SMA({sma_period}): ${details['sma']:.2f}")
            print(f"Price vs SMA: {get_indicator_status('price_vs_sma', price_vs_sma * 100, 0)}% ")
            
            # Technical Indicators
            print(f"\n{Fore.CYAN}Technical Indicators:{Style.RESET_ALL}")
            print(f"{'─'*50}")
            print(f"RSI: {get_indicator_status('rsi', details['rsi'], 70):<20} [Good: <70]")
            print(f"CCI: {get_indicator_status('cci', details['cci'], 100):<20} [Good: <100]")
            
            # MACD Information
            print(f"\n{Fore.CYAN}MACD Analysis:{Style.RESET_ALL}")
            print(f"{'─'*50}")
            print(f"MACD: {details['macd']:.2f}")
            print(f"Signal: {details['macd_signal']:.2f}")
            print(f"Histogram: {details['macd_hist']:.2f}")
            
            # Final Verdict
            print(f"\n{'='*50}")
            verdict = f"{Fore.GREEN}BUY" if is_buy else f"{Fore.RED}NOT A BUY"
            print(f"Final Verdict: {verdict}{Style.RESET_ALL}")
            print(f"{'='*50}")
            
        else:
            print(f"\n{Fore.RED}Failed to analyze {ticker}. Please verify the ticker symbol and try again.{Style.RESET_ALL}")
        
    except ValueError as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()