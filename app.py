from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import yfinance as yf
from datetime import datetime
import traceback
import requests

app = Flask(__name__)
CORS(app)

# Indian market stocks (NSE) - Only for default display
DEFAULT_SYMBOLS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'BHARTIARTL.NS', 'ITC.NS', 'SBIN.NS', 'LT.NS'
]

# Function to search stocks dynamically using Yahoo Finance API
def search_yahoo_finance(query):
    """Search for Indian stocks using Yahoo Finance API"""
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search"
        params = {
            'q': query,
            'quotesCount': 15,
            'newsCount': 0,
            'enableFuzzyQuery': False,
            'quotesQueryId': 'tss_match_phrase_query',
            'region': 'IN',
            'lang': 'en-IN'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, params=params, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            quotes = data.get('quotes', [])

            # Filter for Indian stocks (NSE and BSE)
            indian_stocks = []
            for quote in quotes:
                symbol = quote.get('symbol', '')
                # Only include NSE (.NS) and BSE (.BO) stocks
                if '.NS' in symbol or '.BO' in symbol:
                    indian_stocks.append({
                        'symbol': symbol,
                        'name': quote.get('longname') or quote.get('shortname', symbol)
                    })

            return indian_stocks

        return []

    except Exception as e:
        print(f"Error searching Yahoo Finance: {e}")
        return []

# Minimal fallback list (Nifty 50) for when API fails
FALLBACK_STOCKS = [
    {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries'},
    {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services'},
    {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank'},
    {'symbol': 'INFY.NS', 'name': 'Infosys'},
    {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank'},
    {'symbol': 'HINDUNILVR.NS', 'name': 'Hindustan Unilever'},
    {'symbol': 'BHARTIARTL.NS', 'name': 'Bharti Airtel'},
    {'symbol': 'ITC.NS', 'name': 'ITC Limited'},
    {'symbol': 'SBIN.NS', 'name': 'State Bank of India'},
    {'symbol': 'LT.NS', 'name': 'Larsen & Toubro'},
    {'symbol': 'BAJFINANCE.NS', 'name': 'Bajaj Finance'},
    {'symbol': 'KOTAKBANK.NS', 'name': 'Kotak Mahindra Bank'},
    {'symbol': 'HCLTECH.NS', 'name': 'HCL Technologies'},
    {'symbol': 'WIPRO.NS', 'name': 'Wipro'},
    {'symbol': 'ASIANPAINT.NS', 'name': 'Asian Paints'},
    {'symbol': 'MARUTI.NS', 'name': 'Maruti Suzuki'},
    {'symbol': 'TATAMOTORS.NS', 'name': 'Tata Motors'},
    {'symbol': 'TITAN.NS', 'name': 'Titan Company'},
    {'symbol': 'SUNPHARMA.NS', 'name': 'Sun Pharmaceutical'},
    {'symbol': 'ULTRACEMCO.NS', 'name': 'UltraTech Cement'},
    {'symbol': 'NESTLEIND.NS', 'name': 'Nestle India'},
    {'symbol': 'ONGC.NS', 'name': 'ONGC'},
    {'symbol': 'NTPC.NS', 'name': 'NTPC'},
    {'symbol': 'POWERGRID.NS', 'name': 'Power Grid Corporation'},
    {'symbol': 'AXISBANK.NS', 'name': 'Axis Bank'},
    {'symbol': 'M&M.NS', 'name': 'Mahindra & Mahindra'},
    {'symbol': 'TECHM.NS', 'name': 'Tech Mahindra'},
    {'symbol': 'TATASTEEL.NS', 'name': 'Tata Steel'},
    {'symbol': 'ADANIPORTS.NS', 'name': 'Adani Ports'},
    {'symbol': 'ADANIENT.NS', 'name': 'Adani Enterprises'},
    {'symbol': 'BAJAJFINSV.NS', 'name': 'Bajaj Finserv'},
    {'symbol': 'DIVISLAB.NS', 'name': 'Divi\'s Laboratories'},
    {'symbol': 'DRREDDY.NS', 'name': 'Dr. Reddy\'s Laboratories'},
    {'symbol': 'EICHERMOT.NS', 'name': 'Eicher Motors'},
    {'symbol': 'GRASIM.NS', 'name': 'Grasim Industries'},
    {'symbol': 'HEROMOTOCO.NS', 'name': 'Hero MotoCorp'},
    {'symbol': 'HINDALCO.NS', 'name': 'Hindalco Industries'},
    {'symbol': 'INDUSINDBK.NS', 'name': 'IndusInd Bank'},
    {'symbol': 'JSWSTEEL.NS', 'name': 'JSW Steel'},
    {'symbol': 'CIPLA.NS', 'name': 'Cipla'},
    {'symbol': 'BPCL.NS', 'name': 'Bharat Petroleum'},
    {'symbol': 'COALINDIA.NS', 'name': 'Coal India'},
    {'symbol': 'BRITANNIA.NS', 'name': 'Britannia Industries'},
    {'symbol': 'SHREECEM.NS', 'name': 'Shree Cement'},
    {'symbol': 'VEDL.NS', 'name': 'Vedanta'},
    {'symbol': 'APOLLOHOSP.NS', 'name': 'Apollo Hospitals'},
    {'symbol': 'TATACONSUM.NS', 'name': 'Tata Consumer Products'},
    {'symbol': 'ADANIGREEN.NS', 'name': 'Adani Green Energy'},
    {'symbol': 'SBILIFE.NS', 'name': 'SBI Life Insurance'},
    {'symbol': 'HDFCLIFE.NS', 'name': 'HDFC Life Insurance'},
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info

        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        previous_close = info.get('previousClose', 0)

        change = current_price - previous_close if current_price and previous_close else 0
        change_percent = (change / previous_close * 100) if previous_close else 0

        data = {
            'symbol': symbol.upper(),
            'name': info.get('longName', symbol.upper()),
            'price': round(current_price, 2) if current_price else 0,
            'change': round(change, 2),
            'changePercent': round(change_percent, 2),
            'previousClose': round(previous_close, 2) if previous_close else 0,
            'open': round(info.get('open', 0), 2),
            'dayHigh': round(info.get('dayHigh', 0), 2),
            'dayLow': round(info.get('dayLow', 0), 2),
            'volume': info.get('volume', 0),
            'marketCap': info.get('marketCap', 0),
            'fiftyTwoWeekHigh': round(info.get('fiftyTwoWeekHigh', 0), 2),
            'fiftyTwoWeekLow': round(info.get('fiftyTwoWeekLow', 0), 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 400

@app.route('/api/stocks/multiple')
def get_multiple_stocks():
    try:
        stocks_data = []

        for symbol in DEFAULT_SYMBOLS:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info

                current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
                previous_close = info.get('previousClose', 0)

                change = current_price - previous_close if current_price and previous_close else 0
                change_percent = (change / previous_close * 100) if previous_close else 0

                stocks_data.append({
                    'symbol': symbol,
                    'name': info.get('longName', symbol),
                    'price': round(current_price, 2) if current_price else 0,
                    'change': round(change, 2),
                    'changePercent': round(change_percent, 2)
                })
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                continue

        return jsonify({
            'stocks': stocks_data,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 400

@app.route('/api/history/<symbol>')
def get_stock_history(symbol):
    """Get historical data for different time periods"""
    try:
        period = request.args.get('period', '1d')  # Default to 1 day

        # Map periods to yfinance parameters
        period_map = {
            '1d': {'period': '1d', 'interval': '5m'},
            '1w': {'period': '5d', 'interval': '30m'},
            '1m': {'period': '1mo', 'interval': '1d'},
            '3m': {'period': '3mo', 'interval': '1d'},
            '6m': {'period': '6mo', 'interval': '1d'},
            '1y': {'period': '1y', 'interval': '1d'},
            '5y': {'period': '5y', 'interval': '1wk'},
            'max': {'period': 'max', 'interval': '1mo'}
        }

        params = period_map.get(period, period_map['1d'])

        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(**params)

        if hist.empty:
            return jsonify({'error': 'No historical data available'}), 404

        history_data = []

        for index, row in hist.iterrows():
            # Format date based on period
            if period == '1d':
                time_str = index.strftime('%H:%M')
            elif period in ['1w', '1m', '3m', '6m']:
                time_str = index.strftime('%d %b')
            else:
                time_str = index.strftime('%b %Y')

            history_data.append({
                'time': time_str,
                'timestamp': int(index.timestamp() * 1000),  # For sorting
                'price': round(row['Close'], 2),
                'open': round(row['Open'], 2),
                'high': round(row['High'], 2),
                'low': round(row['Low'], 2),
                'volume': int(row['Volume'])
            })

        return jsonify({
            'symbol': symbol.upper(),
            'period': period,
            'history': history_data
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 400

@app.route('/api/search/suggestions')
def search_suggestions():
    """Dynamic stock search using Yahoo Finance API"""
    try:
        query = request.args.get('q', '').strip()

        if not query:
            return jsonify({'suggestions': []})

        # First, try Yahoo Finance API for live search
        suggestions = search_yahoo_finance(query)

        # If API returns results, use them
        if suggestions:
            return jsonify({'suggestions': suggestions})

        # Fallback: search in local Nifty 50 list
        query_upper = query.upper()
        fallback_results = []

        for stock in FALLBACK_STOCKS:
            symbol_clean = stock['symbol'].replace('.NS', '').upper()
            name_upper = stock['name'].upper()

            if symbol_clean.startswith(query_upper) or query_upper in name_upper:
                fallback_results.append(stock)

            if len(fallback_results) >= 10:
                break

        return jsonify({'suggestions': fallback_results})

    except Exception as e:
        return jsonify({
            'error': str(e),
            'suggestions': []
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
