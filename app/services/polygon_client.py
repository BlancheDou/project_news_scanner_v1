"""Polygon.io API client for fetching market data."""
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
import pytz
from app.config import Config
from app.logger import setup_logger, log_agent_decision, log_system_output

logger = setup_logger(__name__)

class PolygonClient:
    """Client for interacting with Polygon.io API."""
    
    BASE_URL = "https://api.polygon.io"
    
    def __init__(self):
        """Initialize Polygon client."""
        log_agent_decision(logger, "PolygonClient.__init__")
        self.api_key = Config.POLYGON_API_KEY
        if not self.api_key:
            logger.warning("POLYGON_API_KEY not set in configuration")
        log_system_output(logger, "Polygon client initialized")
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get the latest price for a symbol.
        Uses New York (EDT) timezone.
        
        Args:
            symbol: Ticker symbol (e.g., 'SPY', 'QQQ')
            
        Returns:
            Latest price or None if not found
        """
        log_agent_decision(logger, f"get_latest_price({symbol})")
        try:
            # Map symbol for Polygon API
            polygon_symbol = self._map_symbol(symbol)
            
            # Get previous close price (most reliable for latest price)
            url = f"{self.BASE_URL}/v2/aggs/ticker/{polygon_symbol}/prev"
            params = {
                "adjusted": "true",
                "apiKey": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                log_system_output(logger, f"No price data found for {symbol}: {data.get('status')}")
                return None
            
            result = data.get("results")
            if not result:
                log_system_output(logger, f"No price data found for {symbol}")
                return None
            
            # Previous close endpoint returns a single result object
            latest_price = float(result.get("c", result.get("close", 0)))  # 'c' is close price
            log_system_output(logger, f"Latest price for {symbol}: {latest_price}")
            return latest_price
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")
            log_system_output(logger, f"Error: {str(e)}")
            return None
    
    def get_price_change(self, symbol: str, hours: int = 1) -> Optional[Dict]:
        """
        Get price change over the last N hours.
        Uses New York (EDT) timezone and queries the most recent available data.
        
        Args:
            symbol: Ticker symbol
            hours: Number of hours to look back
            
        Returns:
            Dict with 'current_price', 'previous_price', 'change', 'change_percent'
        """
        log_agent_decision(logger, f"get_price_change({symbol}, {hours}h)")
        try:
            # Use New York timezone
            ny_tz = pytz.timezone(Config.TIMEZONE)
            ny_now = datetime.now(ny_tz)
            
            # Map symbol for Polygon API
            polygon_symbol = self._map_symbol(symbol)
            
            # Calculate date range
            # For hourly data, we'll use aggregates endpoint
            # Get today's date and yesterday's date
            if ny_now.hour < 16 or (ny_now.hour == 16 and ny_now.minute < 30):
                # Before market close, use previous day
                end_date = ny_now - timedelta(days=1)
            else:
                # After market close, use today if it's a trading day
                end_date = ny_now
            
            # Ensure it's a weekday (Mon-Fri)
            while end_date.weekday() >= 5:  # Saturday=5, Sunday=6
                end_date = end_date - timedelta(days=1)
            
            # For hourly data, use Unix timestamps (milliseconds) for precise control
            # Calculate end time (market close: 4:00 PM ET)
            end_time_ny = end_date.replace(hour=16, minute=0, second=0, microsecond=0)
            
            # Calculate start time (N hours before end)
            start_time_ny = end_time_ny - timedelta(hours=hours)
            
            # Convert to Unix timestamps in milliseconds
            end_timestamp_ms = int(end_time_ny.timestamp() * 1000)
            start_timestamp_ms = int(start_time_ny.timestamp() * 1000)
            
            # Use aggregates endpoint for hourly data
            # Polygon aggregates endpoint: /v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}
            # For hourly data: multiplier=1, timespan=hour
            url = f"{self.BASE_URL}/v2/aggs/ticker/{polygon_symbol}/range/1/hour/{start_timestamp_ms}/{end_timestamp_ms}"
            params = {
                "adjusted": "true",
                "sort": "asc",
                "limit": 50000,
                "apiKey": self.api_key
            }
            
            log_system_output(logger, f"Querying {symbol} from {start_time_ny.strftime('%Y-%m-%d %H:%M:%S %Z')} to {end_time_ny.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK" or not data.get("results"):
                log_system_output(logger, f"No data found for {symbol}")
                return None
            
            results = data["results"]
            if len(results) == 0:
                log_system_output(logger, f"No data rows for {symbol}")
                return None
            
            # Get first and last close prices
            first_price = float(results[0]["c"])  # 'c' is close price
            last_price = float(results[-1]["c"])
            
            change = last_price - first_price
            change_percent = (change / first_price) * 100 if first_price > 0 else 0
            
            # Get timestamp from last result
            last_timestamp_ms = results[-1]["t"]  # Unix timestamp in milliseconds
            timestamp = datetime.fromtimestamp(last_timestamp_ms / 1000, tz=ny_tz)
            
            result = {
                'symbol': symbol,
                'current_price': last_price,
                'previous_price': first_price,
                'change': change,
                'change_percent': change_percent,
                'timestamp': timestamp.isoformat()
            }
            
            log_system_output(logger, f"Price change for {symbol}: {change_percent:.2f}%")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching price change for {symbol}: {str(e)}")
            log_system_output(logger, f"Error: {str(e)}")
            return None
    
    def _map_symbol(self, symbol: str) -> str:
        """
        Map symbol to Polygon.io format.
        
        Args:
            symbol: Original symbol
            
        Returns:
            Mapped symbol for Polygon.io
        """
        # Polygon.io uses standard ticker symbols
        # For crypto, prefix with X: (e.g., X:BTCUSD)
        symbol_map = {
            "SPY": "SPY",
            "QQQ": "QQQ",
            "GLD": "GLD",
            "BTC": "X:BTCUSD"  # Crypto prefix for Polygon
        }
        return symbol_map.get(symbol, symbol)

