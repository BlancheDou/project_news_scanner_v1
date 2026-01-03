"""FastAPI main application."""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict
import asyncio
from app.services.monitoring_service import MonitoringService
from app.config import Config
from app.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title="Stock Event AI")

# Global monitoring service instance
monitoring_service = MonitoringService()

# Store recent analyses
recent_analyses: List[Dict] = []

@app.on_event("startup")
async def startup_event():
    """Start background monitoring task."""
    logger.info("Starting application...")
    # Start monitoring in background
    asyncio.create_task(monitoring_service.start_monitoring())

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Stock Event AI</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                padding: 30px;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .controls {
                margin-bottom: 30px;
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 16px;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            button:active {
                transform: translateY(0);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .status {
                padding: 15px;
                background: #f5f5f5;
                border-radius: 6px;
                margin-bottom: 20px;
                font-size: 14px;
                color: #666;
            }
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
                color: #667eea;
            }
            .loading.active {
                display: block;
            }
            .results {
                margin-top: 30px;
            }
            .ticker-card {
                background: #f9f9f9;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                border-left: 4px solid #667eea;
            }
            .ticker-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            .ticker-name {
                font-size: 1.5em;
                font-weight: bold;
                color: #333;
            }
            .price-change {
                font-size: 1.2em;
                font-weight: bold;
            }
            .price-change.positive {
                color: #10b981;
            }
            .price-change.negative {
                color: #ef4444;
            }
            .news-section {
                margin-top: 20px;
            }
            .news-item {
                background: white;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 6px;
                border: 1px solid #e5e5e5;
            }
            .news-item.high {
                border-left: 4px solid #ef4444;
            }
            .news-item.medium {
                border-left: 4px solid #f59e0b;
            }
            .news-item.low {
                border-left: 4px solid #10b981;
            }
            .news-title {
                font-weight: bold;
                color: #333;
                margin-bottom: 5px;
            }
            .news-snippet {
                color: #666;
                font-size: 0.9em;
                margin-bottom: 5px;
            }
            .news-meta {
                font-size: 0.8em;
                color: #999;
            }
            .analysis-section {
                margin-top: 20px;
                padding: 15px;
                background: #f0f4ff;
                border-radius: 6px;
            }
            .analysis-title {
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }
            .analysis-content {
                color: #555;
                line-height: 1.6;
            }
            .error {
                background: #fee;
                color: #c33;
                padding: 15px;
                border-radius: 6px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📈 Stock Event AI</h1>
            <p class="subtitle">Automated monitoring and analysis of significant market movements</p>
            
            <div class="controls">
                <button id="analyzeBtn" type="button">🔍 Run On-Demand Analysis</button>
                <button id="refreshBtn" type="button">🔄 Refresh Recent Analyses</button>
            </div>
            
            <div class="status" id="status">
                Status: Monitoring active. Checking for significant price movements every hour.
            </div>
            
            <div class="loading" id="loading">
                ⏳ Analyzing market movements...
            </div>
            
            <div class="error" id="error" style="display: none;"></div>
            
            <div class="results" id="results"></div>
        </div>
        
        <script>
            async function triggerAnalysis() {
                console.log('triggerAnalysis called');
                const btn = document.getElementById('analyzeBtn');
                const loading = document.getElementById('loading');
                const error = document.getElementById('error');
                const results = document.getElementById('results');
                
                if (!btn || !loading || !error || !results) {
                    console.error('Required elements not found');
                    alert('Error: Page elements not found. Please refresh the page.');
                    return;
                }
                
                btn.disabled = true;
                loading.classList.add('active');
                error.style.display = 'none';
                results.innerHTML = '';
                
                try {
                    console.log('Sending request to /api/analyze');
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    console.log('Response received:', response.status);
                    
                    if (!response.ok) {
                        const errorText = await response.text();
                        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
                    }
                    
                    const data = await response.json();
                    console.log('Data received:', data);
                    displayResults(data);
                } catch (e) {
                    console.error('Error in triggerAnalysis:', e);
                    error.textContent = 'Error: ' + e.message;
                    error.style.display = 'block';
                } finally {
                    btn.disabled = false;
                    loading.classList.remove('active');
                }
            }
            
            // Ensure function is available globally
            window.triggerAnalysis = triggerAnalysis;
            window.loadRecentAnalyses = loadRecentAnalyses;
            
            async function loadRecentAnalyses() {
                try {
                    console.log('Loading recent analyses');
                    const response = await fetch('/api/recent');
                    const data = await response.json();
                    displayResults(data);
                } catch (e) {
                    console.error('Error loading recent analyses:', e);
                }
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            function formatAnalysisText(text) {
                if (!text) return '';
                // Escape HTML first - this preserves newlines as actual newline characters
                let formatted = escapeHtml(text);
                // Convert line breaks to <br> - split on actual newline character (char code 10)
                var newlineChar = String.fromCharCode(10);
                formatted = formatted.split(newlineChar).join('<br>');
                // Convert numbered lists - match digits followed by dot and space
                // Use RegExp constructor to avoid escaping issues in template strings
                var numPattern = '(\\\\d+)\\\\.\\\\s+';
                var numRegex = new RegExp(numPattern, 'g');
                formatted = formatted.replace(numRegex, '<strong>$1.</strong> ');
                // Convert bullet points - match dash or asterisk followed by space
                var bulletPattern = '[-*]\\\\s+';
                var bulletRegex = new RegExp(bulletPattern, 'g');
                formatted = formatted.replace(bulletRegex, '• ');
                return formatted;
            }
            
            function displayResults(data) {
                const results = document.getElementById('results');
                
                if (!data || data.length === 0) {
                    results.innerHTML = '<p>No analyses available yet. Click "Run On-Demand Analysis" to generate one.</p>';
                    return;
                }
                
                let html = '';
                
                data.forEach(item => {
                    const priceChange = item.price_change || {};
                    const changePercent = priceChange.change_percent || 0;
                    const changeClass = changePercent >= 0 ? 'positive' : 'negative';
                    const changeSign = changePercent >= 0 ? '+' : '';
                    
                    html += `
                        <div class="ticker-card">
                            <div class="ticker-header">
                                <div class="ticker-name">${priceChange.symbol || item.ticker}</div>
                                <div class="price-change ${changeClass}">
                                    ${changeSign}${changePercent.toFixed(2)}%
                                </div>
                            </div>
                            
                            <div>
                                <strong>Current Price:</strong> $${(priceChange.current_price || 0).toFixed(2)}<br>
                                <strong>Previous Price:</strong> $${(priceChange.previous_price || 0).toFixed(2)}<br>
                                <strong>Change:</strong> $${(priceChange.change || 0).toFixed(2)}
                            </div>
                            
                            ${item.news_articles && item.news_articles.length > 0 ? `
                                <div class="news-section">
                                    <h3>📰 Relevant News (Ranked by Importance)</h3>
                                    ${(() => {
                                        // Sort news by importance (High > Medium > Low) and relevance score
                                        const sortedNews = [...item.news_articles].sort((a, b) => {
                                            const importanceOrder = { 'High': 3, 'Medium': 2, 'Low': 1, 'Unknown': 0 };
                                            const aImp = importanceOrder[a.importance || 'Unknown'] || 0;
                                            const bImp = importanceOrder[b.importance || 'Unknown'] || 0;
                                            if (aImp !== bImp) return bImp - aImp;
                                            return (b.relevance_score || 0) - (a.relevance_score || 0);
                                        });
                                        // Show high importance articles first, limit to top 10
                                        const highImportanceNews = sortedNews.filter(n => (n.importance || '').toLowerCase() === 'high');
                                        const otherNews = sortedNews.filter(n => (n.importance || '').toLowerCase() !== 'high');
                                        const displayNews = [...highImportanceNews, ...otherNews].slice(0, 10);
                                        
                                        return displayNews.map(news => {
                                            const importance = (news.importance || 'low').toLowerCase();
                                            const hasValidUrl = news.url && !news.url.includes('example.com') && news.url.startsWith('http');
                                            return `
                                                <div class="news-item ${importance}">
                                                    <div class="news-title">${escapeHtml(news.title || 'No title')}</div>
                                                    <div class="news-snippet">${escapeHtml(news.snippet || 'No snippet')}</div>
                                                    <div class="news-meta">
                                                        <span style="font-weight: bold; color: ${importance === 'high' ? '#ef4444' : importance === 'medium' ? '#f59e0b' : '#10b981'}">
                                                            ${news.importance || 'Unknown'} Importance
                                                        </span>
                                                        ${news.relevance_score ? ` | Relevance: ${((news.relevance_score || 0) * 100).toFixed(1)}%` : ''}
                                                        ${news.source ? ` | Source: ${escapeHtml(news.source)}` : ''}
                                                        ${hasValidUrl ? ` | <a href="${escapeHtml(news.url)}" target="_blank" rel="noopener noreferrer" style="color: #667eea; text-decoration: underline;">Read more →</a>` : ''}
                                                    </div>
                                                </div>
                                            `;
                                        }).join('');
                                    })()}
                                </div>
                            ` : ''}
                            
                            ${item.analysis && item.analysis.impact_analysis ? `
                                <div class="analysis-section">
                                    <div class="analysis-title">🔍 Deep-Dive Analysis</div>
                                    ${item.analysis.key_factors && item.analysis.key_factors.length > 0 ? `
                                        <div style="margin-bottom: 15px;">
                                            <strong>Key Factors:</strong>
                                            <ul style="margin: 10px 0; padding-left: 20px;">
                                                ${item.analysis.key_factors.map(factor => `<li>${escapeHtml(factor)}</li>`).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}
                                    <div class="analysis-content">${formatAnalysisText(item.analysis.impact_analysis)}</div>
                                    ${item.analysis.insights && item.analysis.insights !== 'See impact analysis above.' ? `
                                        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ddd;">
                                            <strong>Future Outlook:</strong>
                                            <div style="margin-top: 5px;">${formatAnalysisText(item.analysis.insights)}</div>
                                        </div>
                                    ` : ''}
                                </div>
                            ` : ''}
                        </div>
                    `;
                });
                
                results.innerHTML = html;
            }
            
            // Set up event listeners when DOM is ready
            document.addEventListener('DOMContentLoaded', function() {
                console.log('DOM loaded, setting up event listeners');
                const analyzeBtn = document.getElementById('analyzeBtn');
                const refreshBtn = document.getElementById('refreshBtn');
                
                if (analyzeBtn) {
                    analyzeBtn.addEventListener('click', triggerAnalysis);
                    console.log('Analyze button event listener attached');
                } else {
                    console.error('Analyze button not found');
                }
                
                if (refreshBtn) {
                    refreshBtn.addEventListener('click', loadRecentAnalyses);
                    console.log('Refresh button event listener attached');
                } else {
                    console.error('Refresh button not found');
                }
                
                // Load recent analyses on page load
                loadRecentAnalyses();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/analyze")
async def analyze_market():
    """Trigger on-demand market analysis."""
    logger.info("On-demand analysis requested")
    try:
        # Check all tickers regardless of movement threshold
        movements = await monitoring_service.check_price_movements()
        
        # If no significant movements, still analyze all tickers
        if not movements:
            # Get price changes for all tickers
            from app.services.polygon_client import PolygonClient
            client = PolygonClient()
            movements = []
            for ticker in Config.MONITORED_TICKERS:
                price_change = client.get_price_change(ticker, hours=1)
                if price_change:
                    movements.append(price_change)
        
        # Analyze each movement
        analyses = []
        for movement in movements:
            analysis = await monitoring_service.analyze_movement(movement)
            analyses.append(analysis)
            # Store in recent analyses
            recent_analyses.insert(0, analysis)
            # Keep only last 10
            if len(recent_analyses) > 10:
                recent_analyses.pop()
        
        return JSONResponse(content=analyses)
        
    except Exception as e:
        logger.error(f"Error in on-demand analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recent")
async def get_recent_analyses():
    """Get recent analyses."""
    return JSONResponse(content=recent_analyses)

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "monitored_tickers": Config.MONITORED_TICKERS}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

