The Core Problem: 
I need to stay informed about large price moves on US markets, including equities (SPY, QQQ, big tech), USD, US Treasuries, crypto, and gold, and find out what could be the driving factors for these large price changes (e.g. important events, like fed monetory policies, CPI, Trump, AI evolvement, earnings from important companies like NVDA, wars, etc.). Normally, I would search for news and do information filtering based on my understanding and experience, and make proper induction/explanation, but I don't have time to read the news every day and every hour.


The MVP (Minimal Viable Product):

# US Market News Impact Monitor

An MVP web application that automatically monitors and detects large price movements of important tickers in US market (including equities (SPY, QQQ, big tech), USD, US Treasuries, crypto, and gold), fetches, filters, and analyzes financial news to find the driving factors for these price movements. The workflow reads a local background.md file for strategic context, performs the scan, and renders a structured JSON report of its findings on the front-end. 

## Features
1. Automatic price minitoring, news fetching and deep-dive analysis

 - Monitors SPY, QQQ, GLD, BTC via Databento API. Monitoring should be triggered periodically every hour based in New York time. Once a large movement is detected (hourly >0.5% drop or increase), the app will trigger news fetching, news filtering. With these external information plus the internal goal always guided by the background.md, the app performs deep-dive analysis using LLM (on how the news would impact high price movement for these important tickers, For example, SPX -1%, might be due to that fed is expected to postpone the rate cut). 
 - In this feature, the price changes for the tickers, the relevant news (including and ranked by the importance) and deep-dive analysis should all be shown on the UI. 

- **Intelligent News Filtering**: Two-stage filtering (rule-based + LLM scoring) to identify impactful news

2. On-demand US market analysis
- The only differences from the automatic monitoring feature is, no matter how the important tickers' price changes, still detect them, then fetch news, filtering, and generate comprehensive market analysis for the important tickers on demand on how the news might impact the ticker prices, triggered by a single button.



The OKRs:
Objective: Deliver high-quality, relevant strategic alerts.


Key Result 1 (Precision): 100% of the news items flagged with High Importance in the final report must be directly related to the strategic goals defined in background.md.


Key Result 2 (Actionability): The final report must be a clean, structured JSON that is easy for a front-end to parse and display.