# ICHARTS - NIFTY Charts Hub

A comprehensive Flask-based web application for analyzing and visualizing NIFTY 50 Index market data including cash, futures, and options (calls & puts). This unified platform provides professional candlestick charts, OHLC analysis, and real-time data visualization for Indian stock market trading.

## 🎯 Overview

ICHARTS is a complete trading analytics platform that consolidates multiple NIFTY data sources into a single, user-friendly web interface. It enables traders and analysts to visualize market data, generate professional charts, and analyze price movements across different market segments.

## ✨ Key Features

### Multi-Market Data Support
- **NIFTY Cash**: Spot market OHLC data visualization
- **NIFTY Futures**: Futures market data analysis
- **NIFTY Call Options**: Call options with dynamic strike price selection
- **NIFTY Put Options**: Put options analysis with strike price filtering

### Chart Types
- **Candlestick Charts**: Professional OHLC charts with customizable timeframes (1-60 minutes)
- **Summary Charts**: Daily overview with price movement statistics
- **Options Chain Visualization**: Comprehensive options chain analysis
- **Straddle Analysis**: Options straddle strategy visualization

### User Interface
- Modern, responsive web design with dark theme
- Dynamic date and strike price selection
- Real-time chart generation
- Mobile-friendly interface
- Professional trading platform aesthetics

### Technical Capabilities
- Database-driven data retrieval from MySQL
- Real-time OHLC data processing
- Timeframe resampling (1min to 60min intervals)
- Market statistics and analytics
- CSV data export functionality

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: MySQL (historical market data)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib (professional chart generation)
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Database Connector**: mysql-connector-python

## 📁 Project Structure

```
icharts/
├── All.py                    # Main unified application (all data types)
├── app.py                    # NIFTY Cash web application
├── future.py                 # NIFTY Futures application
├── nifty_call_app.py         # NIFTY Call Options application
├── nifty_put_app.py          # NIFTY Put Options application
├── database_ohlc.py          # Database OHLC data retrieval
├── candlestick_chart.py      # Chart generation utilities
├── templates/                # HTML templates
│   ├── all_index.html        # Main unified interface
│   ├── index.html            # Cash market interface
│   ├── future_index.html     # Futures interface
│   ├── nifty_call_index.html # Call options interface
│   ├── nifty_put_index.html  # Put options interface
│   └── options_chain_index.html
├── docs/                     # Documentation
├── requirements.txt          # Python dependencies
└── README files              # Component-specific documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- MySQL database with historical NIFTY data
- Required Python packages (see requirements.txt)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AJAIMARVEL/ICHARTS.git
   cd ICHARTS/icharts
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database connection**
   - Update database credentials in the application files
   - Ensure MySQL database is accessible
   - Verify required tables exist (nifty_cash, nifty_future, nifty_call, nifty_put)

4. **Run the application**
   ```bash
   # Unified application (all data types)
   python All.py
   
   # Or run individual applications
   python app.py          # Cash market (port 5000)
   python future.py       # Futures (port 5001)
   python nifty_call_app.py  # Call options (port 8081)
   python nifty_put_app.py   # Put options
   ```

5. **Access the web interface**
   - Open browser: `http://localhost:5000` (for All.py)
   - Select data type, date, and generate charts

## 📊 Database Requirements

The application connects to a MySQL database with the following structure:

- **Host**: Configured in application files
- **Database**: historicaldb
- **Required Tables**:
  - `nifty_cash`: Cash market OHLC data
  - `nifty_future`: Futures market data
  - `nifty_call`: Call options data
  - `nifty_put`: Put options data

### Table Schema
Each table should contain:
- `date`: Trading date (YYMMDD format)
- `time`: Time in seconds since midnight
- `open`, `high`, `low`, `close`: OHLC prices
- `volume`: Trading volume (where applicable)
- `strike`: Strike price (for options tables)

## 🎨 Features in Detail

### Unified Dashboard (All.py)
- Single interface for all NIFTY data types
- Dynamic date selection based on data availability
- Customizable chart timeframes
- Color-coded visualization per data type

### Options Analysis
- Dynamic strike price filtering
- Strike-specific candlestick charts
- Options chain visualization
- Straddle strategy analysis

### Data Export
- CSV export functionality
- Chart image generation
- Market statistics display

## 📝 Usage Examples

### Generate Cash Market Chart
1. Select "Nifty Cash" from data type dropdown
2. Choose a trading date
3. Select chart type (Candlestick or Summary)
4. Set timeframe (for candlestick charts)
5. Click "Generate Chart"

### Analyze Call Options
1. Select "Nifty Call" from data type
2. Choose trading date
3. Select strike price from dropdown
4. Generate chart to view option price movements

## 🔧 Configuration

### Database Settings
Update database configuration in application files:
```python
DB_CONFIG = {
    'host': "your_host",
    'user': "your_user",
    'password': "your_password",
    'database': "historicaldb"
}
```

### Port Configuration
Each application can run on different ports:
- All.py: Port 5000 (default)
- app.py: Port 5000
- future.py: Port 5001
- nifty_call_app.py: Port 8081

## 📚 Documentation

- `README.md`: Basic database OHLC retrieval
- `README_ALL.md`: Unified application documentation
- `README_WEB.md`: Web application features
- `README_NIFTY_CALL.md`: Call options application guide
- `README_NIFTY_PUT.md`: Put options application guide

## 🧪 Testing

The project includes multiple test scripts:
- `test_nifty_call.py`: Database connection testing
- `test_web_endpoint.py`: API endpoint testing
- `test_chart_generation.py`: Chart generation validation
- Various other test utilities

## 🔒 Security Notes

- Database credentials are currently hardcoded (development mode)
- For production, use environment variables or secure configuration
- Consider implementing authentication for production deployment
- Network access should be restricted as needed

## 🚀 Future Enhancements

- Real-time data streaming
- Advanced technical indicators (RSI, MACD, Bollinger Bands)
- Export functionality (PDF, Excel)
- User authentication and session management
- Historical data comparison
- Mobile app version
- Option Greeks calculation
- Risk management tools
- Backtesting capabilities



**Built with ❤️ for the Indian stock market trading community**

