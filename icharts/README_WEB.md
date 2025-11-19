# NIFTY CASH Chart Generator - Web Application

This is a web-based version of the NIFTY CASH candlestick chart generator that allows you to generate charts through a modern web interface instead of the command line.

## Features

- 🌐 **Web Interface**: Beautiful, responsive web application
- 📅 **Date Dropdown**: Select dates from a dropdown populated with available data
- 📈 **Two Chart Types**: 
  - Candlestick charts showing intraday OHLC data
  - Summary charts with daily overview and statistics
- 📱 **Mobile Responsive**: Works on all device sizes
- ⚡ **Real-time Generation**: Charts are generated on-demand
- 🎨 **Modern UI**: Clean, professional design with smooth animations

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Connection**: 
   - Ensure your MySQL database is accessible
   - The application uses the same database credentials as the original script

## Running the Web Application

1. **Start the Flask Server**:
   ```bash
   python app.py
   ```

2. **Access the Web Interface**:
   - Open your browser and go to: `http://localhost:5000`
   - The application will automatically load available dates from your database

## How to Use

1. **Select a Date**: Choose a date from the dropdown menu
2. **Choose Chart Type**: Click either:
   - "Generate Candlestick Chart" for detailed intraday candlestick view
   - "Generate Summary Chart" for daily overview with statistics
3. **View Results**: The chart will be displayed below with additional information

## File Structure

```
database_chart/
├── app.py                 # Flask web application
├── templates/
│   └── index.html        # Web interface template
├── candlestick_chart.py  # Original command-line version
├── requirements.txt       # Python dependencies
└── README_WEB.md         # This file
```

## Technical Details

- **Backend**: Flask web framework
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Charts**: Matplotlib (converted to base64 for web display)
- **Database**: MySQL with mysql-connector-python
- **Responsive Design**: CSS Grid and Flexbox for mobile compatibility

## API Endpoints

- `GET /` - Main page with date selection
- `POST /generate_chart` - Generate chart based on date and type
- `GET /get_dates` - Get list of available dates

## Troubleshooting

- **No dates showing**: Check database connection and ensure data exists
- **Charts not generating**: Verify database credentials and table structure
- **Port conflicts**: Change port in `app.py` if 5000 is already in use

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers

## Security Notes

- Database credentials are hardcoded in the application
- For production use, consider using environment variables
- The application runs on all interfaces (0.0.0.0) - restrict as needed for production
