"""News filtering service with rule-based and LLM scoring."""
from typing import List, Dict
from app.services.ai_builder_client import AIBuilderClient
from app.logger import setup_logger, log_agent_decision, log_system_output

logger = setup_logger(__name__)

class NewsFilter:
    """Two-stage news filtering (rule-based + LLM scoring)."""
    
    def __init__(self, ai_client: AIBuilderClient):
        """Initialize news filter."""
        self.ai_client = ai_client
    
    def filter_news(self, news_articles: List[Dict], background_context: str, ticker: str) -> List[Dict]:
        """
        Filter news articles using two-stage approach.
        
        Args:
            news_articles: List of news articles
            background_context: Strategic context from background.md
            ticker: Related ticker symbol
            
        Returns:
            Filtered and ranked list of news articles
        """
        log_agent_decision(logger, f"filter_news(ticker={ticker}, articles={len(news_articles)})")
        
        # Stage 1: Rule-based filtering
        filtered = self._rule_based_filter(news_articles, ticker)
        log_system_output(logger, f"Rule-based filter: {len(news_articles)} -> {len(filtered)} articles")
        
        # Stage 2: LLM scoring
        scored = self._llm_score_filter(filtered, background_context, ticker)
        log_system_output(logger, f"LLM scoring completed: {len(scored)} articles ranked")
        
        return scored
    
    def _rule_based_filter(self, articles: List[Dict], ticker: str) -> List[Dict]:
        """
        Rule-based filtering stage.
        
        Filters out articles that don't mention relevant keywords.
        For ticker-specific searches, this filter is lenient since search results are already relevant.
        """
        if not articles:
            return []
        
        # Build ticker variations (e.g., TSLA -> tsla, TSLA, Tesla, TESLA)
        ticker_variations = [
            ticker.lower(),
            ticker.upper(),
            ticker.capitalize(),
            ticker.title()
        ]
        
        # Map ticker to company name if applicable
        ticker_to_company = {
            "TSLA": ["tesla", "tesla inc", "tesla motors", "tesla's", "teslas"],
            "SPY": ["spy", "s&p 500", "sp500", "s&p500"],
            "QQQ": ["qqq", "nasdaq", "nasdaq-100"],
            "GLD": ["gld", "gold", "gold etf"],
            "BTC": ["bitcoin", "btc", "crypto", "cryptocurrency"]
        }
        
        # Add company name variations if available
        if ticker in ticker_to_company:
            ticker_variations.extend(ticker_to_company[ticker])
        
        # General financial keywords (expanded list)
        financial_keywords = [
            "market", "markets", "financial", "finance", "economy", "economic",
            "fed", "federal reserve", "federal", "reserve",
            "inflation", "cpi", "earnings", "stock", "stocks", "equity", "equities", "shares",
            "treasury", "bond", "bonds", "crypto", "bitcoin", "gold",
            "trading", "trader", "traders", "investor", "investors", "investment", "investments",
            "price", "prices", "share price", "share prices", "stock price", "stock prices",
            "revenue", "revenues", "profit", "profits", "loss", "losses", "quarterly", "annual",
            "company", "companies", "corporate", "business", "businesses",
            "shares", "shareholder", "shareholders", "ipo", "dividend", "dividends"
        ]
        
        filtered = []
        for i, article in enumerate(articles):
            # Debug: Log article structure for first few articles
            if i < 3:
                log_system_output(logger, f"Article {i} keys: {list(article.keys())}")
                log_system_output(logger, f"Article {i} title: {article.get('title', 'N/A')[:100]}")
                log_system_output(logger, f"Article {i} snippet: {article.get('snippet', 'N/A')[:100]}")
            
            # Get article content - check multiple possible fields
            title = (article.get('title') or article.get('headline') or '').lower()
            snippet = (article.get('snippet') or article.get('summary') or article.get('description') or '').lower()
            content = f"{title} {snippet}"
            
            # If content is empty, include the article anyway (let LLM decide)
            if not content.strip():
                log_system_output(logger, f"Article {i} has no content, including anyway")
                filtered.append(article)
                continue
            
            # Check if article contains relevant keywords
            ticker_mentioned = any(variation.lower() in content for variation in ticker_variations)
            financial_mentioned = any(keyword in content for keyword in financial_keywords)
            
            if i < 3:
                log_system_output(logger, f"Article {i} - Ticker mentioned: {ticker_mentioned}, Financial mentioned: {financial_mentioned}")
            
            # More lenient: include if ticker OR financial keywords OR if it's a short list (likely already filtered by search)
            # Since we're searching for ticker-specific news, most results should be relevant
            if ticker_mentioned or financial_mentioned or len(articles) <= 5:
                filtered.append(article)
            elif i < 3:
                log_system_output(logger, f"Article {i} filtered out - no matching keywords. Content: {content[:150]}")
        
        return filtered
    
    def _llm_score_filter(self, articles: List[Dict], background_context: str, ticker: str) -> List[Dict]:
        """
        LLM-based scoring and ranking stage.
        
        Scores each article for relevance and ranks them.
        """
        scored_articles = []
        
        for article in articles:
            score = self.ai_client.score_news_relevance(article, background_context, ticker)
            article['relevance_score'] = score
            scored_articles.append(article)
        
        # Sort by relevance score (highest first)
        scored_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Assign importance levels
        for i, article in enumerate(scored_articles):
            if article['relevance_score'] >= 0.8:
                article['importance'] = 'High'
            elif article['relevance_score'] >= 0.5:
                article['importance'] = 'Medium'
            else:
                article['importance'] = 'Low'
        
        return scored_articles

