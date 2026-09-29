from typing import Dict, Any
import requests

def convert_currency(amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
    """Convert an amount from one currency to another using live real-time exchange rates.

    Args:
        amount: The monetary amount to convert (e.g., 100.0).
        from_currency: Three-letter ISO currency code to convert from (e.g. 'USD', 'EUR', 'GBP').
        to_currency: Three-letter ISO currency code to convert to (e.g. 'JPY', 'EUR', 'CAD').

    Returns:
        A dictionary containing the conversion details, rate, and converted amount.
    """
    from_curr = from_currency.strip().upper()
    to_curr = to_currency.strip().upper()
    
    url = f"https://open.er-api.com/v6/latest/{from_curr}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        rates = data.get("rates", {})
        if to_curr not in rates:
            return {"error": f"Currency code '{to_curr}' not supported."}
        
        rate = rates[to_curr]
        converted = amount * rate
        return {
            "amount": amount,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "exchange_rate": rate,
            "converted_amount": round(converted, 2),
        }
    except Exception as e:
        return {"error": f"Failed to fetch exchange rates: {str(e)}"}
