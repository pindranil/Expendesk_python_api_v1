# import requests
# from typing import Optional
# from dotenv import load_dotenv
# import os

# load_dotenv()
# API_KEY =  os.getenv("API_KEY")

# def fetch_conversion_rate(from_currency: str, to_currency: str = "INR") -> Optional[float]:
#     try:
#         url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency.upper()}"
#         response = requests.get(url, timeout=5)
#         response.raise_for_status()
#         data = response.json()

#         if data.get("result") != "success":
#             print(f"Exchange rate API returned error: {data.get('error-type')}")
#             return None

#         return data["conversion_rates"].get(to_currency.upper())
#     except Exception as e:
#         print(f"Exchange rate fetch failed for {from_currency}: {e}")
#         return None
import requests
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")  # Required for ExchangeRate-API

def fetch_conversion_rate(from_currency: str, to_currency: str = "INR", date: Optional[str] = None) -> Optional[float]:
    """
    Fetch conversion rate using ExchangeRate-API format.
    If `date` is provided, fetch historical rate (YYYY-MM-DD).
    """
    try:
        base_url = "https://api.exchangerate.host/"
        endpoint = "historical" if date else "latest"

        url = f"{base_url}{endpoint}?"
        url += f"access_key={API_KEY}&source={from_currency.upper()}&currencies={to_currency.upper()}"
        if date:
            url += f"&date={date}"

        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if not data.get("success", True):
            raise ValueError(f"API Error: {data.get('error', {}).get('info', 'Unknown error')}")

        print(f"[DEBUG] Fetched data: {data}")
        return data.get("rates", {}).get(to_currency.upper())
    
    except Exception as e:
        print(f"[ERROR] Failed to fetch exchange rate {from_currency} → {to_currency} on {date or 'latest'}: {e}")
        return None
