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
        """
        keywords = [
            ticker.lower(),
            "market", "financial", "economy", "fed", "federal reserve",
            "inflation", "cpi", "earnings", "stock", "equity",
            "treasury", "bond", "crypto", "bitcoin", "gold"
        ]
        
        filtered = []
        for article in articles:
            title = article.get('title', '').lower()
            snippet = article.get('snippet', '').lower()
            content = f"{title} {snippet}"
            
            # Check if article contains relevant keywords
            if any(keyword in content for keyword in keywords):
                filtered.append(article)
        
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

