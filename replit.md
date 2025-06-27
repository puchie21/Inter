# AI Binary Trading Signal Generator

## Overview

This is a precision AI-powered binary options trading signal generator built with Streamlit. The application specializes in generating highly accurate, time-sensitive trading signals for binary options with optimal entry timing. It combines advanced technical analysis with market session detection and momentum analysis to provide professional-grade trading signals.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application
- **Deployment**: Autoscale deployment on Replit
- **Theme**: Dark theme with custom colors (green primary, dark backgrounds)
- **Layout**: Wide layout with expandable sidebar for configuration
- **Port**: Runs on port 5000

### Backend Architecture
- **Language**: Python 3.11
- **Architecture Pattern**: Modular service-oriented design
- **Core Services**:
  - Trading Engine: Main data processing and signal generation
  - Signal Manager: Signal history management and rate limiting
  - Technical Indicators: Mathematical calculations for trading indicators
  - News Analyzer: Sentiment analysis from forex-related news

### Key Components

1. **Trading Engine (`trading_engine.py`)**
   - Fetches real-time market data using yfinance
   - Implements caching mechanism (60-second timeout)
   - Integrates technical indicators with news sentiment
   - Supports multiple timeframes and currency pairs

2. **Signal Manager (`signal_manager.py`)**
   - Manages trading signal history with JSON file persistence
   - Implements rate limiting (max 3 signals per hour)
   - Handles signal serialization and deserialization

3. **Technical Indicators (`technical_indicators.py`)**
   - Calculates SMA, EMA, RSI, and MACD indicators
   - Built with pandas for efficient data processing
   - Error handling for invalid data scenarios

4. **News Analyzer (`news_analyzer.py`)**
   - Integrates with News API for forex-related news
   - Uses TextBlob for sentiment analysis
   - Falls back to sample data when API key unavailable
   - Filters news by forex relevance keywords

5. **Main Application (`app.py`)**
   - Streamlit frontend with interactive controls
   - Session state management for components
   - Real-time updates with auto-refresh capability
   - Configurable parameters (RSI period, MA periods, confidence threshold)

## Data Flow

1. **Data Acquisition**: yfinance fetches real-time market data for selected currency pairs
2. **Technical Analysis**: Raw price data processed through various technical indicators
3. **News Analysis**: Recent forex news analyzed for sentiment scoring
4. **Signal Generation**: Combined technical and fundamental analysis generates trading signals
5. **Rate Limiting**: Signal manager enforces maximum signal frequency
6. **Persistence**: Signal history stored in JSON format for tracking
7. **Visualization**: Streamlit renders interactive charts and signal dashboard

## External Dependencies

### Data Sources
- **yfinance**: Real-time forex market data
- **News API**: Forex-related news articles (requires API key)

### Key Libraries
- **Streamlit**: Web application framework
- **Plotly**: Interactive charting and visualization
- **Pandas/NumPy**: Data manipulation and numerical computations
- **TextBlob**: Natural language processing for sentiment analysis
- **Requests**: HTTP client for API interactions

### API Requirements
- News API key (stored in environment variable `NEWS_API_KEY`)
- Fallback to sample data when API key unavailable

## Deployment Strategy

- **Platform**: Replit with autoscale deployment
- **Runtime**: Python 3.11 with Nix package management
- **Process**: Streamlit server on port 5000
- **Configuration**: Headless server mode for production deployment
- **Workflows**: Parallel execution with shell commands

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

- June 27, 2025: Initial forex signal generator setup
- June 27, 2025: Enhanced for binary trading with precision timing
- June 27, 2025: Created simplified signal-only app (`simple_binary_app.py`)
  - Removed all complex UI elements and charts
  - Clean, minimal signal display format: "AUD/CAD OTC M1 ⬇️ DOWN TRADE"
  - Automatic 30-second countdown timer for execution
  - High confidence threshold (88%+ for signals)
  - Auto-refresh every 30 seconds to scan for new signals
  - Focused on M1 timeframe for binary options
  - Centered, professional signal presentation
- June 27, 2025: Enhanced for increased signal frequency while maintaining accuracy
  - Lowered confidence threshold from 85% to 75% for more frequent signals
  - Reduced confirmation requirements from 3 to 2 technical indicators
  - Added RSI levels 30/70 in addition to extreme 20/80 levels
  - Added trend continuation signals for moving averages
  - Removed market session restrictions to allow signals during medium volatility
  - Enhanced Bollinger Band and MACD detection for more opportunities
  - Balanced approach: more signals without compromising quality

## Binary Trading Features

### Signal Quality Controls
- Multi-confirmation requirement (minimum 3 technical indicators)
- Market session volatility filtering (skips low-volatility periods)
- Volume surge detection (requires 30-80% above average volume)
- Fresh breakout/reversal detection (not stale signals)
- News sentiment alignment verification

### Timing Precision
- Optimal entry timing calculation (5-40 seconds)
- Market session-based expiry recommendations (1-2 minutes for high volatility)
- Real-time countdown for trade execution
- Bollinger Band breakout/bounce detection for precise entries

### Professional Signal Format
```
📊 AI Binary Trading Signal
Pair: EUR/USD
Timeframe: M1
Direction: BUY
Entry: 14:25:30 (next 30-60 seconds)
Expiry: 1 minute(s)
Reason: RSI extreme oversold reversal + Fresh breakout confirmed
Entry Setup: Strong reversal setup + High volume confirmation
```