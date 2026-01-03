# US Market News Impact Monitor

An MVP web application that automatically monitors and detects large price movements of important tickers in US markets (including equities SPY, QQQ, big tech, USD, US Treasuries, crypto, and gold), fetches, filters, and analyzes financial news to find the driving factors for these price movements.

## Project Structure

```
project_news_scanner_v1/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── logger.py              # Custom logging setup
│   ├── main.py                # FastAPI application and routes
│   └── services/
│       ├── __init__.py
│       ├── polygon_client.py      # Polygon.io API client for market data
│       ├── ai_builder_client.py   # AI Builder API client for news & LLM
│       ├── news_filter.py         # Two-stage news filtering service
│       └── monitoring_service.py  # Price monitoring and analysis orchestration
├── requirements.txt          # Python dependencies
├── .gitignore
└── README.md                # This file
```

**Note**: Internal documentation files (`background.md`, `product_definition_brief.md`, `cursor_system_prompt.md`) are excluded from version control via `.gitignore`. Create `background.md` in the project root for strategic context.

## Key Features

### 1. Automatic Price Monitoring & Analysis
- **Monitored Tickers**: Configurable (default: TSLA, can be set to SPY, QQQ, GLD, BTC, or other tickers)
- **Monitoring Frequency**: Every hour (based on New York time)
- **Threshold**: Detects movements >0.5% (hourly change)
- **Workflow**: When large movement detected → fetch news → filter news → deep-dive LLM analysis
- **Market Hours**: Only monitors during US market hours (9:30 AM - 4:00 PM ET, Mon-Fri)

### 2. Intelligent News Filtering
- **Two-Stage Filtering**:
  1. **Rule-Based**: Filters articles based on relevant keywords (market, financial, fed, inflation, etc.)
  2. **LLM Scoring**: Uses AI Builder API to score relevance (0.0-1.0) and rank articles
- **Importance Levels**: High (≥0.8), Medium (≥0.5), Low (<0.5)

### 3. Deep-Dive Analysis
- Uses LLM (supermind-agent-v1) to analyze how news impacts price movements
- Considers strategic context from `background.md`
- Provides:
  - Key driving factors
  - Impact analysis
  - Ranked news articles
  - Future outlook insights

### 4. On-Demand Analysis
- Button-triggered analysis regardless of price movement threshold
- Analyzes all monitored tickers on demand
- Generates comprehensive market analysis

### 5. Web Interface
- Modern, responsive HTML/JS frontend
- Displays:
  - Price changes with visual indicators
  - Ranked news articles (color-coded by importance)
  - Deep-dive analysis results
- Real-time status updates

### 6. Detailed Logging
- Console logging with custom format:
  - `[Agent] Decided to call tool: [tool name]`
  - `[System] Tool Output: '...'`
  - `[Agent] Final Answer: '...'`

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd project_news_scanner_v1
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root and add your API keys:
   ```
   SUPER_MIND_API_KEY=your_supermind_api_key_here
   POLYGON_API_KEY=your_polygon_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here  # Optional: for faster LLM scoring
   USE_OPENAI_FOR_SCORING=true  # Set to "true" to use OpenAI for scoring (faster, default: true)
   OPENAI_MODEL_FOR_SCORING=gpt-5-mini  # OpenAI model to use for scoring (default: gpt-5-mini)
   ```

5. **Create background.md**:
   Create a `background.md` file in the project root with your strategic context. The application reads this file to guide its analysis.

## Running the Application

### Start the FastAPI server:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or using the main module directly:
```bash
python -m app.main
```

### Access the web interface:
Open your browser and navigate to:
```
http://localhost:8000
```

### API Endpoints:
- `GET /` - Main web interface
- `POST /api/analyze` - Trigger on-demand market analysis
- `GET /api/recent` - Get recent analyses
- `GET /api/health` - Health check endpoint

## Key Modules

### `app/config.py`
- Manages application configuration
- Loads environment variables
- Defines monitored tickers, thresholds, and API settings

### `app/services/polygon_client.py`
- Interfaces with Polygon.io API for market data
- Fetches price changes for monitored tickers
- Handles symbol mapping and timezone-aware queries
- Supports both latest price and historical price change queries

### `app/services/ai_builder_client.py`
- Interfaces with AI Builder Student Portal API
- Searches for financial news
- Performs LLM-based analysis and scoring
- Uses OpenAI SDK with custom base URL and model

### `app/services/news_filter.py`
- Implements two-stage news filtering
- Rule-based keyword filtering
- LLM-based relevance scoring and ranking

### `app/services/monitoring_service.py`
- Orchestrates price monitoring workflow
- Checks for significant movements
- Triggers news fetching and analysis
- Manages hourly monitoring loop

### `app/main.py`
- FastAPI application setup
- API endpoints
- Serves HTML/JS frontend
- Background monitoring task management

### `app/logger.py`
- Custom logging utilities
- Agent decision logging
- System output logging
- Agent answer logging

## Configuration

Key configuration options in `app/config.py`:
- `MONITORED_TICKERS`: List of tickers to monitor (default: ["TSLA"], can be configured to ["SPY", "QQQ", "GLD", "BTC"])
- `PRICE_CHANGE_THRESHOLD`: Threshold for significant movement (default: 0.005 = 0.5%)
- `MONITORING_INTERVAL_HOURS`: How often to check (default: 1 hour)
- `TIMEZONE`: Timezone for market hours (default: "America/New_York")
- `USE_OPENAI_FOR_SCORING`: Use OpenAI for LLM scoring instead of AI Builder API (default: true, faster scoring)
- `OPENAI_MODEL_FOR_SCORING`: OpenAI model to use for scoring (default: "gpt-5-mini")

## Technology Stack

- **Backend**: FastAPI (Python web framework)
- **Frontend**: HTML5, JavaScript (vanilla)
- **Market Data**: Polygon.io API
- **News & AI**: AI Builder Student Portal API (OpenAI SDK)
- **LLM Scoring**: OpenAI GPT-5-mini (configurable, faster than AI Builder API)
- **Logging**: Python logging module
- **Environment**: python-dotenv

## Notes

- The application runs background monitoring automatically on startup
- Market hours detection ensures monitoring only during trading hours
- News filtering ensures only relevant articles are analyzed
- All analyses are stored in memory (last 10 analyses)
- The application includes error handling and fallback mechanisms

## Development

To modify the application:
1. Edit the relevant service files in `app/services/`
2. Update configuration in `app/config.py`
3. Modify the frontend HTML/JS in `app/main.py` (root route)
4. Restart the server to apply changes

## Troubleshooting

- **API Errors**: Ensure your `.env` file has valid API keys (especially `POLYGON_API_KEY` and `SUPER_MIND_API_KEY`)
- **No Data**: Check Polygon.io API access and symbol availability. Verify your API key has access to the tickers you're monitoring
- **News Search Issues**: Verify AI Builder API key (`SUPER_MIND_API_KEY`) and base URL
- **Monitoring Not Working**: Check console logs for errors and ensure market hours. Verify `background.md` exists in project root
- **Price Data Issues**: Ensure Polygon.io API key is valid and has access to the market data endpoints

