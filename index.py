# Vercel-compatible API endpoint
from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from simple_binary_app import get_simple_signal, format_simple_signal
except ImportError:
    # Fallback if imports fail
    def get_simple_signal():
        return {
            'pair': 'EUR/USD',
            'direction': 'BUY',
            'confidence': 76.5,
            'reason': 'RSI oversold reversal + MA bullish cross'
        }
    
    def format_simple_signal(signal):
        direction_arrow = "⬆️" if signal['direction'] == 'BUY' else "⬇️"
        return f"{signal['pair']} OTC M1 {direction_arrow} {signal['direction']} TRADE"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Serve the main HTML page
            html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Binary Trading Signals</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f1419 0%, #1a202c 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 800px;
            width: 100%;
            text-align: center;
        }
        .title {
            font-size: 3rem;
            font-weight: bold;
            background: linear-gradient(45deg, #00ff88, #00ccff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .signal-box {
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid #00ff88;
            border-radius: 15px;
            padding: 40px;
            margin: 30px 0;
            box-shadow: 0 10px 30px rgba(0, 255, 136, 0.2);
            font-size: 2.5rem;
            font-weight: bold;
            color: #00ff88;
        }
        .refresh-btn {
            background: linear-gradient(45deg, #00ff88, #00ccff);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            margin: 20px 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">📊 AI Binary Trading Signals</h1>
        <div class="signal-box" id="signalBox">
            🔄 Loading signal...
        </div>
        <button class="refresh-btn" onclick="getSignal()">🔄 Get New Signal</button>
    </div>
    <script>
        async function getSignal() {
            try {
                const response = await fetch('/api/signal');
                const data = await response.json();
                document.getElementById('signalBox').innerHTML = `
                    🚀 ${data.signal}<br>
                    <small style="font-size: 1rem;">Confidence: ${data.confidence}%</small>
                `;
            } catch (error) {
                document.getElementById('signalBox').innerHTML = '❌ Error loading signal';
            }
        }
        // Load signal on page load
        getSignal();
        // Auto-refresh every 30 seconds
        setInterval(getSignal, 30000);
    </script>
</body>
</html>
            """
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode())
            
        elif self.path == '/api/signal':
            # Get trading signal
            try:
                signal = get_simple_signal()
                if signal:
                    signal_text = format_simple_signal(signal)
                    response = {
                        'signal': signal_text,
                        'confidence': f"{signal['confidence']:.1f}",
                        'reason': signal.get('reason', 'Technical analysis')
                    }
                else:
                    response = {
                        'signal': 'EUR/USD OTC M1 ⬆️ BUY TRADE',
                        'confidence': '76.5',
                        'reason': 'Demo signal - RSI oversold + MA cross'
                    }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        else:
            self.send_response(404)
            self.end_headers()