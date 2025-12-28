"""AI Builder API client for news fetching and LLM analysis."""
import openai
from typing import List, Dict, Optional
from app.config import Config
from app.logger import setup_logger, log_agent_decision, log_system_output, log_agent_answer

logger = setup_logger(__name__)

class AIBuilderClient:
    """Client for interacting with AI Builder Student Portal API."""
    
    def __init__(self):
        """Initialize OpenAI client with AI Builder configuration."""
        log_agent_decision(logger, "AIBuilderClient.__init__")
        self.client = openai.OpenAI(
            api_key=Config.SUPER_MIND_API_KEY,
            base_url=Config.OPENAI_BASE_URL
        )
        log_system_output(logger, "AI Builder client initialized")
    
    def search_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for news articles using the AI Builder API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of news articles with title, url, snippet, etc.
        """
        log_agent_decision(logger, f"search_news(query='{query}')")
        try:
            # Request structured news data with real URLs
            prompt = f"""Search for recent financial news articles about: {query}

Please provide {max_results} recent news articles in the following JSON format:
{{
  "articles": [
    {{
      "title": "Article title",
      "url": "Full URL to the article",
      "snippet": "Brief summary or excerpt",
      "source": "News source name",
      "timestamp": "Publication date/time"
    }}
  ]
}}

Requirements:
- Use real, recent news articles from reputable financial news sources
- Include actual URLs that can be accessed
- Focus on articles published within the last 24-48 hours
- Prioritize articles from sources like: Bloomberg, Reuters, Financial Times, Wall Street Journal, CNBC, MarketWatch, Yahoo Finance, etc.
- Make sure URLs are complete and valid
- Provide meaningful snippets that summarize the article content

Return ONLY valid JSON, no additional text or markdown formatting."""
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial news search assistant. You have access to recent financial news and can provide real article URLs from major financial news sources."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            log_system_output(logger, f"News search response received: {content[:300]}...")
            
            # Parse the response to extract structured news articles
            articles = self._parse_news_response(content, query, max_results)
            log_agent_answer(logger, f"Found {len(articles)} news articles")
            return articles
            
        except Exception as e:
            logger.error(f"Error searching news: {str(e)}")
            log_system_output(logger, f"Error: {str(e)}")
            return []
    
    def analyze_news_impact(self, ticker: str, price_change: Dict, news_articles: List[Dict], background_context: str) -> Dict:
        """
        Perform deep-dive analysis on how news impacts price movements.
        
        Args:
            ticker: Ticker symbol
            price_change: Price change data
            news_articles: List of news articles
            background_context: Strategic context from background.md
            
        Returns:
            Analysis result with insights and impact assessment
        """
        log_agent_decision(logger, f"analyze_news_impact(ticker={ticker})")
        try:
            # Format news articles for the prompt
            news_summary = "\n".join([
                f"- {article.get('title', 'No title')}: {article.get('snippet', 'No snippet')}"
                for article in news_articles[:10]
            ])
            
            prompt = f"""You are a financial market analyst. Analyze how the following news might impact the price movement of {ticker}.

Strategic Context:
{background_context}

Price Movement:
- Symbol: {price_change['symbol']}
- Current Price: ${price_change['current_price']:.2f}
- Previous Price: ${price_change['previous_price']:.2f}
- Change: {price_change['change_percent']:.2f}%

Recent News Articles:
{news_summary}

Provide a comprehensive analysis in the following format:

KEY FACTORS:
List the 3-5 key driving factors from the news that explain this price movement.

IMPACT ANALYSIS:
Provide a detailed, well-written explanation (2-3 paragraphs) of how these factors relate to the price movement. Write in clear, professional language without markdown formatting or code blocks.

FUTURE OUTLOOK:
Provide insights on potential future impact (1-2 paragraphs).

Write your response in plain text format, using clear section headers. Do not use JSON, markdown code blocks, or excessive formatting.
"""
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert financial analyst. Provide detailed, structured analysis of market movements and news impact."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            analysis_content = response.choices[0].message.content
            log_system_output(logger, f"Analysis generated: {analysis_content[:300]}...")
            
            # Parse and structure the analysis
            analysis = self._parse_analysis_response(analysis_content, ticker, price_change, news_articles)
            log_agent_answer(logger, f"Analysis completed for {ticker}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing news impact: {str(e)}")
            log_system_output(logger, f"Error: {str(e)}")
            return {
                "ticker": ticker,
                "error": str(e),
                "key_factors": [],
                "impact_analysis": "Analysis failed due to error.",
                "ranked_news": [],
                "insights": ""
            }
    
    def score_news_relevance(self, news_article: Dict, background_context: str, ticker: str) -> float:
        """
        Score news article relevance using LLM.
        
        Args:
            news_article: News article dict
            background_context: Strategic context
            ticker: Related ticker
            
        Returns:
            Relevance score between 0 and 1
        """
        log_agent_decision(logger, f"score_news_relevance(ticker={ticker})")
        try:
            prompt = f"""Rate the relevance of this news article to our strategic goals and the ticker {ticker}.

Strategic Context:
{background_context}

News Article:
Title: {news_article.get('title', 'No title')}
Content: {news_article.get('snippet', 'No content')}

Rate the relevance on a scale of 0.0 to 1.0, where:
- 1.0 = Highly relevant and directly impacts our strategic goals
- 0.5 = Moderately relevant
- 0.0 = Not relevant

Respond with only a number between 0.0 and 1.0."""
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            score = float(score_text) if score_text.replace('.', '').isdigit() else 0.5
            log_system_output(logger, f"Relevance score: {score}")
            return score
            
        except Exception as e:
            logger.error(f"Error scoring news: {str(e)}")
            return 0.5
    
    def _parse_news_response(self, content: str, query: str, max_results: int = 10) -> List[Dict]:
        """Parse news search response into structured format."""
        import json
        import re
        
        articles = []
        
        try:
            # Try to extract JSON from the response
            # Remove markdown code blocks if present
            json_content = content.strip()
            json_content = re.sub(r'^```json\s*', '', json_content, flags=re.MULTILINE)
            json_content = re.sub(r'^```\s*', '', json_content, flags=re.MULTILINE)
            json_content = re.sub(r'```\s*$', '', json_content, flags=re.MULTILINE)
            json_content = json_content.strip()
            
            # Try to parse as JSON
            try:
                data = json.loads(json_content)
                if isinstance(data, dict) and 'articles' in data:
                    articles = data['articles']
                elif isinstance(data, list):
                    articles = data
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract articles using regex
                logger.warning("Failed to parse JSON, trying regex extraction")
                
                # Look for article patterns in the text
                article_pattern = r'\{"title":\s*"([^"]+)",\s*"url":\s*"([^"]+)",\s*"snippet":\s*"([^"]+)",\s*"source":\s*"([^"]+)",\s*"timestamp":\s*"([^"]+)"\}'
                matches = re.findall(article_pattern, content, re.DOTALL)
                
                for match in matches:
                    articles.append({
                        "title": match[0],
                        "url": match[1],
                        "snippet": match[2],
                        "source": match[3],
                        "timestamp": match[4]
                    })
            
            # Validate and clean articles
            validated_articles = []
            for article in articles[:max_results]:
                if isinstance(article, dict):
                    # Ensure required fields exist
                    title = article.get('title', 'No title')
                    url = article.get('url', '')
                    snippet = article.get('snippet', '')
                    
                    # Skip if URL is invalid or dummy
                    if not url or 'example.com' in url.lower() or not url.startswith('http'):
                        continue
                    
                    validated_articles.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet or title[:200],  # Use title as snippet if snippet is missing
                        "source": article.get('source', 'Financial News'),
                        "timestamp": article.get('timestamp', '')
                    })
            
            # If we got no valid articles, try a fallback approach
            if not validated_articles:
                logger.warning("No valid articles parsed, using fallback")
                # Try to extract URLs and titles from the content
                url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
                urls = re.findall(url_pattern, content)
                
                # Extract titles near URLs
                for i, url in enumerate(urls[:max_results]):
                    # Try to find title before URL
                    title_match = re.search(r'([^.\n]+?)\s*' + re.escape(url), content[:content.find(url)+500])
                    title = title_match.group(1).strip() if title_match else f"News article {i+1} about {query}"
                    
                    validated_articles.append({
                        "title": title[:200],
                        "url": url,
                        "snippet": title[:200],
                        "source": "Financial News",
                        "timestamp": ""
                    })
            
            return validated_articles[:max_results]
            
        except Exception as e:
            logger.error(f"Error parsing news response: {str(e)}")
            log_system_output(logger, f"Error parsing news: {str(e)}")
            # Return empty list on error
            return []
    
    def _parse_analysis_response(self, content: str, ticker: str, price_change: Dict, news_articles: List[Dict]) -> Dict:
        """Parse analysis response into structured format and clean up formatting."""
        import json
        import re
        
        # Clean up the content - remove markdown code blocks, JSON formatting
        cleaned_content = self._clean_markdown_content(content)
        
        # Extract structured data from text sections
        key_factors = []
        impact_analysis = cleaned_content
        insights = ""
        
        # Try to extract sections by headers
        # Look for KEY FACTORS section
        factors_match = re.search(r'KEY FACTORS[:\s]*\n(.*?)(?=\n(?:IMPACT ANALYSIS|FUTURE OUTLOOK|$))', cleaned_content, re.IGNORECASE | re.DOTALL)
        if factors_match:
            factors_text = factors_match.group(1)
            # Extract list items
            factor_items = re.findall(r'(?:^|\n)(?:\d+\.|[-*•])\s*(.+?)(?=\n|$)', factors_text, re.MULTILINE)
            if factor_items:
                key_factors = [item.strip() for item in factor_items[:5]]
            else:
                # Try to split by newlines
                key_factors = [line.strip() for line in factors_text.split('\n') if line.strip()][:5]
        
        # Look for IMPACT ANALYSIS section
        impact_match = re.search(r'IMPACT ANALYSIS[:\s]*\n(.*?)(?=\n(?:FUTURE OUTLOOK|KEY FACTORS|$))', cleaned_content, re.IGNORECASE | re.DOTALL)
        if impact_match:
            impact_analysis = impact_match.group(1).strip()
        else:
            # If no section header, use the whole content as impact analysis
            impact_analysis = cleaned_content
        
        # Look for FUTURE OUTLOOK section
        insights_match = re.search(r'FUTURE OUTLOOK[:\s]*\n(.*?)(?=\n(?:KEY FACTORS|IMPACT ANALYSIS|$))', cleaned_content, re.IGNORECASE | re.DOTALL)
        if insights_match:
            insights = insights_match.group(1).strip()
        
        # Clean up impact_analysis - remove code blocks, extra formatting
        impact_analysis = self._clean_markdown_content(impact_analysis)
        insights = self._clean_markdown_content(insights)
        
        return {
            "ticker": ticker,
            "price_change": price_change,
            "key_factors": key_factors if key_factors else ["Analysis in progress"],
            "impact_analysis": impact_analysis,
            "ranked_news": [
                {
                    **article,
                    "importance": "High" if i < 3 else "Medium" if i < 6 else "Low",
                    "relevance_score": 0.9 - (i * 0.1)
                }
                for i, article in enumerate(news_articles)
            ],
            "insights": insights if insights else "See impact analysis above."
        }
    
    def _clean_markdown_content(self, content: str) -> str:
        """Remove markdown formatting, code blocks, and clean up text."""
        import re
        
        if not content:
            return ""
        
        # Remove code blocks (```json, ```python, etc.)
        content = re.sub(r'```[\w]*\n?', '', content)
        content = re.sub(r'```', '', content)
        
        # Remove JSON structure markers if they're at the start
        content = re.sub(r'^\s*\{[\s\n]*"', '', content)
        content = re.sub(r'"\s*\}\s*$', '', content)
        
        # Remove excessive newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Remove markdown headers
        content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
        
        # Clean up quotes around JSON keys
        content = re.sub(r'"([^"]+)":\s*', r'\1: ', content)
        
        # Remove JSON array/list markers at start of lines
        content = re.sub(r'^\s*[-*]\s*', '', content, flags=re.MULTILINE)
        
        # Trim whitespace
        content = content.strip()
        
        return content

