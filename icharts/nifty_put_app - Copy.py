from flask import Flask, render_template, request, jsonify
import mysql.connector
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web applications
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import io
import base64
import os

app = Flask(__name__)

# Configure matplotlib for web use
plt.ioff()  # Turn off interactive mode
matplotlib.use('Agg')  # Ensure we use the Agg backend

def convert_date_to_db_format(date_str):
    """
    Convert YYYY-MM-DD format to YYMMDD format for database
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%y%m%d')
    except ValueError:
        return None

def convert_db_time_to_readable(seconds):
    """
    Convert seconds since midnight to HH:MM:SS format
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def convert_db_date_to_readable(date_int):
    """
    Convert YYMMDD format to YYYY-MM-DD format
    """
    try:
        date_str = str(date_int)
        if len(date_str) == 6:
            year = "20" + date_str[:2]
            month = date_str[2:4]
            day = date_str[4:6]
            return f"{year}-{month}-{day}"
        return str(date_int)
    except:
        return str(date_int)

def get_available_dates():
    """
    Get list of available dates from database for NIFTY put options
    """
    host = "106.51.63.60"
    user = "mahesh"
    password = "mahesh_123"
    database = "historicaldb"
    
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        
        # Get unique dates from nifty_put table (adjust table name as needed)
        query = """
        SELECT DISTINCT date FROM nifty_put 
        ORDER BY date DESC
        LIMIT 100
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        dates = []
        for row in results:
            date_int = row[0]
            readable_date = convert_db_date_to_readable(date_int)
            dates.append(readable_date)
        
        return dates
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return []
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

def get_available_strikes(date):
    """
    Get available strike prices for a specific date
    """
    host = "106.51.63.60"
    user = "mahesh"
    password = "mahesh_123"
    database = "historicaldb"
    
    try:
        db_date = convert_date_to_db_format(date)
        if db_date is None:
            return []
        
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        
        # Get unique strike prices for the date
        query = """
        SELECT DISTINCT strike FROM nifty_put 
        WHERE date = %s
        ORDER BY strike
        """
        cursor.execute(query, (db_date,))
        results = cursor.fetchall()
        
        strikes = []
        for row in results:
            strikes.append(float(row[0]))
        
        return strikes
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return []
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

def get_available_expiries(date, strike):
    """
    Get available expiry dates for a specific date and strike price
    """
    host = "106.51.63.60"
    user = "mahesh"
    password = "mahesh_123"
    database = "historicaldb"
    
    try:
        db_date = convert_date_to_db_format(date)
        if db_date is None:
            return []
        
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        
        # Get unique expiry dates for the date and strike
        query = """
        SELECT DISTINCT expiry FROM nifty_put 
        WHERE date = %s AND strike = %s
        ORDER BY expiry
        """
        cursor.execute(query, (db_date, strike))
        results = cursor.fetchall()
        
        expiries = []
        for row in results:
            expiry_int = row[0]
            readable_expiry = convert_db_date_to_readable(expiry_int)
            expiries.append(readable_expiry)
        
        return expiries
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return []
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

def get_put_data_for_date_strike_expiry(date, strike, expiry):
    """
    Get NIFTY put option data for a specific date, strike price, and expiry date
    """
    host = "106.51.63.60"
    user = "mahesh"
    password = "mahesh_123"
    database = "historicaldb"
    
    try:
        db_date = convert_date_to_db_format(date)
        db_expiry = convert_date_to_db_format(expiry)
        if db_date is None or db_expiry is None:
            return None
        
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        
        # Get all data for the date, strike, and expiry
        query = """
        SELECT * FROM nifty_put 
        WHERE date = %s AND strike = %s AND expiry = %s
        ORDER BY time
        """
        cursor.execute(query, (db_date, strike, db_expiry))
        results = cursor.fetchall()
        
        if not results:
            return None
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Create DataFrame
        df = pd.DataFrame(results, columns=columns)
        
        # Debug: Print raw data information
        print(f"DEBUG: Raw data from database for date {date}, strike {strike}, expiry {expiry}")
        print(f"Columns: {columns}")
        print(f"Data shape: {df.shape}")
        print(f"First few rows:")
        print(df.head())
        
        # Check for data type issues
        print(f"Data types:")
        print(df.dtypes)
        
        # Check for missing or invalid values
        print(f"Missing values:")
        print(df.isnull().sum())
        
        # Check OHLC data ranges
        if 'open' in df.columns and 'high' in df.columns and 'low' in df.columns and 'close' in df.columns:
            print(f"OHLC ranges (raw values):")
            print(f"Open: {df['open'].min()} to {df['open'].max()}")
            print(f"High: {df['high'].min()} to {df['high'].max()}")
            print(f"Low: {df['low'].min()} to {df['low'].max()}")
            print(f"Close: {df['close'].min()} to {df['close'].max()}")
        
        # Convert database formats back to readable formats
        if 'date' in df.columns:
            df['date_readable'] = df['date'].apply(convert_db_date_to_readable)
        if 'time' in df.columns:
            df['time_readable'] = df['time'].apply(convert_db_time_to_readable)
        if 'expiry' in df.columns:
            df['expiry_readable'] = df['expiry'].apply(convert_db_date_to_readable)
        
        return df
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

def create_put_candlestick_chart(df, date, strike, expiry):
    """
    Create a professional candlestick chart for NIFTY put options
    """
    if df is None or len(df) == 0:
        return None
    
    # Create datetime index for proper time series plotting
    df['datetime'] = pd.to_datetime(df['date_readable'] + ' ' + df['time_readable'])
    df.set_index('datetime', inplace=True)
    
    # Scale down OHLC values by dividing by 100 (convert from paise to rupees)
    df_scaled = df.copy()
    df_scaled['open'] = df['open'] / 100
    df_scaled['high'] = df['high'] / 100
    df_scaled['low'] = df['low'] / 100
    df_scaled['close'] = df['close'] / 100
    
    # Debug: Print data statistics to identify scaling issues
    print(f"DEBUG: Data statistics for strike {strike}:")
    print(f"Open range: {df_scaled['open'].min():.2f} to {df_scaled['open'].max():.2f}")
    print(f"High range: {df_scaled['high'].min():.2f} to {df_scaled['high'].max():.2f}")
    print(f"Low range: {df_scaled['low'].min():.2f} to {df_scaled['low'].max():.2f}")
    print(f"Close range: {df_scaled['close'].min():.2f} to {df_scaled['close'].max():.2f}")
    
    # Filter out extreme outliers that might be data errors
    # Calculate reasonable price range (within 3 standard deviations)
    price_std = df_scaled[['open', 'high', 'low', 'close']].values.flatten().std()
    price_mean = df_scaled[['open', 'high', 'low', 'close']].values.flatten().mean()
    
    # Filter data within reasonable range
    reasonable_mask = (
        (df_scaled['open'] >= price_mean - 3 * price_std) &
        (df_scaled['open'] <= price_mean + 3 * price_std) &
        (df_scaled['high'] >= price_mean - 3 * price_std) &
        (df_scaled['high'] <= price_mean + 3 * price_std) &
        (df_scaled['low'] >= price_mean - 3 * price_std) &
        (df_scaled['low'] <= price_mean + 3 * price_std) &
        (df_scaled['close'] >= price_mean - 3 * price_std) &
        (df_scaled['close'] <= price_mean + 3 * price_std)
    )
    
    df_filtered = df_scaled[reasonable_mask].copy()
    
    if len(df_filtered) == 0:
        print("WARNING: All data filtered out as outliers, using original data")
        df_filtered = df_scaled.copy()
    
    print(f"DEBUG: After filtering outliers: {len(df_filtered)} data points")
    print(f"Filtered price range: {df_filtered[['open', 'high', 'low', 'close']].values.flatten().min():.2f} to {df_filtered[['open', 'high', 'low', 'close']].values.flatten().max():.2f}")
    
    # Set dark theme style
    plt.style.use('dark_background')
    
    # Set up the plot with dark theme
    fig, ax = plt.subplots(figsize=(16, 9), facecolor='#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    # Plot candlesticks with professional styling
    for i, (idx, row) in enumerate(df_filtered.iterrows()):
        # Calculate candlestick dimensions
        open_price = row['open']
        close_price = row['close']
        high_price = row['high']
        low_price = row['low']
        
        # Determine colors (professional trading colors)
        if close_price >= open_price:
            color = '#00ff88'  # Bright green for bullish
            edge_color = '#00cc6a'
            wick_color = '#00ff88'
        else:
            color = '#ff4444'  # Bright red for bearish
            edge_color = '#cc3333'
            wick_color = '#ff4444'
        
        # Plot the wick (line) - thicker and more visible
        ax.plot([i, i], [low_price, high_price], color=wick_color, linewidth=2.5, alpha=0.9)
        
        # Plot the body with better styling
        body_height = abs(close_price - open_price)
        body_bottom = min(open_price, close_price)
        
        if body_height > 0:
            # Main body
            ax.bar(i, body_height, bottom=body_bottom, color=color, 
                   edgecolor=edge_color, linewidth=1.5, width=0.7, alpha=0.9)
            
            # Add subtle gradient effect
            if close_price > open_price:
                # Bullish - add lighter top
                ax.bar(i, body_height * 0.3, bottom=body_bottom + body_height * 0.7, 
                       color='#66ffaa', edgecolor='none', width=0.7, alpha=0.6)
            else:
                # Bearish - add lighter bottom
                ax.bar(i, body_height * 0.3, bottom=body_bottom, 
                       color='#ff6666', edgecolor='none', width=0.7, alpha=0.6)
        else:
            # Doji (open = close) - more visible
            ax.plot([i-0.35, i+0.35], [open_price, open_price], color=edge_color, linewidth=3)
    
    # Customize the plot with professional styling
    ax.set_title(f'NIFTY Put Option • Strike: {strike} • Expiry: {expiry} • OHLC Chart ({date})', 
                 fontsize=18, fontweight='bold', color='#ffffff', pad=20)
    ax.set_xlabel('Time', fontsize=14, color='#cccccc', fontweight='bold')
    ax.set_ylabel('Option Price (INR)', fontsize=14, color='#cccccc', fontweight='bold')
    
    # Professional grid styling
    ax.grid(True, alpha=0.2, color='#444444', linewidth=0.8)
    ax.set_axisbelow(True)
    
    # Set x-axis labels with better formatting
    n_points = len(df_filtered)
    if n_points > 20:
        step = max(1, n_points // 15)
        x_ticks = range(0, n_points, step)
        x_labels = [df_filtered.index[i].strftime('%H:%M') for i in x_ticks]
    else:
        x_ticks = range(n_points)
        x_labels = [df_filtered.index[i].strftime('%H:%M') for i in x_ticks]
    
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels, rotation=45, color='#cccccc', fontsize=11)
    
    # Set y-axis styling with better scaling
    ax.tick_params(axis='y', colors='#cccccc', labelsize=11)
    
    # Improve Y-axis scaling to focus on the actual data range
    price_min = df_filtered[['open', 'high', 'low', 'close']].values.flatten().min()
    price_max = df_filtered[['open', 'high', 'low', 'close']].values.flatten().max()
    price_range = price_max - price_min
    
    # Add some padding to Y-axis for better visibility
    y_padding = price_range * 0.1
    ax.set_ylim(price_min - y_padding, price_max + y_padding)
    
    # Add professional price statistics box
    current_price = df_filtered['close'].iloc[-1]
    price_change = current_price - df_filtered['open'].iloc[0]
    price_change_pct = (df_filtered['open'].iloc[0] > 0) and (price_change / df_filtered['open'].iloc[0]) * 100 or 0
    
    stats_text = f"""Strike: {strike}
Expiry: {expiry}
O {df_filtered['open'].iloc[0]:,.2f}
H {df_filtered['high'].max():,.2f}
L {df_filtered['low'].min():,.2f}
C {current_price:,.2f}
{price_change:+.2f} ({price_change_pct:+.2f}%)"""
    
    # Position stats box like professional platforms
    bbox_props = dict(boxstyle='round,pad=0.8', facecolor='#2a2a2a', 
                      edgecolor='#444444', alpha=0.9)
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            verticalalignment='top', fontsize=12, fontweight='bold',
            color='#ffffff', bbox=bbox_props, fontfamily='monospace')
    
    # Add current price line indicator
    ax.axhline(y=current_price, color='#ff4444', linestyle='--', alpha=0.7, linewidth=1.5)
    
    # Style the spines
    for spine in ax.spines.values():
        spine.set_color('#444444')
        spine.set_linewidth(1.5)
    
    plt.tight_layout()
    
    # Convert plot to base64 string
    img_buffer = io.BytesIO()
    try:
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', 
                    facecolor='#1a1a1a', edgecolor='none')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    except Exception as e:
        print(f"Error saving chart: {e}")
        return None
    finally:
        plt.close('all')  # Close all figures to prevent memory leaks
        plt.clf()  # Clear current figure
    
    return img_base64

def calculate_time_frame(df):
    """
    Calculate time frame information from the data
    """
    try:
        # Get the first and last time entries
        first_time = df['time_readable'].iloc[0]
        last_time = df['time_readable'].iloc[-1]
        
        # Calculate trading duration
        first_seconds = df['time'].iloc[0]
        last_seconds = df['time'].iloc[-1]
        duration_seconds = last_seconds - first_seconds
        
        # Convert duration to hours and minutes
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        
        # Format duration
        if hours > 0:
            duration_str = f"{hours}h {minutes}m"
        else:
            duration_str = f"{minutes}m"
        
        # Calculate data intervals (time between consecutive data points)
        if len(df) > 1:
            interval_seconds = (last_seconds - first_seconds) / (len(df) - 1)
            if interval_seconds < 60:
                interval_str = f"{int(interval_seconds)}s"
            elif interval_seconds < 3600:
                interval_str = f"{int(interval_seconds // 60)}m"
            else:
                interval_str = f"{int(interval_seconds // 3600)}h"
        else:
            interval_str = "N/A"
        
        return {
            'market_open': first_time,
            'market_close': last_time,
            'trading_duration': duration_str,
            'data_intervals': interval_str
        }
        
    except Exception as e:
        print(f"Error calculating time frame: {e}")
        return {
            'market_open': 'N/A',
            'market_close': 'N/A',
            'trading_duration': 'N/A',
            'data_intervals': 'N/A'
        }

@app.route('/')
def index():
    """Main page with date, strike, and expiry selection"""
    dates = get_available_dates()
    return render_template('nifty_put_index.html', dates=dates)

@app.route('/get_strikes/<date>')
def get_strikes_for_date(date):
    """API endpoint to get available strikes for a date"""
    strikes = get_available_strikes(date)
    return jsonify({'strikes': strikes})

@app.route('/get_expiries/<date>/<strike>')
def get_expiries_for_date_strike(date, strike):
    """API endpoint to get available expiry dates for a date and strike"""
    try:
        strike_float = float(strike)
        expiries = get_available_expiries(date, strike_float)
        return jsonify({'expiries': expiries})
    except ValueError:
        return jsonify({'error': 'Invalid strike price'})

@app.route('/generate_put_chart', methods=['POST'])
def generate_put_chart():
    """Generate put option chart based on selected date, strike, and expiry"""
    date = request.form.get('date')
    strike = request.form.get('strike')
    expiry = request.form.get('expiry')
    
    if not date or not strike or not expiry:
        return jsonify({'error': 'Please select date, strike price, and expiry date'})
    
    try:
        strike_float = float(strike)
    except ValueError:
        return jsonify({'error': 'Invalid strike price'})
    
    df = get_put_data_for_date_strike_expiry(date, strike_float, expiry)
    if df is None:
        return jsonify({'error': f'No data found for date: {date}, strike: {strike}, and expiry: {expiry}'})
    
    chart_base64 = create_put_candlestick_chart(df, date, strike_float, expiry)
    if chart_base64 is None:
        return jsonify({'error': 'Failed to generate put option chart'})
        
    chart_title = f'NIFTY Put Option - Strike: {strike} - Expiry: {expiry} - {date}'
    
    # Prepare chart data for interactive chart
    chart_data = []
    for _, row in df.iterrows():
        chart_data.append({
            'time': row['time_readable'],
            'open': float(row['open']) / 100,  # Convert from paise to rupees
            'high': float(row['high']) / 100,
            'low': float(row['low']) / 100,
            'close': float(row['close']) / 100
        })
    
    # Calculate time frame information
    time_frame_info = calculate_time_frame(df)
    
    return jsonify({
        'success': True,
        'chart_base64': chart_base64,
        'chart_title': chart_title,
        'record_count': len(df),
        'strike': strike,
        'expiry': expiry,
        'time_frame': time_frame_info,
        'chart_data': chart_data  # Add this for interactive chart
    })

@app.route('/get_dates')
def get_dates():
    """API endpoint to get available dates"""
    dates = get_available_dates()
    return jsonify({'dates': dates})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8082)
