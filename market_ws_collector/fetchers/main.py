from config import REST_ENDPOINTS
from fetcher import fetch
from parser import parse_binance

# def main():
#     for name, url in REST_ENDPOINTS.items():
#         print(f"Fetching from {name}...")
#         data = fetch(url)
#         if name == "binance" and data:
#             symbols = parse_binance(data)
#             print(f"{name} 合约数量: {len(symbols)}")

if __name__ == "__main__":
    main()
