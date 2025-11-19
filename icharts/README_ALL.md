# NIFTY Charts Hub - All.py

## Overview
`All.py` is a comprehensive Flask application that serves as a central hub for analyzing all types of NIFTY 50 Index data. It provides a unified interface to access and visualize data from different sources through a single web application.

## Features

### Data Types Supported
- **Nifty Cash**: Spot market data
- **Nifty Future**: Futures market data  
- **Nifty Call**: Call options data
- **Nifty Put**: Put options data

### Chart Types
- **Candlestick Charts**: Interactive OHLC charts with customizable timeframes
- **Summary Charts**: Daily price movement and OHLC summary analysis

### Key Functionality
- Dropdown selection for data type
- Date selection based on available data
- Customizable timeframes (1 minute to 60 minutes)
- Professional dark theme UI
- Real-time chart generation
- Comprehensive market statistics

## How to Run

### Prerequisites
Make sure you have the required dependencies installed:
```bash
pip install -r requirements.txt
```

### Running the Application
1. Navigate to the `icharts` directory
2. Run the application:
```bash
python All.py
```
3. Open your web browser and go to: `http://localhost:5000`

## Usage Instructions

### 1. Select Data Type
- Use the "Data Type" dropdown to choose between:
  - Nifty Cash
  - Nifty Future
  - Nifty Call
  - Nifty Put

### 2. Choose Date
- Select a date from the available dates for your chosen data type
- Dates are automatically loaded based on the selected data type

### 3. Select Chart Type
- **Candlestick Chart**: Detailed OHLC analysis with customizable timeframes
- **Summary Chart**: Daily overview with price movement and OHLC summary

### 4. Set Timeframe (for Candlestick Charts)
- Choose the time interval in minutes (1-60 minutes)
- Default is 1 minute for maximum detail

### 5. Generate Chart
- Click the "Generate Chart" button
- Wait for the chart to be generated
- View the chart and market statistics

## Database Configuration

The application connects to a MySQL database with the following configuration:
- Host: 106.51.63.60
- User: mahesh
- Password: mahesh_123
- Database: historicaldb

### Required Database Tables
- `nifty_cash`: Cash market data
- `nifty_future`: Futures market data
- `nifty_call`: Call options data
- `nifty_put`: Put options data

## File Structure

```
icharts/
├── All.py                 # Main application file
├── templates/
│   └── all_index.html    # Main HTML template
├── app.py                # Original cash market app
├── future.py             # Original futures app
├── nifty_call_app.py     # Original call options app
├── nifty_put_app.py      # Original put options app
└── README_ALL.md         # This file
```

## Technical Details

### Architecture
- **Flask Web Framework**: Lightweight and flexible web framework
- **Matplotlib**: Professional chart generation with dark theme
- **MySQL Connector**: Database connectivity
- **Pandas**: Data manipulation and resampling
- **Responsive Design**: Mobile-friendly HTML/CSS

### Key Functions
- `get_available_dates(data_type)`: Retrieves available dates for specific data type
- `get_ohlc_data_for_date(date, data_type)`: Fetches OHLC data for specific date and type
- `create_candlestick_chart_base64()`: Generates candlestick charts
- `create_summary_chart_base64()`: Generates summary charts
- `resample_ohlc_data()`: Resamples data to different timeframes

### Color Schemes
Each data type has its own color scheme for visual distinction:
- **Nifty Cash**: Green theme (#00ff88)
- **Nifty Future**: Blue theme (#00ccff)
- **Nifty Call**: Green theme (#00ff88)
- **Nifty Put**: Orange theme (#ff8800)

## Benefits

1. **Unified Interface**: Access all NIFTY data types from one application
2. **Consistent Experience**: Same UI and functionality across all data types
3. **Efficient Workflow**: No need to switch between different applications
4. **Professional Charts**: High-quality visualizations with dark theme
5. **Real-time Data**: Live database queries for up-to-date information

## Troubleshooting

### Common Issues
1. **Database Connection Error**: Check database credentials and network connectivity
2. **No Data Available**: Verify that the selected date has data in the database
3. **Chart Generation Failed**: Check if matplotlib is properly configured
4. **Port Already in Use**: Change the port number in `All.py` if port 5000 is occupied

### Debug Routes
- `/test`: Basic Flask functionality test
- `/debug`: Template loading test
- `/get_dates`: API endpoint for available dates

## Future Enhancements

- Real-time data streaming
- Advanced technical indicators
- Export functionality (PDF, CSV)
- User authentication
- Historical data comparison
- Mobile app version

## Support

For technical support or questions, please refer to the main project documentation or contact the development team.
