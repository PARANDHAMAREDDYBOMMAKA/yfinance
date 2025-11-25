# Live Indian Market Data - Real-time Stock Tracker

A beautiful web application to track live Indian stock market data (NSE) using yfinance and Flask.

## Features

- **Real-time stock price updates** for Indian market (NSE/BSE)
- **Dynamic search powered by Yahoo Finance API** - Search ANY Indian stock live
- **Interactive price charts** with multiple timeframes (1D, 1W, 1M, 3M, 6M, 1Y, 5Y, MAX)
- **Beautiful Chart.js visualizations** - Green for gains, red for losses
- **Smart autocomplete suggestions** - Type any company name or symbol
- **Comprehensive coverage** - Access to ALL NSE & BSE listed stocks (5000+ companies)
- **Recently listed companies** - Find even the newest IPOs
- **Keyboard navigation** - Use arrow keys to navigate suggestions
- Detailed stock information (52-week high/low, volume, market cap, etc.)
- Auto-refresh every 30 seconds
- Manual refresh button
- Beautiful gradient UI with smooth animations
- Responsive design
- Indian Rupee (₹) currency display

## Installation

1. Make sure your virtual environment is activated:
```bash
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## Usage

### View Popular Indian Stocks
- The homepage displays 10 popular Indian stocks with live prices
- Includes: Reliance, TCS, HDFC Bank, Infosys, ICICI Bank, and more
- Green indicates price increase, red indicates decrease
- Data auto-refreshes every 30 seconds

### Search for ANY Indian Stock
- Use the search bar at the top
- **Type ANY company name or symbol** (e.g., "Reliance", "TCS", "Tata", "Adani", "Zomato")
- **Live search results** from Yahoo Finance API appear instantly
- Search works for:
  - **All NSE stocks** (5000+ companies)
  - **All BSE stocks**
  - **Recently listed IPOs**
  - **Small-cap, mid-cap, and large-cap companies**
- **Keyboard controls:**
  - Arrow Up/Down: Navigate through suggestions
  - Enter: Select highlighted suggestion
  - Escape: Close suggestions
- Click on any suggestion to view detailed information:
  - Current price and change
  - Previous close and open prices
  - Day's high and low
  - Volume and market cap
  - 52-week high and low
  - **Interactive price chart** with multiple timeframes

### View Price Charts
- When you open a stock's detail view, an **interactive chart** is displayed
- **8 timeframe options**:
  - **1D**: Intraday (5-minute intervals)
  - **1W**: Last 5 days (30-minute intervals)
  - **1M**: Last month (daily)
  - **3M**: Last 3 months (daily)
  - **6M**: Last 6 months (daily)
  - **1Y**: Last year (daily)
  - **5Y**: Last 5 years (weekly)
  - **MAX**: All available history (monthly)
- **Dynamic colors**: Green gradient for positive performance, red for negative
- **Hover to see details**: Hover over any point to see exact price
- **Smooth animations**: Beautiful transitions when switching timeframes

### Stock Symbol Format
- Indian stocks use the `.NS` suffix (NSE) or `.BO` suffix (BSE)
- Examples: `RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS`, `ZOMATO.NS`
- The app automatically adds `.NS` if you enter just the symbol name
- **No need to maintain a local database** - all searches are dynamic!

### Refresh Data
- Click the circular refresh button (↻) in the bottom-right corner
- Or wait for automatic refresh every 30 seconds

## API Endpoints

The application provides the following API endpoints:

- `GET /` - Main web interface
- `GET /api/stocks/multiple` - Get data for multiple default stocks
- `GET /api/stock/<symbol>` - Get detailed data for a specific stock (e.g., `/api/stock/RELIANCE.NS`)
- `GET /api/search/suggestions?q=<query>` - Get autocomplete suggestions (e.g., `/api/search/suggestions?q=reliance`)
- `GET /api/history/<symbol>` - Get historical data (1 day, 5-minute intervals)

## Technologies Used

- Backend: Flask (Python web framework)
- Market Data: yfinance (Yahoo Finance API)
- Frontend: HTML5, CSS3, JavaScript
- Data Processing: Pandas

## Notes

- Stock data is fetched from Yahoo Finance via the yfinance library
- Market data may have a slight delay (typically 15-20 minutes for free tier)
- The app runs on port 8000 by default
- Real-time updates depend on market hours and data availability

## Troubleshooting

If you encounter any issues:

1. Make sure your virtual environment is activated
2. Verify all dependencies are installed: `pip list`
3. Check if port 8000 is available
4. Ensure you have internet connectivity (required for fetching market data)

## How It Works

### Dynamic Search
The app uses **Yahoo Finance API** for live stock search:
- When you type in the search box, the app queries Yahoo Finance API in real-time
- Returns up to 15 matching stocks filtered for Indian markets (NSE/BSE)
- No local database needed - always up-to-date with latest listings
- Fallback to Nifty 50 list if API is unavailable

### Customization
You can customize the default stocks displayed on homepage by editing the `DEFAULT_SYMBOLS` list in `app.py`:

```python
DEFAULT_SYMBOLS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'BHARTIARTL.NS', 'ITC.NS', 'SBIN.NS', 'LT.NS'
]
```

Add or remove stock symbols as per your preference.

## Known Issues

- **Market Hours**: Stock data is most accurate during market hours (9:15 AM - 3:30 PM IST)
- **Data Availability**: Some stocks may not display if yfinance cannot fetch their data
- **Delays**: yfinance data may have a 15-20 minute delay for Indian stocks
- **Missing Stocks**: If a stock doesn't appear, it might be due to:
  - Market being closed
  - Temporary data unavailability from Yahoo Finance
  - Incorrect symbol format (ensure `.NS` suffix is used)
