from technical_analyzer import TechnicalAnalyzer
from colorama import init, Fore, Style

# Initialize colorama
init()

def get_signal_color(signal):
    colors = {
        "STRONG BUY": Fore.GREEN,
        "BUY": Fore.LIGHTGREEN_EX,
        "NEUTRAL": Fore.YELLOW,
        "SELL": Fore.LIGHTRED_EX,
        "STRONG SELL": Fore.RED
    }
    return colors.get(signal, Fore.WHITE)

def main():
    try:
        ticker = input("Enter company ticker (e.g., AAPL): ").strip().upper()
        sma_period = int(input("Enter SMA period (e.g., 20): ").strip())
        
        print(f"\n{Fore.CYAN}Analyzing {ticker}...{Style.RESET_ALL}")
        analyzer = TechnicalAnalyzer(ticker, sma_period)
        is_buy = analyzer.is_buy()
        details = analyzer.get_analysis_details()
        
        if details:
            print(f"\n{'='*60}")
            print(f"{Fore.YELLOW}Technical Analysis for {ticker}{Style.RESET_ALL}")
            print(f"{'='*60}")
            
            # Price and SMA
            print(f"\n{Fore.CYAN}Price Analysis:{Style.RESET_ALL}")
            print(f"Current Price: ${details['price']:.2f}")
            print(f"SMA({sma_period}): ${details['sma']:.2f}")
            print(f"Price vs SMA: {Fore.GREEN if details['price'] > details['sma'] else Fore.RED}" 
                  f"{((details['price']/details['sma'])-1)*100:.2f}%{Style.RESET_ALL}")
            
            # Technical Indicators
            print(f"\n{Fore.CYAN}Technical Indicators:{Style.RESET_ALL}")
            print(f"{'─'*60}")
            
            # RSI
            signal_color = get_signal_color(details['rsi']['verdict'])
            print(f"RSI: {details['rsi']['value']:.2f} "
                  f"({signal_color}{details['rsi']['verdict']}{Style.RESET_ALL})")
            
            # CCI
            signal_color = get_signal_color(details['cci']['verdict'])
            print(f"CCI: {details['cci']['value']:.2f} "
                  f"({signal_color}{details['cci']['verdict']}{Style.RESET_ALL})")
            
            # ATR
            print(f"ATR: ${details['atr']:.2f} ({details['atr_percent']:.2f}% of price)")
            
            # MACD
            print(f"\n{Fore.CYAN}MACD Analysis:{Style.RESET_ALL}")
            print(f"{'─'*60}")
            print(f"MACD: {details['macd']:.2f}")
            print(f"Signal: {details['macd_signal']:.2f}")
            print(f"Histogram: {details['macd_hist']:.2f}")
            
            # Final Verdict
            print(f"\n{'='*60}")
            verdict = f"{Fore.GREEN}BUY" if is_buy else f"{Fore.RED}NOT A BUY"
            print(f"Final Verdict: {verdict}{Style.RESET_ALL}")
            print(f"{'='*60}")
            
        else:
            print(f"\n{Fore.RED}Failed to analyze {ticker}. Please verify the ticker symbol and try again.{Style.RESET_ALL}")
        
    except ValueError as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()