from flask import Flask, render_template, request, jsonify, send_file
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

# Add debug route to test if Flask is working
@app.route('/test')
def test():
    return "Flask is working! This is a test route."

# Add debug route to check template loading
@app.route('/debug')
def debug():
    try:
        dates = get_available_dates()
        return f"Debug: Template loading test. Available dates: {len(dates)} dates found."
    except Exception as e:
        return f"Debug: Error occurred: {str(e)}"

# Add simple hello world route for testing
@app.route('/hello')
def hello():
    return "Hello World! Flask is working correctly."

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

def get_available_dates():
    """
    Get list of available dates from database
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
        
        # Get unique dates
        query = """
        SELECT DISTINCT date FROM nifty_cash 
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

def get_ohlc_data_for_date(date):
    """
    Get OHLC data for a specific date
    """
    host = "106.51.63.60"
    user = "mahesh"
    password = "mahesh_123"
    database = "historicaldb"
    
    try:
        db_date = convert_date_to_db_format(date)
        if db_date is None:
            return None
        
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        
        # Get all data for the date
        query = """
        SELECT * FROM nifty_cash 
        WHERE date = %s
        ORDER BY time
        """
        cursor.execute(query, (db_date,))
        results = cursor.fetchall()
        
        if not results:
            return None
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Create DataFrame
        df = pd.DataFrame(results, columns=columns)
        
        # Convert database formats back to readable formats
        if 'date' in df.columns:
            df['date_readable'] = df['date'].apply(convert_db_date_to_readable)
        if 'time' in df.columns:
            df['time_readable'] = df['time'].apply(convert_db_time_to_readable)
        
        return df
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

def resample_ohlc_data(df, interval_minutes):
    """
    Resample 1-minute OHLC data to specified interval
    """
    if df is None or len(df) == 0:
        return None
    
    try:
        # Create datetime index for resampling
        df['datetime'] = pd.to_datetime(df['date_readable'] + ' ' + df['time_readable'])
        df.set_index('datetime', inplace=True)
        
        # Scale down OHLC values by dividing by 100 (convert from paise to rupees)
        df_scaled = df.copy()
        df_scaled['open'] = df['open'] / 100
        df_scaled['high'] = df['high'] / 100
        df_scaled['low'] = df['low'] / 100
        df_scaled['close'] = df['close'] / 100
        
        # Resample data to specified interval
        resampled = df_scaled.resample(f'{interval_minutes}min').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last'
        }).dropna()
        
        # Reset index to get datetime as a column
        resampled.reset_index(inplace=True)
        
        # Format time for display
        resampled['time_readable'] = resampled['datetime'].dt.strftime('%H:%M')
        resampled['date_readable'] = resampled['datetime'].dt.strftime('%Y-%m-%d')
        
        return resampled
        
    except Exception as e:
        print(f"Error resampling data: {e}")
        return None

def create_candlestick_chart_base64(df, date, interval_minutes=1):
    """
    Create a professional candlestick chart with dark theme and return as base64 string
    """
    if df is None or len(df) == 0:
        return None
    
    # Create datetime index for proper time series plotting
    df['datetime'] = pd.to_datetime(df['date_readable'] + ' ' + df['time_readable'])
    df.set_index('datetime', inplace=True)
    
    # Data is already scaled from resampling function
    df_scaled = df.copy()
    
    # Set dark theme style
    plt.style.use('dark_background')
    
    # Set up the plot with dark theme
    fig, ax = plt.subplots(figsize=(16, 9), facecolor='#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    # Plot candlesticks with professional styling
    for i, (idx, row) in enumerate(df_scaled.iterrows()):
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
    if interval_minutes == 1:
        title = f'NIFTY 50 Index • OHLC Candlestick Chart ({date})'
    else:
        title = f'NIFTY 50 Index • {interval_minutes}-Minute OHLC Candlestick Chart ({date})'
    
    ax.set_title(title, fontsize=18, fontweight='bold', color='#ffffff', pad=20)
    ax.set_xlabel('Time', fontsize=14, color='#cccccc', fontweight='bold')
    ax.set_ylabel('Price (INR)', fontsize=14, color='#cccccc', fontweight='bold')
    
    # Professional grid styling
    ax.grid(True, alpha=0.2, color='#444444', linewidth=0.8)
    ax.set_axisbelow(True)
    
    # Set x-axis labels with better formatting
    n_points = len(df)
    if n_points > 20:
        step = max(1, n_points // 15)
        x_ticks = range(0, n_points, step)
        x_labels = [df.index[i].strftime('%H:%M') for i in x_ticks]
    else:
        x_ticks = range(n_points)
        x_labels = [df.index[i].strftime('%H:%M') for i in x_ticks]
    
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels, rotation=45, color='#cccccc', fontsize=11)
    
    # Set y-axis styling
    ax.tick_params(axis='y', colors='#cccccc', labelsize=11)
    
    # Add professional price statistics box
    current_price = df['close'].iloc[-1]
    price_change = current_price - df['open'].iloc[0]
    price_change_pct = (price_change / df['open'].iloc[0]) * 100
    
    stats_text = f"""O {df['open'].iloc[0]:,.2f}
H {df['high'].max():,.2f}
L {df['low'].min():,.2f}
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

def create_summary_chart_base64(df, date):
    """
    Create a professional summary chart with dark theme and return as base64 string
    """
    if df is None or len(df) == 0:
        return None
    
    # Scale down OHLC values by dividing by 100 (convert from paise to rupees)
    df_scaled = df.copy()
    df_scaled['open'] = df['open'] / 100
    df_scaled['high'] = df['high'] / 100
    df_scaled['low'] = df['low'] / 100
    df_scaled['close'] = df['close'] / 100
    
    # Calculate daily OHLC
    daily_open = df_scaled['open'].iloc[0]
    daily_high = df_scaled['high'].max()
    daily_low = df_scaled['low'].min()
    daily_close = df_scaled['close'].iloc[-1]
    
    # Set dark theme style
    plt.style.use('dark_background')
    
    # Create the plot with dark theme
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), facecolor='#1a1a1a')
    fig.patch.set_facecolor('#1a1a1a')
    
    # Plot 1: Price movement throughout the day
    df_scaled['datetime'] = pd.to_datetime(df['date_readable'] + ' ' + df['time_readable'])
    df_scaled.set_index('datetime', inplace=True)
    
    # Set background for both subplots
    ax1.set_facecolor('#1a1a1a')
    ax2.set_facecolor('#1a1a1a')
    
    # Plot 1: Price movement with professional styling
    ax1.plot(df_scaled.index, df_scaled['close'], label='Close Price', linewidth=3, color='#00aaff', alpha=0.9)
    ax1.fill_between(df_scaled.index, df_scaled['low'], df_scaled['high'], alpha=0.2, color='#00aaff', label='High-Low Range')
    ax1.axhline(y=daily_open, color='#00ff88', linestyle='--', linewidth=2, alpha=0.8, 
                label=f'Open: {daily_open:,.2f}')
    ax1.axhline(y=daily_close, color='#ff4444', linestyle='--', linewidth=2, alpha=0.8, 
                label=f'Close: {daily_close:,.2f}')
    
    ax1.set_title(f'NIFTY 50 Index • Daily Price Movement ({date})', 
                  fontsize=16, fontweight='bold', color='#ffffff', pad=20)
    ax1.set_ylabel('Price (INR)', fontsize=13, color='#cccccc', fontweight='bold')
    ax1.legend(framealpha=0.9, facecolor='#2a2a2a', edgecolor='#444444')
    ax1.grid(True, alpha=0.2, color='#444444', linewidth=0.8)
    ax1.set_axisbelow(True)
    
    # Format x-axis with professional styling
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, color='#cccccc', fontsize=10)
    ax1.tick_params(axis='y', colors='#cccccc', labelsize=10)
    
    # Plot 2: OHLC Bar Chart with professional styling
    categories = ['Open', 'High', 'Low', 'Close']
    values = [daily_open, daily_high, daily_low, daily_close]
    colors = ['#00ff88', '#00aaff', '#ffaa00', '#ff4444']  # Professional colors
    
    bars = ax2.bar(categories, values, color=colors, alpha=0.8, edgecolor='#444444', linewidth=1.5)
    ax2.set_title('Daily OHLC Summary', fontsize=16, fontweight='bold', color='#ffffff', pad=20)
    ax2.set_ylabel('Price (INR)', fontsize=13, color='#cccccc', fontweight='bold')
    ax2.grid(True, alpha=0.2, color='#444444', linewidth=0.8)
    ax2.set_axisbelow(True)
    
    # Add value labels on bars with better styling
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{value:,.2f}', ha='center', va='bottom', fontweight='bold', 
                color='#ffffff', fontsize=11)
    
    # Add price change information with professional styling
    price_change = daily_close - daily_open
    price_change_pct = (price_change / daily_open) * 100
    change_color = '#00ff88' if price_change >= 0 else '#ff4444'
    
    change_text = f"Change: {price_change:+,.2f} ({price_change_pct:+.2f}%)"
    bbox_props = dict(boxstyle='round,pad=0.8', facecolor='#2a2a2a', 
                      edgecolor='#444444', alpha=0.9)
    
    ax2.text(0.5, 0.95, change_text, transform=ax2.transAxes, 
             ha='center', va='top', fontsize=12, fontweight='bold',
             bbox=bbox_props, color='#ffffff')
    
    # Style the spines for both subplots
    for ax in [ax1, ax2]:
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
        print(f"Error saving summary chart: {e}")
        return None
    finally:
        plt.close('all')  # Close all figures to prevent memory leaks
        plt.clf()  # Clear current figure
    
    return img_base64

@app.route('/')
def index():
    """Main page with date selection"""
    dates = get_available_dates()
    return render_template('index.html', dates=dates)

@app.route('/generate_chart', methods=['POST'])
def generate_chart():
    """Generate chart based on selected date, chart type, and timeframe"""
    date = request.form.get('date')
    chart_type = request.form.get('chart_type')
    timeframe = request.form.get('timeframe', '1')  # Default to 1 minute if not specified
    
    if not date:
        return jsonify({'error': 'Please select a date'})
    
    # Convert timeframe to integer
    try:
        interval_minutes = int(timeframe)
    except ValueError:
        interval_minutes = 1
    
    df = get_ohlc_data_for_date(date)
    if df is None:
        return jsonify({'error': f'No data found for date: {date}'})
    
    if chart_type == 'candlestick':
        # Resample data to selected timeframe
        df_resampled = resample_ohlc_data(df, interval_minutes)
        if df_resampled is None:
            return jsonify({'error': 'Failed to resample data for selected timeframe'})
        
        chart_base64 = create_candlestick_chart_base64(df_resampled, date, interval_minutes)
        if chart_base64 is None:
            return jsonify({'error': 'Failed to generate candlestick chart'})
            
        if interval_minutes == 1:
            chart_title = f'Candlestick Chart - {date}'
        else:
            chart_title = f'{interval_minutes}-Minute Candlestick Chart - {date}'
        
        # Prepare chart data for interactive chart
        chart_data = []
        for _, row in df_resampled.iterrows():
            chart_data.append({
                'time': row['time_readable'],
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close'])
            })
        
        # Calculate time frame information
        time_frame_info = calculate_time_frame(df_resampled)
        
        return jsonify({
            'success': True,
            'chart_base64': chart_base64,
            'chart_title': chart_title,
            'record_count': len(df_resampled),
            'chart_data': chart_data,
            'time_frame': time_frame_info,
            'timeframe': interval_minutes
        })
        
    elif chart_type == 'summary':
        chart_base64 = create_summary_chart_base64(df, date)
        if chart_base64 is None:
            return jsonify({'error': 'Failed to generate summary chart'})
            
        chart_title = f'Summary Chart - {date}'
        
        # Calculate time frame information for summary charts too
        time_frame_info = calculate_time_frame(df)
        
        return jsonify({
            'success': True,
            'chart_base64': chart_base64,
            'chart_title': chart_title,
            'record_count': len(df),
            'time_frame': time_frame_info
        })
    else:
        return jsonify({'error': 'Invalid chart type'})

@app.route('/get_dates')
def get_dates():
    """API endpoint to get available dates"""
    dates = get_available_dates()
    return jsonify({'dates': dates})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
