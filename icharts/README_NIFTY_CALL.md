# NIFTY Call Options Chart Generator

A professional Flask web application for generating candlestick charts for NIFTY call options with dynamic strike price selection.

## 🚀 Features

- **Date Selection**: Choose from available trading dates
- **Strike Price Dropdown**: Dynamic dropdown populated with available strike prices for the selected date
- **Professional Candlestick Charts**: High-quality OHLC charts with dark theme
- **Real-time Data**: Fetches data from MySQL database
- **Responsive Design**: Modern, professional trading platform interface
- **Time Frame Information**: Shows market open/close times and trading duration

## 📁 Files

- `nifty_call_app.py` - Main Flask application for NIFTY call options
- `templates/nifty_call_index.html` - HTML template with date and strike selection
- `test_nifty_call.py` - Database connection and table structure test script

## 🗄️ Database Requirements

The application expects a MySQL database with a table containing NIFTY call options data. The table should have:

- `date` - Trading date (YYMMDD format)
- `time` - Time in seconds since midnight
- `strike` - Strike price of the option
- `open` - Opening price
- `high` - High price
- `low` - Low price
- `close` - Closing price

### Expected Table Names
- `nifty_call` (primary)
- Alternative names: `nifty_options`, `nifty_calls`, `nifty_ce`, etc.

## 🛠️ Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test Database Connection
```bash
python test_nifty_call.py
```

This will:
- Test database connectivity
- Check if the required table exists
- Show available dates and strike prices
- Suggest alternative table names if needed

### 3. Run the Application
```bash
python nifty_call_app.py
```

The app will run on port 8081 to avoid conflicts with your existing NIFTY cash app.

## 🌐 Usage

### Access the Application
Open your browser and go to:
```
http://127.0.0.1:8081
```

### Step-by-Step Process
1. **Select Date**: Choose a trading date from the dropdown
2. **Select Strike**: Choose a strike price from the dynamically populated dropdown
3. **Generate Chart**: Click "Generate Call Option Chart"
4. **View Results**: Professional candlestick chart with trading statistics

## 🔧 Configuration

### Database Settings
Edit `nifty_call_app.py` to modify database connection:
```python
host = "106.51.63.60"
user = "mahesh"
password = "mahesh_123"
database = "historicaldb"
```

### Port Configuration
Change the port in `nifty_call_app.py`:
```python
app.run(debug=False, host='0.0.0.0', port=8081)
```

## 📊 Chart Features

- **Professional Styling**: Dark theme with professional trading colors
- **OHLC Data**: Open, High, Low, Close price visualization
- **Time Series**: Proper time formatting on X-axis
- **Statistics Box**: Shows strike price, OHLC values, and price change
- **Trading Information**: Market open/close times, duration, and data intervals

## 🚨 Troubleshooting

### Database Connection Issues
1. Run `python test_nifty_call.py` to diagnose database problems
2. Check if the table name is correct
3. Verify database credentials and network access

### Table Not Found
If `nifty_call` table doesn't exist:
1. Check what tables are available in your database
2. Update the table name in `nifty_call_app.py`
3. Ensure the table has the required columns (date, time, strike, open, high, low, close)

### Port Conflicts
If port 8081 is busy:
1. Change the port in `nifty_call_app.py`
2. Update the URL in your browser accordingly

## 🔄 API Endpoints

- `GET /` - Main page with date and strike selection
- `GET /get_dates` - Get available trading dates
- `GET /get_strikes/<date>` - Get available strike prices for a date
- `POST /generate_call_chart` - Generate candlestick chart for selected date/strike

## 📱 Browser Compatibility

- Chrome (recommended)
- Firefox
- Edge
- Safari

## 🎨 Customization

### Chart Colors
Modify colors in `create_call_candlestick_chart()` function:
```python
# Bullish colors
color = '#00ff88'  # Green
edge_color = '#00cc6a'

# Bearish colors  
color = '#ff4444'  # Red
edge_color = '#cc3333'
```

### Chart Size
Change chart dimensions:
```python
fig, ax = plt.subplots(figsize=(16, 9), facecolor='#1a1a1a')
```

## 📈 Data Format

The application expects OHLC data in paise (Indian currency) and automatically converts to rupees by dividing by 100.

## 🔐 Security Notes

- This is a development application
- Database credentials are hardcoded (not recommended for production)
- Consider using environment variables for production deployment

## 📞 Support

If you encounter issues:
1. Check the database connection with `test_nifty_call.py`
2. Verify table structure and data availability
3. Check Flask application logs for error messages

## 🚀 Future Enhancements

- Interactive charts with TradingView integration
- Multiple timeframe analysis
- Option Greeks calculation
- Risk management tools
- Export functionality (PDF, CSV)
- Real-time data streaming
