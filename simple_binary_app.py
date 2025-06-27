import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from trading_engine import TradingEngine
from signal_manager import SignalManager

# Page configuration
st.set_page_config(
    page_title="Binary Trading Signals",
    page_icon="📊",
    layout="centered"
)

# Initialize session state
if 'signal_manager' not in st.session_state:
    st.session_state.signal_manager = SignalManager()
if 'trading_engine' not in st.session_state:
    st.session_state.trading_engine = TradingEngine()
if 'last_signal_check' not in st.session_state:
    st.session_state.last_signal_check = datetime.now()

def get_simple_signal():
    """Get a clean, simple binary trading signal"""
    # Currency pairs for binary trading
    pairs = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "AUDCAD=X"]
    
    for pair in pairs:
        try:
            # Get 1-minute data
            data = st.session_state.trading_engine.get_market_data(pair, "1m", "1d")
            if data is None or data.empty:
                continue
                
            # Calculate indicators
            indicators = st.session_state.trading_engine.calculate_indicators(data, 14, 8, 18)
            
            # Generate signal with moderate confidence threshold for more frequency
            signal = st.session_state.trading_engine.generate_binary_trading_signal(
                data, indicators, confidence_threshold=75, timeframe="1m"
            )
            
            if signal and signal['confidence'] >= 75:
                return signal
                
        except Exception as e:
            continue
    
    return None

def format_simple_signal(signal):
    """Format signal in the exact style requested"""
    pair = signal['pair']
    direction_arrow = "⬇️" if signal['direction'] == "SELL" else "⬆️"
    direction_text = "DOWN TRADE" if signal['direction'] == "SELL" else "UP TRADE"
    
    # Calculate execution time (30 seconds from now)
    execution_time = (datetime.now() + timedelta(seconds=30)).strftime('%H:%M:%S')
    
    return f"""**{pair} OTC M1**
{direction_arrow} **{direction_text}**

**Execute at: {execution_time}**"""

def main():
    # Hide Streamlit elements
    st.markdown("""
    <style>
    .stApp > header {visibility: hidden;}
    .stApp > div[data-testid="stDecoration"] {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp > div[data-testid="stToolbar"] {visibility: hidden;}
    
    .main-container {
        text-align: center;
        padding: 2rem;
    }
    
    .signal-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    .waiting-box {
        background: linear-gradient(135deg, #434343 0%, #000000 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        font-size: 1.2rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check for new signals every 30 seconds
    current_time = datetime.now()
    if (current_time - st.session_state.last_signal_check).seconds >= 30:
        st.session_state.last_signal_check = current_time
        
        # Get new signal
        signal = get_simple_signal()
        
        if signal:
            # Add to signal manager
            st.session_state.signal_manager.add_signal(signal)
            
            # Display the signal
            signal_text = format_simple_signal(signal)
            
            st.markdown(f"""
            <div class="signal-box">
                {signal_text.replace('**', '')}
            </div>
            """, unsafe_allow_html=True)
            
            # Countdown timer
            st.markdown("---")
            
            # Create countdown without blocking the interface
            countdown_placeholder = st.empty()
            countdown_placeholder.markdown(f"""
            <div style="text-align: center; font-size: 2rem; color: #ff4444;">
                ⏱️ Execute in 30 seconds
            </div>
            """, unsafe_allow_html=True)
            
            # Auto refresh after showing signal
            time.sleep(2)
            st.rerun()
        
        else:
            # No signal available
            st.markdown(f"""
            <div class="waiting-box">
                <h3>🔍 Scanning for Quality Trading Signals...</h3>
                <p>Enhanced frequency mode - 75% confidence threshold</p>
                <p>Next scan in: {30 - (current_time.second % 30)} seconds</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Auto refresh
            time.sleep(5)
            st.rerun()
    
    else:
        # Show recent signal if available
        recent_signals = st.session_state.signal_manager.get_recent_signals(1)
        if recent_signals:
            signal = recent_signals[0]
            signal_age = (datetime.now() - signal['timestamp']).seconds
            
            if signal_age < 120:  # Show if less than 2 minutes old
                signal_text = format_simple_signal(signal)
                st.markdown(f"""
                <div class="signal-box">
                    {signal_text.replace('**', '')}<br>
                    <small style="opacity: 0.7;">Generated {signal_age}s ago</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="waiting-box">
                    <h3>🔍 Scanning for High-Probability Signals...</h3>
                    <p>Waiting for optimal market conditions</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="waiting-box">
                <h3>🔍 Scanning for High-Probability Signals...</h3>
                <p>Waiting for optimal market conditions</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()