# 📉 NIFTY Put Options Chart Generator

A professional Flask-based web application for generating interactive candlestick charts from NIFTY Put Options OHLC data. This application provides a comprehensive trading platform interface with advanced charting capabilities.

## 🚀 Features

### **Core Functionality**
- **Three-Tier Selection**: Date → Strike Price → Expiry Date
- **Dynamic Dropdowns**: Cascading selection that loads available options
- **Interactive Charts**: Professional TradingView-style candlestick charts
- **OHLC Tooltips**: Hover over bars to see detailed price information
- **Real-time Data**: Fetch data from MySQL database in real-time

### **Chart Features**
- **Professional Styling**: Dark theme with professional trading colors
- **Responsive Design**: Charts adapt to different screen sizes
- **Interactive Elements**: Zoom, pan, and hover functionality
- **Statistical Overlay**: Price statistics and time frame information
- **Fallback Support**: Static charts if interactive library fails to load

### **Data Analysis**
- **OHLC Visualization**: Open, High, Low, Close price representation
- **Time Frame Analysis**: Market open/close times and trading duration
- **Data Validation**: Outlier filtering and data quality checks
- **Performance Metrics**: Price changes and percentage calculations

## 🏗️ File Structure

```
database_chart/
├── nifty_put_app.py              # Main Flask application
├── templates/
│   └── nifty_put_index.html     # HTML interface template
├── requirements.txt               # Python dependencies
└── README_NIFTY_PUT.md          # This documentation
```

## 🗄️ Database Requirements

### **Table Structure**
The application expects a `nifty_put` table with the following columns:
- `date`: Trading date (YYMMDD format)
- `strike`: Strike price
- `expiry`: Expiry date (YYMMDD format)
- `time`: Time in seconds since midnight
- `open`: Opening price (in paise)
- `high`: High price (in paise)
- `low`: Low price (in paise)
- `close`: Closing price (in paise)

### **Database Connection**
- **Host**: 106.51.63.60
- **Database**: historicaldb
- **User**: mahesh
- **Password**: mahesh_123

## 🛠️ Installation

### **1. Prerequisites**
- Python 3.7+
- MySQL database access
- Modern web browser

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Required Packages**
```
Flask==3.0.0
mysql-connector-python==8.2.0
pandas==2.1.4
matplotlib==3.8.2
numpy
```

## 🚀 Usage

### **1. Start the Application**
```bash
python nifty_put_app.py
```

### **2. Access the Application**
Open your browser and navigate to:
```
http://localhost:8082
```

### **3. Using the Interface**

#### **Step 1: Select Date**
- Choose a trading date from the dropdown
- Available dates are loaded from the database

#### **Step 2: Select Strike Price**
- Strike prices populate based on selected date
- Prices are sorted numerically

#### **Step 3: Select Expiry Date**
- Expiry dates populate based on selected date and strike
- Dates are sorted chronologically

#### **Step 4: Generate Chart**
- Click "Generate Put Option Chart" button
- Interactive candlestick chart will be displayed

## 🎯 API Endpoints

### **GET Endpoints**
- `/` - Main page with selection interface
- `/get_dates` - Returns available trading dates
- `/get_strikes/<date>` - Returns strikes for a specific date
- `/get_expiries/<date>/<strike>` - Returns expiries for date/strike

### **POST Endpoints**
- `/generate_put_chart` - Generates chart based on form data

## 📊 Chart Features

### **Interactive Elements**
- **Hover Tooltips**: Display OHLC data on bar hover
- **Crosshair**: Vertical and horizontal price/time indicators
- **Zoom & Pan**: Navigate through time periods
- **Responsive**: Adapts to window resizing

### **Visual Styling**
- **Dark Theme**: Professional trading platform appearance
- **Color Coding**: Green for bullish, red for bearish candles
- **Grid Lines**: Subtle background grid for readability
- **Typography**: Clear, readable fonts and sizing

### **Data Display**
- **Price Statistics**: Open, High, Low, Close values
- **Time Information**: Market hours and trading duration
- **Performance Metrics**: Price changes and percentages
- **Data Count**: Number of data points analyzed

## 🔧 Configuration

### **Port Configuration**
The application runs on port 8082 by default:
```python
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8082)
```

### **Database Configuration**
Database connection parameters are hardcoded in the application:
```python
host = "106.51.63.60"
user = "mahesh"
password = "mahesh_123"
database = "historicaldb"
```

## 🐛 Troubleshooting

### **Common Issues**

#### **1. Database Connection Errors**
- Verify database server is running
- Check network connectivity to 106.51.63.60
- Confirm user credentials are correct

#### **2. Chart Not Loading**
- Check browser console for JavaScript errors
- Verify TradingView LightweightCharts library loads
- Fallback to static charts if interactive fails

#### **3. No Data Available**
- Verify table name is `nifty_put`
- Check data exists for selected parameters
- Review database table structure

#### **4. Port Already in Use**
- Change port number in `nifty_put_app.py`
- Kill existing processes using the port
- Use different port: `app.run(port=8083)`

### **Debug Information**
The application includes extensive debug logging:
- Database query results
- Data processing steps
- Chart generation details
- Error messages and stack traces

## 🔒 Security Notes

- Database credentials are hardcoded (not recommended for production)
- No authentication or authorization implemented
- Direct database access from web application
- Consider implementing proper security measures for production use

## 🚀 Future Enhancements

### **Planned Features**
- **User Authentication**: Login system and user management
- **Data Export**: CSV/Excel download functionality
- **Advanced Indicators**: RSI, MACD, Moving Averages
- **Real-time Updates**: Live data streaming
- **Mobile App**: Native mobile application

### **Technical Improvements**
- **API Rate Limiting**: Prevent abuse and ensure stability
- **Caching**: Redis integration for better performance
- **Logging**: Structured logging with log rotation
- **Monitoring**: Health checks and performance metrics
- **Containerization**: Docker support for easy deployment

## 📱 Browser Compatibility

- **Chrome**: 80+ (Recommended)
- **Firefox**: 75+
- **Safari**: 13+
- **Edge**: 80+
- **Mobile**: Responsive design for mobile browsers

## 🎨 Customization

### **Styling Changes**
- Modify CSS in `templates/nifty_put_index.html`
- Update color schemes and themes
- Adjust layout and spacing
- Customize chart appearance

### **Functionality Extensions**
- Add new chart types
- Implement additional data filters
- Create custom indicators
- Extend API endpoints

## 📞 Support

For technical support or feature requests:
1. Check the troubleshooting section
2. Review debug logs in console
3. Verify database connectivity
4. Test with different browsers

## 📄 License

This application is provided as-is for educational and development purposes. Please ensure compliance with your organization's data usage policies and database access requirements.

---

**Note**: This application is specifically designed for NIFTY Put Options data analysis. For other instruments or markets, the code structure can be adapted by modifying the database queries and table references.
