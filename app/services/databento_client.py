"""Databento API client for fetching market data."""
import databento as db
from datetime import datetime, timedelta
from typing import Dict, Optional
import pytz
from app.config import Config
from app.logger import setup_logger, log_agent_decision, log_system_output

logger = setup_logger(__name__)

class DatabentoClient:
    """Client for interacting with Databento API."""
    
    def __init__(self):
        """Initialize Databento client."""
        log_agent_decision(logger, "DatabentoClient.__init__")
        self.client = db.Historical(Config.DATABENTO_API_KEY)
        log_system_output(logger, "Databento client initialized")
    
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
            # Use New York timezone
            ny_tz = pytz.timezone(Config.TIMEZONE)
            ny_now = datetime.now(ny_tz)
            
            # Get the most recent trading day
            if ny_now.hour < 16:
                end_date = ny_now - timedelta(days=1)
            else:
                end_date = ny_now
            
            # Ensure it's a weekday
            while end_date.weekday() >= 5:
                end_date = end_date - timedelta(days=1)
            
            # Set to market close time (4:00 PM ET)
            end_time_ny = end_date.replace(hour=16, minute=0, second=0, microsecond=0)
            start_time_ny = end_date.replace(hour=9, minute=30, second=0, microsecond=0)
            
            # Convert to UTC
            end_time_utc = end_time_ny.astimezone(pytz.UTC)
            start_time_utc = start_time_ny.astimezone(pytz.UTC)
            
            # Map symbols to Databento format
            db_symbol = self._map_symbol(symbol)
            dataset = self._get_dataset(symbol)
            
            # Fetch the latest trade data
            data_store = self.client.timeseries.get_range(
                dataset=dataset,
                symbols=[db_symbol],
                schema="ohlcv-1h",  # Hourly OHLCV data
                start=start_time_utc,
                end=end_time_utc,
                limit=1
            )
            
            if data_store is None:
                log_system_output(logger, f"No price data found for {symbol}")
                return None
            
            # Convert DBNStore to DataFrame
            try:
                data = data_store.to_df()
            except (AttributeError, Exception) as e:
                logger.warning(f"Could not convert DBNStore to DataFrame for {symbol}: {e}")
                # Try to check if it's already a DataFrame
                if hasattr(data_store, 'iloc'):
                    data = data_store
                else:
                    log_system_output(logger, f"Data store is not convertible for {symbol}")
                    return None
            
            # Check if DataFrame has data
            if data is None:
                log_system_output(logger, f"No price data found for {symbol}")
                return None
            
            # Check if DataFrame is empty using shape
            if hasattr(data, 'shape') and data.shape[0] == 0:
                log_system_output(logger, f"Empty DataFrame for {symbol}")
                return None
            
            # OHLCV schema has 'close' field
            try:
                latest_price = float(data.iloc[-1]['close'])
                log_system_output(logger, f"Latest price for {symbol}: {latest_price}")
                return latest_price
            except (IndexError, KeyError) as e:
                logger.error(f"Error accessing price data for {symbol}: {e}")
                log_system_output(logger, f"Error accessing price data: {e}")
                return None
            
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
            
            # For historical data, we need to query the most recent available trading day
            # Databento historical data typically has data up to the previous trading day
            # So we'll query for yesterday's market data
            
            # Get the most recent trading day (yesterday if today is not available)
            # Market hours: 9:30 AM - 4:00 PM ET
            # We'll query for the last trading day's data
            
            # Calculate end time: end of previous trading day (4:00 PM ET)
            if ny_now.hour < 16 or (ny_now.hour == 16 and ny_now.minute < 30):
                # Before market close, use previous day
                end_date = ny_now - timedelta(days=1)
            else:
                # After market close, use today if it's a trading day
                end_date = ny_now
            
            # Ensure it's a weekday (Mon-Fri)
            while end_date.weekday() >= 5:  # Saturday=5, Sunday=6
                end_date = end_date - timedelta(days=1)
            
            # Set to market close time (4:00 PM ET)
            end_time_ny = end_date.replace(hour=16, minute=0, second=0, microsecond=0)
            
            # Start time: beginning of the same trading day (9:30 AM ET)
            start_time_ny = end_date.replace(hour=9, minute=30, second=0, microsecond=0)
            
            # Convert to UTC for Databento API
            end_time_utc = end_time_ny.astimezone(pytz.UTC)
            start_time_utc = start_time_ny.astimezone(pytz.UTC)
            
            # If we're querying for intraday data (hours < 24), adjust start time
            if hours < 24:
                # For hourly data, go back N hours from market close
                start_time_utc = end_time_utc - timedelta(hours=hours)
            
            db_symbol = self._map_symbol(symbol)
            dataset = self._get_dataset(symbol)
            
            log_system_output(logger, f"Querying {symbol} from {start_time_utc} to {end_time_utc} (NY time: {start_time_ny} to {end_time_ny})")
            
            # Fetch hourly OHLCV data
            data_store = self.client.timeseries.get_range(
                dataset=dataset,
                symbols=[db_symbol],
                schema="ohlcv-1h",
                start=start_time_utc,
                end=end_time_utc,
                limit=100
            )
            
            # Convert DBNStore to DataFrame
            if data_store is None:
                log_system_output(logger, f"No data found for {symbol}")
                return None
            
            # Convert to DataFrame - DBNStore objects have a to_df() method
            try:
                data = data_store.to_df()
            except (AttributeError, Exception) as e:
                logger.warning(f"Could not convert DBNStore to DataFrame for {symbol}: {e}")
                # Try to check if it's already a DataFrame
                if hasattr(data_store, 'iloc'):
                    data = data_store
                else:
                    log_system_output(logger, f"Data store is not convertible for {symbol}")
                    return None
            
            # Check if DataFrame is empty using shape attribute
            if data is None:
                log_system_output(logger, f"No data found for {symbol}")
                return None
            
            if hasattr(data, 'shape'):
                if data.shape[0] == 0:
                    log_system_output(logger, f"Empty DataFrame for {symbol}")
                    return None
            elif hasattr(data, '__len__'):
                try:
                    if len(data) == 0:
                        log_system_output(logger, f"No data rows for {symbol}")
                        return None
                except TypeError:
                    log_system_output(logger, f"Cannot determine data length for {symbol}")
                    return None
            
            # Get first and last close prices
            try:
                first_price = float(data.iloc[0]['close'])
                last_price = float(data.iloc[-1]['close'])
            except (IndexError, KeyError) as e:
                logger.error(f"Error accessing price data for {symbol}: {e}")
                log_system_output(logger, f"Error accessing price data: {e}")
                return None
            
            change = last_price - first_price
            change_percent = (change / first_price) * 100 if first_price > 0 else 0
            
            result = {
                'symbol': symbol,
                'current_price': last_price,
                'previous_price': first_price,
                'change': change,
                'change_percent': change_percent,
                'timestamp': end_time_ny.isoformat()
            }
            
            log_system_output(logger, f"Price change for {symbol}: {change_percent:.2f}%")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching price change for {symbol}: {str(e)}")
            log_system_output(logger, f"Error: {str(e)}")
            # Return None instead of mock data to indicate failure
            return None
    
    def _map_symbol(self, symbol: str) -> str:
        """
        Map symbol to Databento format.
        
        Args:
            symbol: Original symbol
            
        Returns:
            Mapped symbol for Databento
        """
        # For crypto like BTC, might need different handling
        symbol_map = {
            "SPY": "SPY",
            "QQQ": "QQQ",
            "GLD": "GLD",
            "BTC": "BTCUSD"  # Example mapping
        }
        return symbol_map.get(symbol, symbol)
    
    def _get_dataset(self, symbol: str) -> str:
        """
        Get appropriate Databento dataset for symbol.
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            Dataset name
        """
        # Map symbols to appropriate datasets
        # SPY, QQQ are ETFs on NYSE/NASDAQ
        # GLD is on NYSE
        # BTC is crypto
        if symbol == "BTC":
            return "DBEQ.BASIC"  # Crypto dataset
        else:
            return "DBEQ.BASIC"  # US equities dataset

