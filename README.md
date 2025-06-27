# AI Binary Trading Signal Generator

## Deployment Instructions

### For Python-Supporting Platforms (Recommended)

**Vercel (Recommended):**
1. Upload this folder to Vercel
2. Set framework to "Other"
3. Build command: `pip install -r requirements.txt`
4. Start command: `streamlit run app.py --server.port 8000 --server.address 0.0.0.0`

**Railway:**
1. Upload this folder to Railway
2. Add these environment variables:
   - `PORT=8000`
3. Railway will auto-detect and install dependencies

**Render:**
1. Upload this folder to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

**Heroku:**
1. Add `Procfile` with: `web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
2. Deploy to Heroku

### Files Included

- `app.py` - Main entry point
- `simple_binary_app.py` - Core trading signal app
- `trading_engine.py` - Market data and signal generation
- `technical_indicators.py` - Technical analysis calculations
- `signal_manager.py` - Signal history management
- `news_analyzer.py` - Market sentiment analysis
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit configuration

### Features

- Real-time forex market data analysis
- Enhanced frequency binary trading signals (75%+ confidence)
- 1-minute timeframe optimization
- Precise entry timing (30-60 seconds)
- Multiple technical indicator confirmations
- Professional signal format: "EUR/USD OTC M1 ⬆️ UP TRADE"

### Signal Quality

- Balanced approach: High frequency with maintained accuracy
- Multiple confirmations required (RSI, MACD, Bollinger Bands)
- Enhanced RSI levels (30/70 + extreme 20/80) for more opportunities
- Trend continuation signals for moving averages
- Volume surge detection
- Fresh breakout/reversal identification
- News sentiment alignment
- Reduced confirmation requirements (2 indicators vs 3) for frequency

The app now balances frequency and accuracy - more signals while maintaining quality thresholds.