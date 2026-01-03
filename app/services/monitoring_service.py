"""Price monitoring service with hourly triggers."""
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
import pytz
from app.config import Config
from app.services.polygon_client import PolygonClient
from app.services.ai_builder_client import AIBuilderClient
from app.services.news_filter import NewsFilter
from app.logger import setup_logger, log_agent_decision, log_system_output

logger = setup_logger(__name__)

class MonitoringService:
    """Service for monitoring price movements and triggering analysis."""
    
    def __init__(self):
        """Initialize monitoring service."""
        self.polygon_client = PolygonClient()
        self.ai_client = AIBuilderClient()
        self.news_filter = NewsFilter(self.ai_client)
        self.background_context = self._load_background_context()
        self._monitoring_task: Optional[asyncio.Task] = None
    
    def _load_background_context(self) -> str:
        """Load strategic context from background.md."""
        import os
        try:
            # Try to find background.md in project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            background_path = os.path.join(project_root, "background.md")
            with open(background_path, "r") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not load background.md: {e}")
            return "Monitor US financial markets for significant price movements."
    
    async def check_price_movements(self) -> List[Dict]:
        """
        Check all monitored tickers for significant price movements.
        
        Returns:
            List of tickers with significant movements (> threshold)
        """
        log_agent_decision(logger, "check_price_movements()")
        significant_movements = []
        
        for ticker in Config.MONITORED_TICKERS:
            price_change = self.polygon_client.get_price_change(ticker, hours=1)
            
            if price_change is None:
                continue
            
            change_percent = abs(price_change['change_percent'])
            
            if change_percent >= (Config.PRICE_CHANGE_THRESHOLD * 100):
                significant_movements.append(price_change)
                log_system_output(logger, f"Significant movement detected: {ticker} {price_change['change_percent']:.2f}%")
        
        return significant_movements
    
    async def analyze_movement(self, price_change: Dict) -> Dict:
        """
        Analyze a significant price movement.
        
        Args:
            price_change: Price change data for a ticker
            
        Returns:
            Complete analysis including news and impact assessment
        """
        log_agent_decision(logger, f"analyze_movement(ticker={price_change['symbol']})")
        ticker = price_change['symbol']
        
        # Step 1: Search for relevant news
        query = f"{ticker} price movement financial news"
        news_articles = self.ai_client.search_news(query, max_results=15)
        log_system_output(logger, f"Found {len(news_articles)} news articles")
        
        # Step 2: Filter news
        filtered_news = self.news_filter.filter_news(news_articles, self.background_context, ticker)
        log_system_output(logger, f"Filtered to {len(filtered_news)} relevant articles")
        
        # Step 3: Deep-dive analysis
        analysis = self.ai_client.analyze_news_impact(ticker, price_change, filtered_news, self.background_context)
        log_system_output(logger, f"Analysis completed for {ticker}")
        
        return {
            "ticker": ticker,
            "price_change": price_change,
            "news_articles": filtered_news,
            "analysis": analysis
        }
    
    def is_market_hours(self) -> bool:
        """Check if current time is during market hours (NY time)."""
        ny_tz = pytz.timezone(Config.TIMEZONE)
        ny_time = datetime.now(ny_tz)
        
        # Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
        if ny_time.weekday() >= 5:  # Saturday or Sunday
            return False
        
        hour = ny_time.hour
        minute = ny_time.minute
        
        # Before 9:30 AM
        if hour < 9 or (hour == 9 and minute < 30):
            return False
        
        # After 4:00 PM
        if hour >= 16:
            return False
        
        return True
    
    async def start_monitoring(self):
        """Start the hourly monitoring loop."""
        log_agent_decision(logger, "start_monitoring()")
        logger.info("Starting price monitoring service...")
        
        while True:
            try:
                # Check if it's market hours
                if self.is_market_hours():
                    movements = await self.check_price_movements()
                    
                    if movements:
                        logger.info(f"Detected {len(movements)} significant price movements")
                        for movement in movements:
                            analysis = await self.analyze_movement(movement)
                            # Store or emit analysis results
                            logger.info(f"Analysis completed for {movement['symbol']}")
                    else:
                        logger.info("No significant price movements detected")
                else:
                    logger.info("Outside market hours, skipping check")
                
                # Wait for next hour
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

