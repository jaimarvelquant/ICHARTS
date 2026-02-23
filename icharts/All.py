 
from flask import Flask, render_template, request, jsonify, redirect, url_for
import mysql.connector
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web applications
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches
from datetime import datetime, timedelta
import numpy as np
import math
import io
import base64
import os 

app = Flask(__name__)

# Configure matplotlib for web use
plt.ioff()  # Turn off interactive mode
matplotlib.use('Agg')  # Ensure we use the Agg backend

# Database configuration with enhanced timeout settings
DB_CONFIG = {
    'host': "106.51.63.60",
    'user': "mahesh",
    'password': "mahesh_123",
    'database': "historicaldb",
    'connection_timeout': 30,  # Increased to 30 seconds
    'autocommit': True,
    'charset': 'utf8mb4',
    'use_unicode': True
}

def get_db_connection(max_retries=5):
    """Get database connection with enhanced retry logic"""
    for attempt in range(max_retries):
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            # Test the connection with proper cleanup
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            return connection
        except mysql.connector.Error as e:
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                print("All database connection attempts failed")
                # Return None instead of raising exception for graceful handling
                return None
            import time
            # Progressive backoff: 1s, 2s, 3s, 4s
            time.sleep(attempt + 1)
        except Exception as e:
            print(f"Unexpected error in connection attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                return None
            import time
            time.sleep(attempt + 1)
    return None

def convert_date_to_db_format(date_str):
    """Convert YYYY-MM-DD format to YYMMDD format for database"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%y%m%d')
    except ValueError:
        return None

def convert_db_time_to_readable(seconds):
    """Convert seconds since midnight to HH:MM:SS format"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def convert_db_date_to_readable(date_int):
    """Convert YYMMDD or YYYYMMDD format to YYYY-MM-DD format"""
    try:
        date_str = str(date_int)
        if len(date_str) == 6:
            # YYMMDD format
            year = "20" + date_str[:2]
            month = date_str[2:4]
            day = date_str[4:6]
            return f"{year}-{month}-{day}"
        elif len(date_str) == 8:
            # YYYYMMDD format
            year = date_str[:4]
            month = date_str[4:6]
            day = date_str[6:8]
            return f"{year}-{month}-{day}"
        else:
            # Return as-is if format is not recognized
            return str(date_int)
    except Exception as e:
        print(f"Error converting date {date_int}: {e}")
        return str(date_int)

def calculate_vwap(df):
    """Calculate VWAP (Volume Weighted Average Price) for the given dataframe"""
    try:
        print(f"=== STRADDLE VWAP CALCULATION DEBUG ===")
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {list(df.columns)}")
        print(f"First few rows of straddle_high: {df['straddle_high'].head()}")
        print(f"First few rows of straddle_low: {df['straddle_low'].head()}")
        print(f"First few rows of straddle_close: {df['straddle_close'].head()}")
        
        if df is None or len(df) == 0:
            print("DataFrame is None or empty")
            return None
        
        # Calculate typical price (High + Low + Close) / 3
        df['typical_price'] = (df['straddle_high'] + df['straddle_low'] + df['straddle_close']) / 3
        print(f"Typical price calculated, first few values: {df['typical_price'].head()}")
        
        # Calculate cumulative volume (assuming equal volume for each data point)
        # In real scenarios, you'd have actual volume data
        df['volume'] = 1  # Default volume of 1 for each data point
        
        # Calculate cumulative values
        df['cumulative_tp_volume'] = (df['typical_price'] * df['volume']).cumsum()
        df['cumulative_volume'] = df['volume'].cumsum()
        
        # Calculate VWAP
        df['vwap'] = df['cumulative_tp_volume'] / df['cumulative_volume']
        print(f"VWAP calculated, first few values: {df['vwap'].head()}")
        print(f"VWAP final values shape: {df['vwap'].values.shape}")
        
        return df['vwap'].values
        
    except Exception as e:
        print(f"Error calculating VWAP: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_vwap_regular(df):
    """Calculate VWAP (Volume Weighted Average Price) for regular OHLC data"""
    try:
        print(f"=== VWAP CALCULATION DEBUG ===")
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {list(df.columns)}")
        print(f"First few rows of high: {df['high'].head()}")
        print(f"First few rows of low: {df['low'].head()}")
        print(f"First few rows of close: {df['close'].head()}")
        
        if df is None or len(df) == 0:
            print("DataFrame is None or empty")
            return None
        
        # Calculate typical price (High + Low + Close) / 3
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        print(f"Typical price calculated, first few values: {df['typical_price'].head()}")
        
        # Calculate cumulative volume (assuming equal volume for each data point)
        # In real scenarios, you'd have actual volume data
        df['volume'] = 1  # Default volume of 1 for each data point
        
        # Calculate cumulative values
        df['cumulative_tp_volume'] = (df['typical_price'] * df['volume']).cumsum()
        df['cumulative_volume'] = df['volume'].cumsum()
        
        # Calculate VWAP
        df['vwap'] = df['cumulative_tp_volume'] / df['cumulative_volume']
        print(f"VWAP calculated, first few values: {df['vwap'].head()}")
        print(f"VWAP final values shape: {df['vwap'].values.shape}")
        
        return df['vwap'].values
        
    except Exception as e:
        print(f"Error calculating VWAP: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_ema(df, period=20, price_column='close'):
    """Calculate EMA (Exponential Moving Average) for the given dataframe and period"""
    try:
        print(f"=== EMA {period} CALCULATION DEBUG ===")
        print(f"DataFrame shape: {df.shape}")
        print(f"Price column: {price_column}")
        print(f"First few rows of {price_column}: {df[price_column].head()}")
        
        if df is None or len(df) == 0:
            print("DataFrame is None or empty")
            return None
        
        if len(df) < period:
            print(f"Not enough data points for EMA {period}. Need at least {period} points, got {len(df)}")
            return None
        
        # Calculate the smoothing factor
        alpha = 2.0 / (period + 1)
        print(f"EMA {period} alpha (smoothing factor): {alpha}")
        
        # Initialize EMA with the first value
        ema_values = [df[price_column].iloc[0]]
        
        # Calculate EMA for remaining values
        for i in range(1, len(df)):
            ema = alpha * df[price_column].iloc[i] + (1 - alpha) * ema_values[-1]
            ema_values.append(ema)
        
        print(f"EMA {period} calculated, first few values: {ema_values[:5]}")
        print(f"EMA {period} final values shape: {len(ema_values)}")
        print(f"EMA {period} value range: {min(ema_values):.2f} to {max(ema_values):.2f}")
        
        return ema_values
        
    except Exception as e:
        print(f"Error calculating EMA {period}: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_sma(df, period=20):
    """Calculate Simple Moving Average for the given dataframe"""
    try:
        if df is None or len(df) == 0:
            return None
        
        # Calculate SMA using closing prices
        sma = df['straddle_close'].rolling(window=period).mean()
        return sma.values
        
    except Exception as e:
        print(f"Error calculating SMA: {e}")
        return None


def get_date_range(data_type, symbol='nifty'):
    """Get the actual date range (min and max dates) from the database"""
    try:
        print(f"=== GET_DATE_RANGE DEBUG ===")
        print(f"  data_type: {data_type}")
        print(f"  symbol: {symbol}")
        
        # Check cache first
        cache_key = f"{symbol}_{data_type}"
        if cache_key in _date_range_cache:
            print(f"  returning CACHED date range for {cache_key}")
            return _date_range_cache[cache_key]
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Determine table name based on data type and symbol
        table_map = {
            'nifty': {
                'nifty_cash': 'nifty_cash',
                'nifty_future': 'nifty_future',
                'nifty_call': 'nifty_call',
                'nifty_put': 'nifty_put'
            },
            'banknifty': {
                'banknifty_cash': 'banknifty_cash',
                'banknifty_future': 'banknifty_future',
                'banknifty_call': 'banknifty_call',
                'banknifty_put': 'banknifty_put'
            },
            'midcpnifty': {
                'midcpnifty_cash': 'midcpnifty_cash',
                'midcpnifty_future': 'midcpnifty_future',
                'midcpnifty_call': 'midcpnifty_call',
                'midcpnifty_put': 'midcpnifty_put'
            },
            'sensex': {
                'sensex_cash': 'sensex_cash',
                'sensex_future': 'sensex_future',
                'sensex_call': 'sensex_call',
                'sensex_put': 'sensex_put'
            }
        }
        
        symbol_tables = table_map.get(symbol, table_map['nifty'])
        table_name = symbol_tables.get(data_type, list(symbol_tables.values())[0])
        
        print(f"  selected table_name: {table_name}")
        print(f"  available tables for symbol '{symbol}': {list(symbol_tables.keys())}")
        print(f"  requested data_type: {data_type}")
        
        # Get min and max dates
        query = f"SELECT MIN(date) as min_date, MAX(date) as max_date FROM {table_name}"
        print(f"  executing query: {query}")
        
        # First, let's check if the table exists and has any data
        check_query = f"SELECT COUNT(*) as row_count FROM {table_name}"
        print(f"  checking table existence with: {check_query}")
        cursor.execute(check_query)
        count_result = cursor.fetchone()
        print(f"  table row count: {count_result[0] if count_result else 'None'}")
        
        # Also list all available tables for debugging
        try:
            cursor.execute("SHOW TABLES")
            all_tables = cursor.fetchall()
            table_names = [table[0] for table in all_tables]
            print(f"  Available tables in database: {table_names}")
        except Exception as e:
            print(f"  Error listing tables: {e}")
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        # If no data found, try alternative table names
        if not result or not result[0] or not result[1]:
            print(f"  No data found in {table_name}, trying alternative tables...")
            
            # Try common table name variations
            alternative_tables = [
                f"{symbol}_cash",
                f"{symbol}_future", 
                f"{symbol}_call",
                f"{symbol}_put",
                f"{data_type}",
                "nifty_cash"  # fallback to nifty_cash
            ]
            
            for alt_table in alternative_tables:
                if alt_table == table_name:
                    continue  # Skip the one we already tried
                    
                try:
                    print(f"  Trying alternative table: {alt_table}")
                    alt_query = f"SELECT COUNT(*) as row_count FROM {alt_table}"
                    cursor.execute(alt_query)
                    alt_count = cursor.fetchone()
                    
                    if alt_count and alt_count[0] > 0:
                        print(f"  Found data in {alt_table} with {alt_count[0]} rows")
                        # Use this table instead
                        query = f"SELECT MIN(date) as min_date, MAX(date) as max_date FROM {alt_table}"
                        print(f"  executing alternative query: {query}")
                        cursor.execute(query)
                        result = cursor.fetchone()
                        table_name = alt_table  # Update table name for logging
                        break
                    else:
                        print(f"  No data in {alt_table}")
                except Exception as e:
                    print(f"  Error checking {alt_table}: {e}")
                    continue
        
        if result and result[0] and result[1]:
            min_date = convert_db_date_to_readable(result[0])
            max_date = convert_db_date_to_readable(result[1])
            
            print(f"  raw result: {result}")
            print(f"  min_date_int: {result[0]} -> {min_date}")
            print(f"  max_date_int: {result[1]} -> {max_date}")
            print(f"  date range: {min_date} to {max_date}")
            
            # Validate the converted dates
            try:
                from datetime import datetime
                test_min = datetime.strptime(min_date, '%Y-%m-%d')
                test_max = datetime.strptime(max_date, '%Y-%m-%d')
                print(f"  date validation: PASSED")
            except Exception as e:
                print(f"  date validation: FAILED - {e}")
                return None
            
            date_range_result = {
                'min_date': min_date,
                'max_date': max_date,
                'min_date_int': result[0],
                'max_date_int': result[1]
            }
            
            # Cache the result for future requests
            _date_range_cache[cache_key] = date_range_result
            print(f"  cached date range for {cache_key}")
            
            return date_range_result
        else:
            print(f"  no date range found - result: {result}")
            return None
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

# Simple cache for available dates and date ranges to avoid repeated database calls
_dates_cache = {}
_date_range_cache = {}

def get_available_dates(data_type, symbol='nifty'):
    """Get list of available dates based on data type and symbol"""
    try:
        print(f"=== GET_AVAILABLE_DATES DEBUG ===")
        print(f"  data_type: {data_type}")
        print(f"  symbol: {symbol}")
        
        # Check cache first
        cache_key = f"{symbol}_{data_type}"
        if cache_key in _dates_cache:
            print(f"  returning CACHED dates for {cache_key}: {len(_dates_cache[cache_key])} dates")
            return _dates_cache[cache_key]
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Determine table name based on data type and symbol
        table_map = {
            'nifty': {
                'nifty_cash': 'nifty_cash',
                'nifty_future': 'nifty_future',
                'nifty_call': 'nifty_call',
                'nifty_put': 'nifty_put'
            },
            'banknifty': {
                'banknifty_cash': 'banknifty_cash',
                'banknifty_future': 'banknifty_future',
                'banknifty_call': 'banknifty_call',
                'banknifty_put': 'banknifty_put'
            },
            'midcpnifty': {
                'midcpnifty_cash': 'midcpnifty_cash',
                'midcpnifty_future': 'midcpnifty_future',
                'midcpnifty_call': 'midcpnifty_call',
                'midcpnifty_put': 'midcpnifty_put'
            },
            'sensex': {
                'sensex_cash': 'sensex_cash',
                'sensex_future': 'sensex_future',
                'sensex_call': 'sensex_call',
                'sensex_put': 'sensex_put'
            }
        }
        
        symbol_tables = table_map.get(symbol, table_map['nifty'])
        table_name = symbol_tables.get(data_type, list(symbol_tables.values())[0])
        
        print(f"  symbol_tables: {symbol_tables}")
        print(f"  selected table_name: {table_name}")
        
        # Check if this is options data and handle differently
        is_options_data = data_type.endswith('_call') or data_type.endswith('_put')
        
        # Use optimized query for all data types to improve performance
        # This query is more efficient on large tables with many duplicate dates
        query = f"SELECT DISTINCT date FROM {table_name} WHERE date IS NOT NULL ORDER BY date ASC"
        
        if is_options_data:
            print(f"  executing OPTIMIZED OPTIONS query: {query}")
        else:
            print(f"  executing STANDARD query: {query}")
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"  raw query results: {len(results)} rows")
        
        # Convert to readable dates and ensure uniqueness
        date_set = set()  # Use set to ensure no duplicates
        for row in results:
            date_int = row[0]
            if date_int:  # Skip null dates
                readable_date = convert_db_date_to_readable(date_int)
                date_set.add(readable_date)
        
        # Convert back to sorted list
        dates = sorted(list(date_set))
        
        print(f"  unique dates after processing: {len(dates)}")
        print(f"  first 5 dates: {dates[:5] if dates else 'None'}")
        print(f"  last 5 dates: {dates[-5:] if dates else 'None'}")
        
        if is_options_data:
            print(f"  OPTIONS DATA DEBUG: {data_type}")
            print(f"    Raw results: {len(results)}")
            print(f"    Unique dates: {len(dates)}")
            if len(results) != len(dates):
                print(f"    WARNING: Raw results ({len(results)}) != Unique dates ({len(dates)})")
                print(f"    This suggests duplicate dates in options table")
        
        # Cache the results for future requests
        _dates_cache[cache_key] = dates
        print(f"  cached {len(dates)} dates for {cache_key}")
        
        return dates
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return []
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

def get_available_strikes(date, data_type, symbol='nifty'):
    """Get available strike prices for a given date and data type"""
    try:
        # Check if it's a valid options data type for the given symbol
        valid_options_types = {
            'nifty': ['nifty_call', 'nifty_put'],
            'banknifty': ['banknifty_call', 'banknifty_put'],
            'midcpnifty': ['midcpnifty_call', 'midcpnifty_put'],
            'sensex': ['sensex_call', 'sensex_put']
        }
        
        if symbol not in valid_options_types or data_type not in valid_options_types[symbol]:
            print(f"Invalid options data type '{data_type}' for symbol '{symbol}'")
            return []
        
        connection = get_db_connection()
        cursor = connection.cursor()
        db_date = convert_date_to_db_format(date)
        
        cursor.execute(f"SELECT DISTINCT strike FROM {data_type} WHERE date = %s ORDER BY strike", (db_date,))
        strikes = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        return strikes
        
    except Exception as e:
        print(f"Error getting available strikes: {e}")
        return []

def get_available_expiries(date, data_type, strike, symbol='nifty'):
    """Get available expiry dates for a given date, data type, and strike"""
    try:
        # Check if it's a valid options data type for the given symbol
        valid_options_types = {
            'nifty': ['nifty_call', 'nifty_put'],
            'banknifty': ['banknifty_call', 'banknifty_put'],
            'midcpnifty': ['midcpnifty_call', 'midcpnifty_put'],
            'sensex': ['sensex_call', 'sensex_put']
        }
        
        if symbol not in valid_options_types or data_type not in valid_options_types[symbol]:
            print(f"Invalid options data type '{data_type}' for symbol '{symbol}'")
            return []
        
        connection = get_db_connection()
        cursor = connection.cursor()
        db_date = convert_date_to_db_format(date)
        
        cursor.execute(f"SELECT DISTINCT expiry FROM {data_type} WHERE date = %s AND strike = %s ORDER BY expiry", (db_date, strike))
        expiries = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        return expiries
        
    except Exception as e:
        print(f"Error getting available expiries: {e}")
        return []

def get_ohlc_data_for_date(date, data_type, strike=None, expiry=None, symbol='nifty'):
    """Get OHLC data for a specific date and data type"""
    try:
        db_date = convert_date_to_db_format(date)
        if db_date is None:
            return None
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Determine table name based on data type and symbol
        table_map = {
            'nifty': {
                'nifty_cash': 'nifty_cash',
                'nifty_future': 'nifty_future',
                'nifty_call': 'nifty_call',
                'nifty_put': 'nifty_put'
            },
            'banknifty': {
                'banknifty_cash': 'banknifty_cash',
                'banknifty_future': 'banknifty_future',
                'banknifty_call': 'banknifty_call',
                'banknifty_put': 'banknifty_put'
            },
            'midcpnifty': {
                'midcpnifty_cash': 'midcpnifty_cash',
                'midcpnifty_future': 'midcpnifty_future',
                'midcpnifty_call': 'midcpnifty_call',
                'midcpnifty_put': 'midcpnifty_put'
            },
            'sensex': {
                'sensex_cash': 'sensex_cash',
                'sensex_future': 'sensex_future',
                'sensex_call': 'sensex_call',
                'sensex_put': 'sensex_put'
            }
        }
        
        symbol_tables = table_map.get(symbol, table_map['nifty'])
        table_name = symbol_tables.get(data_type, list(symbol_tables.values())[0])
        
        # For options, include strike and expiry in the query
        if symbol == 'nifty' and data_type in ['nifty_call', 'nifty_put'] and strike and expiry:
            query = f"SELECT * FROM {table_name} WHERE date = %s AND strike = %s AND expiry = %s ORDER BY time"
            cursor.execute(query, (db_date, strike, expiry))
        elif symbol == 'banknifty' and data_type in ['banknifty_call', 'banknifty_put'] and strike and expiry:
            query = f"SELECT * FROM {table_name} WHERE date = %s AND strike = %s AND expiry = %s ORDER BY time"
            cursor.execute(query, (db_date, strike, expiry))
        elif symbol == 'midcpnifty' and data_type in ['midcpnifty_call', 'midcpnifty_put'] and strike and expiry:
            query = f"SELECT * FROM {table_name} WHERE date = %s AND strike = %s AND expiry = %s ORDER BY time"
            cursor.execute(query, (db_date, strike, expiry))
        elif symbol == 'sensex' and data_type in ['sensex_call', 'sensex_put'] and strike and expiry:
            query = f"SELECT * FROM {table_name} WHERE date = %s AND strike = %s AND expiry = %s ORDER BY time"
            cursor.execute(query, (db_date, strike, expiry))
        else:
            query = f"SELECT * FROM {table_name} WHERE date = %s ORDER BY time"
            cursor.execute(query, (db_date,))
        
        results = cursor.fetchall()
        
        if not results:
            return None
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Create DataFrame
        df = pd.DataFrame(results, columns=columns)
        
        # Debug: Print raw database values
        print(f"DEBUG: Raw database values (first 3 rows):")
        if len(df) > 0:
            print(f"  Columns: {list(df.columns)}")
            print(f"  Shape: {df.shape}")
            print(f"  First 3 rows OHLC:")
            for i in range(min(3, len(df))):
                print(f"    Row {i}: Open={df.iloc[i]['open']}, High={df.iloc[i]['high']}, Low={df.iloc[i]['low']}, Close={df.iloc[i]['close']}")
        
        # Filter out records with missing OHLC data and inconsistent values
        if len(df) > 0:
            original_count = len(df)
            # Remove rows where any OHLC value is null or 0
            df = df.dropna(subset=['open', 'high', 'low', 'close'])
            df = df[(df['open'] > 0) & (df['high'] > 0) & (df['low'] > 0) & (df['close'] > 0)]
            
            # Additional filtering: Remove records with unrealistic values (too small or too large)
            # Only apply realistic value filtering for BANKNIFTY data types
            if 'symbol' in df.columns and data_type in ['banknifty_cash', 'banknifty_future']:
                banknifty_mask = df['symbol'] == 'BANKNIFTY'
                if banknifty_mask.any():
                    # For BANKNIFTY, values should be in reasonable range (40,000-70,000 before scaling)
                    realistic_mask = (
                        (df['open'] >= 4000000) & (df['open'] <= 7000000) &
                        (df['high'] >= 4000000) & (df['high'] <= 7000000) &
                        (df['low'] >= 4000000) & (df['low'] <= 7000000) &
                        (df['close'] >= 4000000) & (df['close'] <= 7000000)
                    )
                    df = df[realistic_mask | ~banknifty_mask]
            
            filtered_count = len(df)
            print(f"DEBUG: Filtered data - Original: {original_count}, After filtering: {filtered_count}")
            
            if len(df) == 0:
                print("ERROR: No valid OHLC data after filtering")
                return None
        
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

def calculate_time_frame(df):
    """Calculate time frame information from the data"""
    try:
        print(f"=== CALCULATE_TIME_FRAME DEBUG ===")
        print(f"DataFrame columns: {list(df.columns)}")
        print(f"DataFrame shape: {df.shape}")
        print(f"First few rows:")
        print(df.head(3))
        
        # Get the first and last time entries
        first_time = df['time_readable'].iloc[0]
        last_time = df['time_readable'].iloc[-1]
        
        print(f"First time: {first_time}, Last time: {last_time}")
        
        # Calculate trading duration
        if 'time' in df.columns:
            first_seconds = df['time'].iloc[0]
            last_seconds = df['time'].iloc[-1]
            duration_seconds = last_seconds - first_seconds
            print(f"First seconds: {first_seconds}, Last seconds: {last_seconds}, Duration: {duration_seconds}")
        else:
            print("ERROR: 'time' column not found in DataFrame!")
            print("Available columns:", list(df.columns))
            return {
                'market_open': 'N/A',
                'market_close': 'N/A',
                'trading_duration': 'N/A',
                'data_intervals': 'N/A'
            }
        
        # Convert duration to hours and minutes
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        
        # Format duration
        if hours > 0:
            duration_str = f"{hours}h {minutes}m"
        else:
            duration_str = f"{minutes}m"
        
        # Calculate data intervals
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

def resample_ohlc_data(df, interval_minutes, data_type='nifty_cash'):
    """Resample 1-minute OHLC data to specified interval"""
    if df is None or len(df) == 0:
        return None
    
    try:
        # Use a simpler, battle-tested path for NIFTY spot data to avoid
        # complex filtering issues and ensure reliable resampling
        if data_type == 'nifty_cash':
            print(f"DEBUG: Using simple resampling path for nifty_cash ({len(df)} records, interval {interval_minutes}min)")
            df_simple = df.copy()
            df_simple['datetime'] = pd.to_datetime(df_simple['date_readable'] + ' ' + df_simple['time_readable'])
            df_simple.set_index('datetime', inplace=True)
            
            df_scaled = df_simple.copy()
            df_scaled['open'] = df_simple['open'] / 100
            df_scaled['high'] = df_simple['high'] / 100
            df_scaled['low'] = df_simple['low'] / 100
            df_scaled['close'] = df_simple['close'] / 100
            
            resampled = df_scaled.resample(f'{interval_minutes}min').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last'
            }).dropna()
            
            if len(resampled) == 0:
                print("DEBUG: Simple resampling produced no data for nifty_cash")
                return None
            
            resampled.reset_index(inplace=True)
            resampled['time_readable'] = resampled['datetime'].dt.strftime('%H:%M')
            resampled['date_readable'] = resampled['datetime'].dt.strftime('%Y-%m-%d')
            resampled['time'] = resampled['datetime'].dt.hour * 3600 + resampled['datetime'].dt.minute * 60
            
            print(f"DEBUG: Simple resampling for nifty_cash successful: {len(resampled)} records")
            return resampled

        print(f"DEBUG: Resampling {len(df)} records to {interval_minutes}-minute intervals")
        
        # Create datetime index for resampling
        df['datetime'] = pd.to_datetime(df['date_readable'] + ' ' + df['time_readable'])
        df.set_index('datetime', inplace=True)
        
        print(f"DEBUG: Original time range: {df.index[0]} to {df.index[-1]}")
        
        # Debug: Print original values before scaling
        print(f"DEBUG: Original OHLC values (first 5 rows):")
        print(f"  Open: {df['open'].head().tolist()}")
        print(f"  High: {df['high'].head().tolist()}")
        print(f"  Low: {df['low'].head().tolist()}")
        print(f"  Close: {df['close'].head().tolist()}")
        
        # Scale down OHLC values by dividing by 100 (convert from paise to rupees)
        df_scaled = df.copy()
        
        if data_type in ['nifty_call', 'nifty_put', 'banknifty_call', 'banknifty_put', 'midcpnifty_call', 'midcpnifty_put', 'sensex_call', 'sensex_put']:
            sample_values = df['open'].head(5).tolist()
            print(f"DEBUG: Options sample values: {sample_values}")
            if all(val < 1000 for val in sample_values):
                print("DEBUG: Options data already in rupees, no scaling needed")
                df_scaled['open'] = df['open']
                df_scaled['high'] = df['high']
                df_scaled['low'] = df['low']
                df_scaled['close'] = df['close']
            else:
                print("DEBUG: Options data in paise, scaling by 100")
                df_scaled['open'] = df['open'] / 100
                df_scaled['high'] = df['high'] / 100
                df_scaled['low'] = df['low'] / 100
                df_scaled['close'] = df['close'] / 100
        else:
            print("DEBUG: Cash/Future data scaling by 100")
            df_scaled['open'] = df['open'] / 100
            df_scaled['high'] = df['high'] / 100
            df_scaled['low'] = df['low'] / 100
            df_scaled['close'] = df['close'] / 100
        
        # Debug: Print scaling results
        print(f"DEBUG: Scaling results (first 3 rows):")
        print(f"  Original Open: {df['open'].head(3).tolist()}")
        print(f"  Scaled Open: {df_scaled['open'].head(3).tolist()}")
        print(f"  Original High: {df['high'].head(3).tolist()}")
        print(f"  Scaled High: {df_scaled['high'].head(3).tolist()}")
        print(f"  Original Low: {df['low'].head(3).tolist()}")
        print(f"  Scaled Low: {df_scaled['low'].head(3).tolist()}")
        print(f"  Original Close: {df['close'].head(3).tolist()}")
        print(f"  Scaled Close: {df_scaled['close'].head(3).tolist()}")
        
        # For options data, filter out unrealistic small values that are likely data errors
        if data_type in ['nifty_call', 'nifty_put', 'banknifty_call', 'banknifty_put', 'midcpnifty_call', 'midcpnifty_put', 'sensex_call', 'sensex_put']:
            print(f"DEBUG: Filtering unrealistic values for options data...")
            original_count = len(df_scaled)
            
            # For options, use flexible range based on actual data values
            all_values = pd.concat([df_scaled['open'], df_scaled['high'], df_scaled['low'], df_scaled['close']])
            min_val = all_values.min()
            max_val = all_values.max()
            
            print(f"DEBUG: Options data range - min: {min_val}, max: {max_val}")
            
            # Use flexible thresholds that work for both small and large option values
            # Check if data is consistently large or small, not mixed
            if max_val > 1000 and min_val > 100:  # All values are large (like call data)
                # For large option values (like 3800+), use broader range
                lower_limit = 0.01
                upper_limit = max(10000, max_val * 1.5)  # At least 10000, or 1.5x max value
                print(f"DEBUG: Using large options range ({lower_limit} to {upper_limit})")
            elif max_val < 1000 and min_val > 0.1:  # All values are small (like put data)
                # For small option values, use normal range
                lower_limit = 0.01
                upper_limit = 1000
                print(f"DEBUG: Using small options range ({lower_limit} to {upper_limit})")
            else:
                # Mixed data or edge cases - use very permissive range
                lower_limit = 0.01
                upper_limit = max(10000, max_val * 2)  # Very permissive
                print(f"DEBUG: Using mixed/permissive options range ({lower_limit} to {upper_limit})")
            
            valid_mask = (
                (df_scaled['open'] >= lower_limit) & (df_scaled['open'] <= upper_limit) &
                (df_scaled['high'] >= lower_limit) & (df_scaled['high'] <= upper_limit) &
                (df_scaled['low'] >= lower_limit) & (df_scaled['low'] <= upper_limit) &
                (df_scaled['close'] >= lower_limit) & (df_scaled['close'] <= upper_limit)
            )
            
            df_scaled = df_scaled[valid_mask]
            filtered_count = len(df_scaled)
            print(f"DEBUG: Options data filtering - Original: {original_count}, After filtering: {filtered_count}")
            
            if len(df_scaled) == 0:
                print("ERROR: No valid options data after filtering unrealistic values")
                return None
            
            # Debug: Print filtered values
            print(f"DEBUG: Filtered OHLC values (first 5 rows):")
            print(f"  Open: {df_scaled['open'].head().tolist()}")
            print(f"  High: {df_scaled['high'].head().tolist()}")
            print(f"  Low: {df_scaled['low'].head().tolist()}")
            print(f"  Close: {df_scaled['close'].head().tolist()}")
        
        # Debug: Print scaled values after scaling
        print(f"DEBUG: Scaled OHLC values (first 5 rows):")
        print(f"  Open: {df_scaled['open'].head().tolist()}")
        print(f"  High: {df_scaled['high'].head().tolist()}")
        print(f"  Low: {df_scaled['low'].head().tolist()}")
        print(f"  Close: {df_scaled['close'].head().tolist()}")
        
        # Additional filtering: Remove records with unrealistic values after scaling
        print(f"DEBUG: Additional filtering after scaling...")
        original_scaled_count = len(df_scaled)
        
        # Only apply BANKNIFTY-specific filtering for BANKNIFTY data types
        if 'symbol' in df_scaled.columns and data_type in ['banknifty_cash', 'banknifty_future']:
            banknifty_mask = df_scaled['symbol'] == 'BANKNIFTY'
            if banknifty_mask.any():
                # Filter out records with unrealistic values after scaling
                realistic_mask = (
                    (df_scaled['open'] >= 40000) & (df_scaled['open'] <= 70000) &
                    (df_scaled['high'] >= 40000) & (df_scaled['high'] <= 70000) &
                    (df_scaled['low'] >= 40000) & (df_scaled['low'] <= 70000) &
                    (df_scaled['close'] >= 40000) & (df_scaled['close'] <= 70000)
                )
                df_scaled = df_scaled[realistic_mask | ~banknifty_mask]
                print(f"DEBUG: After scaling filter - Original: {original_scaled_count}, Filtered: {len(df_scaled)}")
        
        # Resample data to specified interval using simple and correct aggregation
        print(f"DEBUG: Using resampling rule: '{interval_minutes}min'")
        
        # Filter out records with mixed data before resampling
        # Separate logic for options data vs cash/future data
        if len(df_scaled) > 0:
            if data_type in ['nifty_call', 'nifty_put', 'banknifty_call', 'banknifty_put', 'midcpnifty_call', 'midcpnifty_put', 'sensex_call', 'sensex_put']:
                # ===== OPTIONS DATA LOGIC (CALL/PUT) =====
                print("DEBUG: Applying OPTIONS data filtering logic")
                
                # Check for mixed data by looking at the range of values
                all_values = pd.concat([df_scaled['open'], df_scaled['high'], df_scaled['low'], df_scaled['close']])
                min_val = all_values.min()
                max_val = all_values.max()
                
                # Use the same flexible range logic as in the initial filtering
                if max_val > 1000 and min_val > 100:  # All values are large (like call data)
                    # For large option values (like 1800+), use broader range
                    lower_limit = 0.01
                    upper_limit = max(10000, max_val * 1.5)  # At least 10000, or 1.5x max value
                    print(f"DEBUG: Using large options range for mixed data filtering ({lower_limit} to {upper_limit})")
                elif max_val < 1000 and min_val > 0.1:  # All values are small (like put data)
                    # For small option values, use normal range
                    lower_limit = 0.01
                    upper_limit = 1000
                    print(f"DEBUG: Using small options range for mixed data filtering ({lower_limit} to {upper_limit})")
                else:
                    # Mixed data or edge cases - use very permissive range
                    lower_limit = 0.01
                    upper_limit = max(10000, max_val * 2)  # Very permissive
                    print(f"DEBUG: Using mixed/permissive options range for mixed data filtering ({lower_limit} to {upper_limit})")
                
                valid_mask = (
                    (df_scaled['open'] >= lower_limit) & (df_scaled['open'] <= upper_limit) &
                    (df_scaled['high'] >= lower_limit) & (df_scaled['high'] <= upper_limit) &
                    (df_scaled['low'] >= lower_limit) & (df_scaled['low'] <= upper_limit) &
                    (df_scaled['close'] >= lower_limit) & (df_scaled['close'] <= upper_limit)
                )
            else:
                # ===== CASH/FUTURE DATA LOGIC (SPOT/FUTURE) =====
                print("DEBUG: Applying CASH/FUTURE data filtering logic")
                
                # For cash/future data, after scaling by 100, values should be in hundreds range
                # Original values are in thousands (18000-19000), after /100 they become 180-190
                valid_mask = (
                    (df_scaled['open'] >= 100) & (df_scaled['open'] <= 10000) &
                    (df_scaled['high'] >= 100) & (df_scaled['high'] <= 10000) &
                    (df_scaled['low'] >= 100) & (df_scaled['low'] <= 10000) &
                    (df_scaled['close'] >= 100) & (df_scaled['close'] <= 10000)
                )
                print("DEBUG: Using cash/future range (100-10000) for scaled data")
            
            df_scaled = df_scaled[valid_mask]
            print(f"DEBUG: Filtered mixed data - kept {len(df_scaled)} records out of original")
            
            if len(df_scaled) == 0:
                print("ERROR: No valid data after filtering mixed values")
                return None
        
        try:
            # For options data, use more careful resampling to avoid picking wrong values
            if data_type in ['nifty_call', 'nifty_put', 'banknifty_call', 'banknifty_put', 'midcpnifty_call', 'midcpnifty_put', 'sensex_call', 'sensex_put']:
                print("DEBUG: Using options-specific resampling logic")
                # Filter out obviously wrong values (like 1) before resampling
                df_clean = df_scaled.copy()
                # Remove records where all OHLC values are 1 (likely data errors)
                invalid_mask = (df_clean['open'] == 1) & (df_clean['high'] == 1) & (df_clean['low'] == 1) & (df_clean['close'] == 1)
                df_clean = df_clean[~invalid_mask]
                print(f"DEBUG: Removed {invalid_mask.sum()} invalid records (all values = 1)")
                
                resampled = df_clean.resample(f'{interval_minutes}min').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last'
                }).dropna()
                print(f"DEBUG: Options resampling successful: {len(resampled)} records")
            else:
                # Use standard resampling for cash/future data
                resampled = df_scaled.resample(f'{interval_minutes}min').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last'
                }).dropna()
                print(f"DEBUG: Standard resampling successful: {len(resampled)} records")
        except Exception as e:
            print(f"DEBUG: Resampling failed: {e}")
            # Fallback: manual resampling with simple aggregation
            df_scaled['time_group'] = df_scaled.index.floor(f'{interval_minutes}min')
            
            def simple_group_agg(group):
                result = {}
                for col in ['open', 'high', 'low', 'close']:
                    if col in group.columns:
                        if col == 'open':
                            result[col] = group[col].iloc[0]
                        elif col == 'high':
                            result[col] = group[col].max()
                        elif col == 'low':
                            result[col] = group[col].min()
                        elif col == 'close':
                            result[col] = group[col].iloc[-1]
                return pd.Series(result)
            
            resampled = df_scaled.groupby('time_group').apply(simple_group_agg).dropna()
            print(f"DEBUG: Manual resampling successful: {len(resampled)} records")
        
        # After resampling, filter out any remaining mixed data
        if len(resampled) > 0:
            # Separate filtering logic for options vs cash/future data
            if data_type in ['nifty_call', 'nifty_put', 'banknifty_call', 'banknifty_put', 'midcpnifty_call', 'midcpnifty_put', 'sensex_call', 'sensex_put']:
                # ===== OPTIONS DATA LOGIC (CALL/PUT) =====
                print("DEBUG: Applying OPTIONS data filtering after resampling")
                print(f"DEBUG: Before filtering - resampled values:")
                print(f"  Open: {resampled['open'].head().tolist()}")
                print(f"  High: {resampled['high'].head().tolist()}")
                print(f"  Low: {resampled['low'].head().tolist()}")
                print(f"  Close: {resampled['close'].head().tolist()}")
                
                # For options data, use flexible thresholds based on actual values
                all_resampled_values = pd.concat([resampled['open'], resampled['high'], resampled['low'], resampled['close']])
                min_resampled = all_resampled_values.min()
                max_resampled = all_resampled_values.max()
                
                print(f"DEBUG: Resampled options range - min: {min_resampled}, max: {max_resampled}")
                
                if max_resampled > 1000 and min_resampled > 100:  # All values are large (like call data)
                    # For large option values, use broader range
                    lower_limit = 0.01
                    upper_limit = max(10000, max_resampled * 1.5)
                    print(f"DEBUG: Using large resampled options range ({lower_limit} to {upper_limit})")
                elif max_resampled < 1000 and min_resampled > 0.1:  # All values are small (like put data)
                    # For small option values, use normal range
                    lower_limit = 0.01
                    upper_limit = 1000
                    print(f"DEBUG: Using small resampled options range ({lower_limit} to {upper_limit})")
                else:
                    # Mixed data or edge cases - use very permissive range
                    lower_limit = 0.01
                    upper_limit = max(10000, max_resampled * 2)  # Very permissive
                    print(f"DEBUG: Using mixed/permissive resampled options range ({lower_limit} to {upper_limit})")
                
                valid_mask = (
                    (resampled['open'] >= lower_limit) & (resampled['open'] <= upper_limit) &
                    (resampled['high'] >= lower_limit) & (resampled['high'] <= upper_limit) &
                    (resampled['low'] >= lower_limit) & (resampled['low'] <= upper_limit) &
                    (resampled['close'] >= lower_limit) & (resampled['close'] <= upper_limit)
                )
                resampled = resampled[valid_mask]
                print(f"DEBUG: After filtering options resampled data - kept {len(resampled)} records")
                print(f"DEBUG: After filtering - resampled values:")
                print(f"  Open: {resampled['open'].head().tolist()}")
                print(f"  High: {resampled['high'].head().tolist()}")
                print(f"  Low: {resampled['low'].head().tolist()}")
                print(f"  Close: {resampled['close'].head().tolist()}")
            else:
                # ===== CASH/FUTURE DATA LOGIC (SPOT/FUTURE) =====
                print("DEBUG: Applying CASH/FUTURE data filtering after resampling")
                # Check for mixed data in resampled results (after scaling by 100)
                has_large_values = (resampled['open'] > 1000).any() or (resampled['high'] > 1000).any()
                has_small_values = (resampled['low'] < 100).any() or (resampled['close'] < 100).any()
                
                if has_large_values and has_small_values:
                    print("WARNING: Mixed data detected in resampled results - filtering out small values")
                    # Keep only records where all values are in the hundreds range (after scaling)
                    valid_mask = (
                        (resampled['open'] >= 100) & (resampled['open'] <= 10000) &
                        (resampled['high'] >= 100) & (resampled['high'] <= 10000) &
                        (resampled['low'] >= 100) & (resampled['low'] <= 10000) &
                        (resampled['close'] >= 100) & (resampled['close'] <= 10000)
                    )
                    resampled = resampled[valid_mask]
                    print(f"DEBUG: After filtering mixed resampled data - kept {len(resampled)} records")
        
        # Debug: Print resampled values
        if len(resampled) > 0:
            print(f"DEBUG: Resampled OHLC values (first 5 rows):")
            print(f"  Open: {resampled['open'].head().tolist()}")
            print(f"  High: {resampled['high'].head().tolist()}")
            print(f"  Low: {resampled['low'].head().tolist()}")
            print(f"  Close: {resampled['close'].head().tolist()}")
            
            # Debug: Check for 12:05:00 specifically
            if 'time_readable' in resampled.columns:
                time_12_05 = resampled[resampled['time_readable'] == '12:05']
                if len(time_12_05) > 0:
                    row = time_12_05.iloc[0]
                    print(f"DEBUG: 12:05:00 specific values:")
                    print(f"  Open: {row['open']}")
                    print(f"  High: {row['high']}")
                    print(f"  Low: {row['low']}")
                    print(f"  Close: {row['close']}")
                else:
                    print("DEBUG: No 12:05:00 data found in resampled data")
        
        if len(resampled) == 0:
            if interval_minutes == 1 and len(df_scaled) > 0:
                print("DEBUG: No data after resampling, using original scaled data for 1-minute interval")
                resampled = df_scaled.copy()
            else:
                print("DEBUG: No data after resampling!")
                return None
            
        # Reset index to get datetime as a column
        resampled.reset_index(inplace=True)
        
        # Format time for display
        # Check what the datetime column is named after reset_index
        datetime_col = None
        for col in resampled.columns:
            if 'datetime' in col.lower() or resampled[col].dtype.name.startswith('datetime'):
                datetime_col = col
                break
        
        if datetime_col is None:
            print(f"DEBUG: Available columns after reset_index: {list(resampled.columns)}")
            print("ERROR: Could not find datetime column after resampling")
            return None
        
        print(f"DEBUG: Using datetime column: {datetime_col}")
        
        resampled['time_readable'] = resampled[datetime_col].dt.strftime('%H:%M')
        resampled['date_readable'] = resampled[datetime_col].dt.strftime('%Y-%m-%d')
        
        # Add the missing 'time' column (seconds since midnight) for calculate_time_frame function
        resampled['time'] = resampled[datetime_col].dt.hour * 3600 + resampled[datetime_col].dt.minute * 60
        
        print(f"DEBUG: Resampled time range: {resampled['time_readable'].iloc[0]} to {resampled['time_readable'].iloc[-1]}")
        print(f"DEBUG: Sample times: {resampled['time_readable'].head(5).tolist()}")
        print(f"DEBUG: Added 'time' column with values: {resampled['time'].head(5).tolist()}")
        
        return resampled
        
    except Exception as e:
        print(f"Error resampling data: {e}")
        import traceback
        traceback.print_exc()
        return None

def resample_straddle_data(df, interval_minutes):
    """Resample straddle data to specified interval"""
    if df is None or len(df) == 0:
        return None
    
    if interval_minutes == 1:
        return df
    
    try:
        print(f"DEBUG: Resampling straddle data {len(df)} records to {interval_minutes}-minute intervals")
        
        # Create datetime index for resampling
        df['datetime'] = pd.to_datetime(df['date_readable'] + ' ' + df['time_readable'])
        df.set_index('datetime', inplace=True)
        
        print(f"DEBUG: Original time range: {df.index[0]} to {df.index[-1]}")
        
        # Resample data to specified interval
        print(f"DEBUG: Using resampling rule: '{interval_minutes}min'")
        try:
            # First try the standard approach
            resampled = df.resample(f'{interval_minutes}min').agg({
                'straddle_open': 'first',
                'straddle_high': 'max',
                'straddle_low': 'min',
                'straddle_close': 'last',
                'call_open': 'first',
                'call_high': 'max',
                'call_low': 'min',
                'call_close': 'last',
                'put_open': 'first',
                'put_high': 'max',
                'put_low': 'min',
                'put_close': 'last'
            }).dropna()
            print(f"DEBUG: Standard resampling successful: {len(resampled)} records")
        except Exception as e:
            print(f"DEBUG: Standard resampling failed: {e}")
            # Fallback: manual resampling
            df['time_group'] = df.index.floor(f'{interval_minutes}min')
            resampled = df.groupby('time_group').agg({
                'straddle_open': 'first',
                'straddle_high': 'max',
                'straddle_low': 'min',
                'straddle_close': 'last',
                'call_open': 'first',
                'call_high': 'max',
                'call_low': 'min',
                'call_close': 'last',
                'put_open': 'first',
                'put_high': 'max',
                'put_low': 'min',
                'put_close': 'last'
            }).dropna()
            print(f"DEBUG: Manual resampling successful: {len(resampled)} records")
        
        if len(resampled) == 0:
            print("DEBUG: No data after resampling!")
            return None
            
        # Reset index to get datetime as a column
        resampled.reset_index(inplace=True)
        
        # Format time for display
        # Check what the datetime column is named after reset_index
        datetime_col = None
        for col in resampled.columns:
            if 'datetime' in col.lower() or resampled[col].dtype.name.startswith('datetime'):
                datetime_col = col
                break
        
        if datetime_col is None:
            print(f"DEBUG: Available columns after reset_index: {list(resampled.columns)}")
            print("ERROR: Could not find datetime column after resampling")
            return None
        
        print(f"DEBUG: Using datetime column: {datetime_col}")
        
        resampled['time_readable'] = resampled[datetime_col].dt.strftime('%H:%M')
        resampled['date_readable'] = resampled[datetime_col].dt.strftime('%Y-%m-%d')
        
        # Add the missing 'time' column (seconds since midnight) for calculate_time_frame function
        resampled['time'] = resampled[datetime_col].dt.hour * 3600 + resampled[datetime_col].dt.minute * 60
        
        print(f"DEBUG: Resampled time range: {resampled['time_readable'].iloc[0]} to {resampled['time_readable'].iloc[-1]}")
        print(f"DEBUG: Sample times: {resampled['time_readable'].head(5).tolist()}")
        print(f"DEBUG: Added 'time' column with values: {resampled['time'].head(5).tolist()}")
        
        return resampled
        
    except Exception as e:
        print(f"Error resampling straddle data: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_candlestick_chart_base64(df, date, interval_minutes, data_type, symbol='nifty', indicators=None):
    """Create a professional candlestick chart and return as base64 string"""
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
    
    # Color scheme based on data type
    color_schemes = {
        'nifty_cash': {'bull': '#00ff88', 'bear': '#ff4444', 'edge_bull': '#00cc66', 'edge_bear': '#cc3333'},
        'nifty_future': {'bull': '#00ff88', 'bear': '#ff4444', 'edge_bull': '#00cc66', 'edge_bear': '#cc3333'},
        'nifty_call': {'bull': '#00ff88', 'bear': '#ff4444', 'edge_bull': '#00cc66', 'edge_bear': '#cc3333'},
        'nifty_put': {'bull': '#00ff88', 'bear': '#ff4444', 'edge_bull': '#00cc66', 'edge_bear': '#cc3333'}
    }
    
    colors = color_schemes.get(data_type, color_schemes['nifty_cash'])
    
    # Debug: Print values being used in chart
    print(f"DEBUG: Chart values (first 5 rows):")
    for i, (idx, row) in enumerate(df_scaled.head().iterrows()):
        print(f"  Row {i}: Open={row['open']}, High={row['high']}, Low={row['low']}, Close={row['close']}")
    
    # Debug: Check for contaminated data in the entire dataset
    print(f"DEBUG: Checking for contaminated data in entire dataset:")
    
    # Use flexible thresholds based on actual data values
    all_values = pd.concat([df_scaled['open'], df_scaled['high'], df_scaled['low'], df_scaled['close']])
    min_val = all_values.min()
    max_val = all_values.max()
    
    print(f"  Data range - min: {min_val}, max: {max_val}")
    
    if data_type in ['nifty_call', 'nifty_put', 'banknifty_call', 'banknifty_put', 'midcpnifty_call', 'midcpnifty_put', 'sensex_call', 'sensex_put']:
        # For options data, use flexible range based on actual values
        if max_val > 1000 and min_val > 100:  # All values are large (like call data)
            min_price_threshold = 0.01
            max_price_threshold = max(10000, max_val * 1.5)
            print(f"  Using large options thresholds: {min_price_threshold} to {max_price_threshold}")
        elif max_val < 1000 and min_val > 0.1:  # All values are small (like put data)
            min_price_threshold = 0.01
            max_price_threshold = 1000
            print(f"  Using small options thresholds: {min_price_threshold} to {max_price_threshold}")
        else:
            # Mixed data or edge cases - use very permissive range
            min_price_threshold = 0.01
            max_price_threshold = max(10000, max_val * 2)  # Very permissive
            print(f"  Using mixed/permissive options thresholds: {min_price_threshold} to {max_price_threshold}")
    else:
        # For cash/future data, use higher thresholds
        min_price_threshold = 1000
        max_price_threshold = 1000000
        print(f"  Using cash/future thresholds: {min_price_threshold} to {max_price_threshold}")
    
    # Filter out contaminated data before plotting
    print(f"DEBUG: Filtering contaminated data before plotting...")
    original_count = len(df_scaled)
    df_scaled = df_scaled[(df_scaled['low'] >= min_price_threshold) & (df_scaled['close'] >= min_price_threshold) & 
                         (df_scaled['low'] <= max_price_threshold) & (df_scaled['close'] <= max_price_threshold)]
    filtered_count = len(df_scaled)
    print(f"  Original records: {original_count}, After filtering: {filtered_count}")
    
    if len(df_scaled) == 0:
        print("ERROR: No valid data left after filtering contaminated values")
        return None
    
    # Plot candlesticks
    print(f"DEBUG: Plotting {len(df_scaled)} candlesticks...")
    for i, (idx, row) in enumerate(df_scaled.iterrows()):
        open_price = row['open']
        close_price = row['close']
        high_price = row['high']
        low_price = row['low']
        
        # Debug: Print first few candlestick dimensions
        if i < 5:
            print(f"  Candlestick {i}: O={open_price:.2f}, H={high_price:.2f}, L={low_price:.2f}, C={close_price:.2f}")
            print(f"    Body height: {abs(close_price - open_price):.2f}, Body bottom: {min(open_price, close_price):.2f}")
            print(f"    Wick range: {low_price:.2f} to {high_price:.2f}")
        
        if close_price >= open_price:
            color = colors['bull']
            edge_color = colors['edge_bull']
            wick_color = colors['bull']
        else:
            color = colors['bear']
            edge_color = colors['edge_bear']
            wick_color = colors['bear']
        
        # Plot the wick (vertical line from low to high)
        ax.plot([i, i], [low_price, high_price], color=wick_color, linewidth=3, alpha=0.9, solid_capstyle='round')
        
        # Plot the body
        body_height = abs(close_price - open_price)
        body_bottom = min(open_price, close_price)
        
        if body_height > 0:
            # Use rectangle for better visibility
            from matplotlib.patches import Rectangle
            rect = Rectangle((i - 0.3, body_bottom), 0.6, body_height, 
                           facecolor=color, edgecolor=edge_color, linewidth=2, alpha=0.9)
            ax.add_patch(rect)
        else:
            # Doji (when open = close) - horizontal line
            ax.plot([i-0.3, i+0.3], [open_price, open_price], color=edge_color, linewidth=4, alpha=0.9)
    
            # Customize the plot with user-friendly names
        display_names = {
            'nifty_cash': 'Spot',
            'nifty_future': 'Future',
            'nifty_call': 'Call',
            'nifty_put': 'Put'
        }
        data_type_display = display_names.get(data_type, data_type.replace('_', ' ').title())
        
        symbol_display = symbol.upper() # For displaying NIFTY or BANKNIFTY
        
        if interval_minutes == 1:
            title = f'{symbol_display} Index • OHLC Candlestick Chart ({date}) - {data_type_display}'
        else:
            title = f'{symbol_display} Index • {interval_minutes}-Minute OHLC Candlestick Chart ({date}) - {data_type_display}'
    
    ax.set_title(title, fontsize=18, fontweight='bold', color='#ffffff', pad=20)
    ax.set_xlabel('Time', fontsize=14, color='#cccccc', fontweight='bold')
    ax.set_ylabel('Price (INR)', fontsize=14, color='#cccccc', fontweight='bold')
    
    # Grid and styling
    ax.grid(True, alpha=0.2, color='#444444', linewidth=0.8)
    ax.set_axisbelow(True)
    
    # Set x-axis labels
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
    
    # Adjust y-axis limits to show proper candlestick range
    if len(df_scaled) > 0:
        all_prices = []
        for _, row in df_scaled.iterrows():
            all_prices.extend([row['open'], row['high'], row['low'], row['close']])
        
        if all_prices:
            min_price = min(all_prices)
            max_price = max(all_prices)
            price_range = max_price - min_price
            
            # Add some padding and ensure minimum range for visibility
            # For options data, use smaller padding since prices are typically small
            if data_type in ['nifty_call', 'nifty_put', 'banknifty_call', 'banknifty_put', 'midcpnifty_call', 'midcpnifty_put', 'sensex_call', 'sensex_put']:
                padding = max(price_range * 0.1, 0.5)  # 10% padding or minimum 0.5 points for options
            else:
                padding = max(price_range * 0.1, 50)  # 10% padding or minimum 50 points for cash/future
            y_min = min_price - padding
            y_max = max_price + padding
            
            ax.set_ylim(y_min, y_max)
            print(f"DEBUG: Set y-axis limits: {y_min:.2f} to {y_max:.2f} (range: {price_range:.2f})")
    
    # Add price statistics box
    current_price = df_scaled['close'].iloc[-1]
    price_change = current_price - df_scaled['open'].iloc[0]
    price_change_pct = (price_change / df_scaled['open'].iloc[0]) * 100
    
    stats_text = f"""O {df_scaled['open'].iloc[0]:,.2f}
H {df_scaled['high'].max():,.2f}
L {df_scaled['low'].min():,.2f}
C {current_price:,.2f}
{price_change:+.2f} ({price_change_pct:+.2f}%)"""
    
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
    
    # Plot indicators if specified
    print(f"=== INDICATORS DEBUG ===")
    print(f"Indicators received: {indicators}")
    print(f"Indicators type: {type(indicators)}")
    
    if indicators:
        print(f"Processing {len(indicators)} indicators")
        for indicator in indicators:
            print(f"Processing indicator: {indicator}")
            if indicator == 'vwap':
                print("VWAP indicator detected, calculating...")
                vwap_values = calculate_vwap_regular(df)
                print(f"VWAP values returned: {vwap_values is not None}")
                if vwap_values is not None:
                    print(f"Plotting VWAP line with {len(vwap_values)} points")
                    ax.plot(range(len(vwap_values)), vwap_values, color='#ff6b6b', linewidth=2, 
                           label='VWAP', alpha=0.8)
                    print("VWAP line plotted successfully")
                else:
                    print("VWAP values are None, not plotting")
            elif indicator == 'ema_20':
                print("EMA 20 indicator detected, calculating...")
                ema_20_values = calculate_ema(df, period=20, price_column='close')
                print(f"EMA 20 values returned: {ema_20_values is not None}")
                if ema_20_values is not None:
                    print(f"Plotting EMA 20 line with {len(ema_20_values)} points")
                    ax.plot(range(len(ema_20_values)), ema_20_values, color='#ff6b35', linewidth=2, 
                           label='EMA (Close, 20)', alpha=0.8)
                    print("EMA 20 line plotted successfully")
                else:
                    print("EMA 20 values are None, not plotting")
            
            elif indicator == 'ema_50':
                print("EMA 50 indicator detected, calculating...")
                ema_50_values = calculate_ema(df, period=50, price_column='close')
                print(f"EMA 50 values returned: {ema_50_values is not None}")
                if ema_50_values is not None:
                    print(f"Plotting EMA 50 line with {len(ema_50_values)} points")
                    ax.plot(range(len(ema_50_values)), ema_50_values, color='#4ecdc4', linewidth=2, 
                           label='EMA (Close, 50)', alpha=0.8)
                    print("EMA 50 line plotted successfully")
                else:
                    print("EMA 50 values are None, not plotting")
            
            elif indicator == 'ema_100':
                print("EMA 100 indicator detected, calculating...")
                ema_100_values = calculate_ema(df, period=100, price_column='close')
                print(f"EMA 100 values returned: {ema_100_values is not None}")
                if ema_100_values is not None:
                    print(f"Plotting EMA 100 line with {len(ema_100_values)} points")
                    ax.plot(range(len(ema_100_values)), ema_100_values, color='#9b59b6', linewidth=2, 
                           label='EMA (Close, 100)', alpha=0.8)
                    print("EMA 100 line plotted successfully")
                else:
                    print("EMA 100 values are None, not plotting")
            
            elif indicator == 'ema_200':
                print("EMA 200 indicator detected, calculating...")
                ema_200_values = calculate_ema(df, period=200, price_column='close')
                print(f"EMA 200 values returned: {ema_200_values is not None}")
                if ema_200_values is not None:
                    print(f"Plotting EMA 200 line with {len(ema_200_values)} points")
                    ax.plot(range(len(ema_200_values)), ema_200_values, color='#e74c3c', linewidth=2, 
                           label='EMA (Close, 200)', alpha=0.8)
                    print("EMA 200 line plotted successfully")
                else:
                    print("EMA 200 values are None, not plotting")
            else:
                print(f"Unknown indicator: {indicator}")
        
        # Add legend for indicators
        ax.legend(loc='upper left', fontsize=10, framealpha=0.8, 
                 facecolor='#2a2a2a', edgecolor='#444444')
        print("Legend added for indicators")
    else:
        print("No indicators received")
    
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
        plt.close('all')
        plt.clf()
    
    return img_base64

def create_summary_chart_base64(df, date, data_type, symbol='nifty'):
    """Create a professional summary chart and return as base64 string"""
    if df is None or len(df) == 0:
        return None
    
    # Scale down OHLC values
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
    
    # Color scheme based on data type
    color_schemes = {
        'nifty_cash': {'line': '#00ff88', 'fill': '#00ff88', 'open': '#00ff88', 'close': '#ff4444'},
        'nifty_future': {'line': '#00ccff', 'fill': '#00ccff', 'open': '#00ff88', 'close': '#ff4444'},
        'nifty_call': {'line': '#00ff88', 'fill': '#00ff88', 'open': '#00ff88', 'close': '#ff4444'},
        'nifty_put': {'line': '#ff8800', 'fill': '#ff8800', 'open': '#00ff88', 'close': '#ff4444'}
    }
    
    colors = color_schemes.get(data_type, color_schemes['nifty_cash'])
    
    # Set background for both subplots
    ax1.set_facecolor('#1a1a1a')
    ax2.set_facecolor('#1a1a1a')
    
    # Plot 1: Price movement
    df_scaled['datetime'] = pd.to_datetime(df['date_readable'] + ' ' + df['time_readable'])
    df_scaled.set_index('datetime', inplace=True)
    
    # Use user-friendly names for labels and title
    display_names = {
        'nifty_cash': 'Spot',
        'nifty_future': 'Future',
        'nifty_call': 'Call',
        'nifty_put': 'Put',
        'banknifty_cash': 'Spot',
        'banknifty_future': 'Future',
        'banknifty_call': 'Call',
        'banknifty_put': 'Put'
    }
    data_type_display = display_names.get(data_type, data_type.replace('_', ' ').title())
    
    symbol_display = symbol.upper() # For displaying NIFTY or BANKNIFTY
    
    ax1.plot(df_scaled.index, df_scaled['close'], label=f'{data_type_display} Close Price',
            linewidth=3, color=colors['line'], alpha=0.9)
    
    ax1.fill_between(df_scaled.index, df_scaled['low'], df_scaled['high'], alpha=0.2, color=colors['fill'], label='High-Low Range')
    ax1.axhline(y=daily_open, color=colors['open'], linestyle='--', linewidth=2, alpha=0.8, 
                label=f'Open: {daily_open:,.2f}')
    ax1.axhline(y=daily_close, color=colors['close'], linestyle='--', linewidth=2, alpha=0.8, 
                label=f'Close: {daily_close:,.2f}')
    
    title = f'{symbol_display} Index • Daily Price Movement ({date}) - {data_type_display}'
    
    ax1.set_title(title, fontsize=16, fontweight='bold', color='#ffffff', pad=20)
    ax1.set_ylabel('Price (INR)', fontsize=13, color='#cccccc', fontweight='bold')
    ax1.legend(framealpha=0.9, facecolor='#2a2a2a', edgecolor='#444444')
    ax1.grid(True, alpha=0.2, color='#444444', linewidth=0.8)
    ax1.set_axisbelow(True)
    
    # Format x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, color='#cccccc', fontsize=10)
    ax1.tick_params(axis='y', colors='#cccccc', labelsize=10)
    
    # Plot 2: OHLC Bar Chart
    categories = ['Open', 'High', 'Low', 'Close']
    values = [daily_open, daily_high, daily_low, daily_close]
    bar_colors = [colors['open'], colors['line'], '#ffaa00', colors['close']]
    
    bars = ax2.bar(categories, values, color=bar_colors, alpha=0.8, edgecolor='#444444', linewidth=1.5)
    ax2.set_title(f'Daily OHLC Summary - {data_type_display}', fontsize=16, fontweight='bold', color='#ffffff', pad=20)
    ax2.set_ylabel('Price (INR)', fontsize=13, color='#cccccc', fontweight='bold')
    ax2.grid(True, alpha=0.2, color='#444444', linewidth=0.8)
    ax2.set_axisbelow(True)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{value:,.2f}', ha='center', va='bottom', fontweight='bold', 
                color='#ffffff', fontsize=11)
    
    # Add price change information
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
        plt.close('all')
        plt.clf()
    
    return img_base64

@app.route('/')
def main_index():
    """Main landing page with chart type selection"""
    return render_template('main_index.html')

@app.route('/symbol_selection')
def symbol_selection():
    """Symbol selection page for single chart analysis"""
    return render_template('symbol_selection.html')

@app.route('/single_chart')
def single_chart():
    """Single chart analysis page with data type selection and date selection"""
    symbol = request.args.get('symbol', 'nifty')
    data_type = request.args.get('data_type', '')
    
    print(f"=== SINGLE CHART DEBUG ===")
    print(f"  Requested symbol: {symbol}")
    print(f"  Requested data_type: {data_type}")
    
    # Determine data types based on symbol
    if symbol == 'nifty':
        data_types = ['nifty_cash', 'nifty_future', 'nifty_call', 'nifty_put']
        if not data_type or not data_type.startswith('nifty_'):
            data_type = 'nifty_cash'
    elif symbol == 'banknifty':
        data_types = ['banknifty_cash', 'banknifty_future', 'banknifty_call', 'banknifty_put']
        if not data_type or not data_type.startswith('banknifty_'):
            data_type = 'banknifty_cash'
    elif symbol == 'midcpnifty':
        data_types = ['midcpnifty_cash', 'midcpnifty_future', 'midcpnifty_call', 'midcpnifty_put']
        if not data_type or not data_type.startswith('midcpnifty_'):
            data_type = 'midcpnifty_cash'
    elif symbol == 'sensex':
        data_types = ['sensex_cash', 'sensex_future', 'sensex_call', 'sensex_put']
        if not data_type or not data_type.startswith('sensex_'):
            data_type = 'sensex_cash'
    else:
        # Default to nifty
        symbol = 'nifty'
        data_types = ['nifty_cash', 'nifty_future', 'nifty_call', 'nifty_put']
        data_type = 'nifty_cash'
    
    print(f"  Final symbol: {symbol}")
    print(f"  Final data_types: {data_types}")
    print(f"  Final selected_data_type: {data_type}")
    
    return render_template('all_index.html', 
                         symbol=symbol,
                         selected_symbol=symbol,
                         data_types=data_types,
                         selected_data_type=data_type)

@app.route('/change_data_type')
def change_data_type():
    """Change data type and redirect to single chart page"""
    symbol = request.args.get('symbol', 'nifty')
    data_type = request.args.get('data_type', 'nifty_cash')
    return redirect(url_for('single_chart', symbol=symbol, data_type=data_type))

@app.route('/generate_chart', methods=['POST'])
def generate_chart():
    """Generate chart based on selected parameters"""
    date = request.form.get('date')
    chart_type = request.form.get('chart_type')
    timeframe = request.form.get('timeframe', '1')
    data_type = request.form.get('data_type', 'nifty_cash')
    strike = request.form.get('strike')
    expiry = request.form.get('expiry')
    
    # Get indicators from form data
    indicators = request.form.getlist('indicators') if request.form.get('indicators') else []
    print(f"=== ROUTE DEBUG ===")
    print(f"Form data indicators: {request.form.getlist('indicators')}")
    print(f"Form data indicators (get): {request.form.get('indicators')}")
    print(f"Final indicators list: {indicators}")
    print(f"Indicators type: {type(indicators)}")
    print(f"Indicators length: {len(indicators)}")
    
    # Get symbol from form data, fallback to determining from data type
    symbol = request.form.get('symbol', '')
    if not symbol:
        if data_type.startswith('banknifty_'):
            symbol = 'banknifty'
        elif data_type.startswith('midcpnifty_'):
            symbol = 'midcpnifty'
        elif data_type.startswith('sensex_'):
            symbol = 'sensex'
        else:
            symbol = 'nifty'
    
    print(f"=== CHART GENERATION DEBUG ===")
    print(f"Received parameters:")
    print(f"  date: {date}")
    print(f"  chart_type: {chart_type}")
    print(f"  timeframe: '{timeframe}' (type: {type(timeframe)})")
    print(f"  data_type: {data_type}")
    print(f"  strike: {strike}")
    print(f"  expiry: {expiry}")

    
    if not date:
        return jsonify({'error': 'Please select a date'})
    
    # For options, validate strike and expiry
    if data_type in ['nifty_call', 'nifty_put', 'banknifty_call', 'banknifty_put', 'midcpnifty_call', 'midcpnifty_put', 'sensex_call', 'sensex_put']:
        if not strike:
            return jsonify({'error': 'Please select a strike price for options'})
        if not expiry:
            return jsonify({'error': 'Please select an expiry date for options'})
    
    # Convert timeframe to integer
    try:
        interval_minutes = int(timeframe)
        print(f"Converted timeframe '{timeframe}' to interval_minutes: {interval_minutes}")
    except ValueError:
        interval_minutes = 1
        print(f"Failed to convert timeframe '{timeframe}', using default: {interval_minutes}")
    
    df = get_ohlc_data_for_date(date, data_type, strike, expiry, symbol)
    if df is None:
        error_msg = f'No data found for date: {date} and data type: {data_type}'
        if data_type in ['nifty_call', 'nifty_put'] or data_type in ['banknifty_call', 'banknifty_put']:
            error_msg += f', strike: {strike}, expiry: {expiry}'
        return jsonify({'error': error_msg})
    
    if chart_type == 'candlestick':
        print(f"Processing candlestick chart with interval_minutes: {interval_minutes}")
        
        # Resample data to selected timeframe
        df_resampled = resample_ohlc_data(df, interval_minutes, data_type)
        if df_resampled is None:
            return jsonify({'error': 'Failed to resample data for selected timeframe'})
        
        print(f"Resampling completed. Original records: {len(df)}, Resampled records: {len(df_resampled)}")
        
        chart_base64 = create_candlestick_chart_base64(df_resampled, date, interval_minutes, data_type, symbol, indicators)
        if chart_base64 is None:
            return jsonify({'error': 'Failed to generate candlestick chart'})
            
        # Use user-friendly names for chart titles
        display_names = {
            'nifty_cash': 'Spot',
            'nifty_future': 'Future',
            'nifty_call': 'Call',
            'nifty_put': 'Put',
            'banknifty_cash': 'Spot',
            'banknifty_future': 'Future',
            'banknifty_call': 'Call',
            'banknifty_put': 'Put',
            'midcpnifty_cash': 'Spot',
            'midcpnifty_future': 'Future',
            'midcpnifty_call': 'Call',
            'midcpnifty_put': 'Put',
            'sensex_cash': 'Spot',
            'sensex_future': 'Future',
            'sensex_call': 'Call',
            'sensex_put': 'Put'
        }
        data_type_display = display_names.get(data_type, data_type.replace('_', ' ').title())
        if interval_minutes == 1:
            chart_title = f'Candlestick Chart - {date} ({data_type_display})'
        else:
            chart_title = f'{interval_minutes}-Minute Candlestick Chart - {date} ({data_type_display})'
        
        print(f"Generated chart title: '{chart_title}'")
        
        # Filter out contaminated data before preparing interactive chart data
        print(f"DEBUG: Filtering contaminated data for interactive chart...")
        original_count = len(df_resampled)
        
        # Use flexible thresholds based on actual data values
        all_values = pd.concat([df_resampled['open'], df_resampled['high'], df_resampled['low'], df_resampled['close']])
        min_val = all_values.min()
        max_val = all_values.max()
        
        if data_type in ['nifty_call', 'nifty_put', 'banknifty_call', 'banknifty_put', 'midcpnifty_call', 'midcpnifty_put', 'sensex_call', 'sensex_put']:
            # For options data, use flexible range based on actual values
            if max_val > 1000 and min_val > 100:  # All values are large (like call data)
                min_price_threshold = 0.01
                max_price_threshold = max(10000, max_val * 1.5)
            elif max_val < 1000 and min_val > 0.1:  # All values are small (like put data)
                min_price_threshold = 0.01
                max_price_threshold = 1000
            else:
                # Mixed data or edge cases - use very permissive range
                min_price_threshold = 0.01
                max_price_threshold = max(10000, max_val * 2)  # Very permissive
        else:
            min_price_threshold = max(0.01, min_val * 0.5)
            max_price_threshold = max_val * 1.5
        
        df_resampled_clean = df_resampled[(df_resampled['low'] >= min_price_threshold) & (df_resampled['close'] >= min_price_threshold) & 
                                         (df_resampled['low'] <= max_price_threshold) & (df_resampled['close'] <= max_price_threshold)]
        filtered_count = len(df_resampled_clean)
        print(f"  Original records: {original_count}, After filtering: {filtered_count}")
        
        if len(df_resampled_clean) == 0:
            return jsonify({'error': 'No valid data available for chart generation'})
        
        # Prepare chart data for interactive chart
        chart_data = []
        for _, row in df_resampled_clean.iterrows():
            chart_data.append({
                'time': row['time_readable'],
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close'])
            })
        
        # Calculate time frame information
        time_frame_info = calculate_time_frame(df_resampled_clean)
        
        print(f"Returning response with timeframe: {interval_minutes}")
        
        return jsonify({
            'success': True,
            'chart_base64': chart_base64,
            'chart_title': chart_title,
            'record_count': len(df_resampled_clean),
            'chart_data': chart_data,
            'time_frame': time_frame_info,
            'data_source': data_type,
            'timeframe': interval_minutes
        })
        
    elif chart_type == 'summary':
        chart_base64 = create_summary_chart_base64(df, date, data_type, symbol)
        if chart_base64 is None:
            return jsonify({'error': 'Failed to generate summary chart'})
            
        # Use user-friendly names for chart titles
        display_names = {
            'nifty_cash': 'Spot',
            'nifty_future': 'Future',
            'nifty_call': 'Call',
            'nifty_put': 'Put',
            'banknifty_cash': 'Spot',
            'banknifty_future': 'Future',
            'banknifty_call': 'Call',
            'banknifty_put': 'Put',
            'midcpnifty_cash': 'Spot',
            'midcpnifty_future': 'Future',
            'midcpnifty_call': 'Call',
            'midcpnifty_put': 'Put',
            'sensex_cash': 'Spot',
            'sensex_future': 'Future',
            'sensex_call': 'Call',
            'sensex_put': 'Put'
        }
        data_type_display = display_names.get(data_type, data_type.replace('_', ' ').title())
        chart_title = f'Summary Chart - {date} ({data_type_display})'
        
        # Calculate time frame information for summary charts too
        time_frame_info = calculate_time_frame(df)
        
        return jsonify({
            'success': True,
            'chart_base64': chart_base64,
            'chart_title': chart_title,
            'record_count': len(df),
            'time_frame': time_frame_info,
            'data_source': data_type
        })
    else:
        return jsonify({'error': 'Invalid chart type'})

@app.route('/get_date_range')
def get_date_range_route():
    """API endpoint to get the date range for a specific data type and symbol"""
    data_type = request.args.get('data_type', 'nifty_cash')
    symbol = request.args.get('symbol', 'nifty')
    print(f"=== GET_DATE_RANGE_ROUTE DEBUG ===")
    print(f"  data_type: {data_type}")
    print(f"  symbol: {symbol}")
    
    date_range = get_date_range(data_type, symbol)
    print(f"  date_range result: {date_range}")
    
    if date_range is None:
        print(f"  WARNING: date_range is None, returning error response")
        return jsonify({'error': 'No date range found for the specified data type and symbol'})
    
    return jsonify({'date_range': date_range})

@app.route('/get_dates')
def get_dates():
    """API endpoint to get available dates for a specific data type"""
    data_type = request.args.get('data_type', 'nifty_cash')
    symbol = request.args.get('symbol', 'nifty')
    dates = get_available_dates(data_type, symbol)
    return jsonify({'dates': dates})

@app.route('/get_strikes')
def get_strikes():
    """API endpoint to get available strikes for a date and data type"""
    date = request.args.get('date')
    data_type = request.args.get('data_type')
    symbol = request.args.get('symbol', 'nifty')
    
    if not date or not data_type:
        return jsonify({'error': 'Date and data type are required'})
    
    strikes = get_available_strikes(date, data_type, symbol)
    return jsonify({'strikes': strikes})

@app.route('/get_expiries')
def get_expiries():
    """API endpoint to get available expiries for a date, data type, and strike"""
    date = request.args.get('date')
    data_type = request.args.get('data_type')
    strike = request.args.get('strike')
    symbol = request.args.get('symbol', 'nifty')
    
    if not date or not data_type or not strike:
        return jsonify({'error': 'Date, data type, and strike are required'})
    
    expiries = get_available_expiries(date, data_type, float(strike), symbol)
    return jsonify({'expiries': expiries})

@app.route('/test')
def test():
    """Test route to verify Flask is working"""
    return "Flask is working! This is a test route from All.py"

@app.route('/debug_tables')
def debug_tables():
    """Debug endpoint to check available tables and their data"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        all_tables = cursor.fetchall()
        table_names = [table[0] for table in all_tables]
        
        # Check each table for data
        table_info = {}
        for table_name in table_names:
            try:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                
                # Get date range if table has a date column
                try:
                    cursor.execute(f"SELECT MIN(date) as min_date, MAX(date) as max_date FROM {table_name}")
                    date_result = cursor.fetchone()
                    if date_result and date_result[0] and date_result[1]:
                        min_date = convert_db_date_to_readable(date_result[0])
                        max_date = convert_db_date_to_readable(date_result[1])
                        table_info[table_name] = {
                            'row_count': count,
                            'min_date': min_date,
                            'max_date': max_date,
                            'min_date_int': date_result[0],
                            'max_date_int': date_result[1]
                        }
                    else:
                        table_info[table_name] = {
                            'row_count': count,
                            'date_range': 'No date data'
                        }
                except:
                    table_info[table_name] = {
                        'row_count': count,
                        'date_range': 'No date column'
                    }
            except Exception as e:
                table_info[table_name] = {'error': str(e)}
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'available_tables': table_names,
            'table_info': table_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/test_expiry_data')
def test_expiry_data():
    """Test endpoint to check what expiry data is available"""
    date = request.args.get('date', '2025-08-14')
    symbol = request.args.get('symbol', 'nifty')
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        db_date = convert_date_to_db_format(date)
        
        # Check what data is available for this date
        table_map = {
            'nifty': {
                'call_table': 'nifty_call',
                'put_table': 'nifty_put'
            }
        }
        
        symbol_tables = table_map.get(symbol, table_map['nifty'])
        call_table = symbol_tables['call_table']
        put_table = symbol_tables['put_table']
        
        # Get all expiries for the date
        cursor.execute(f"SELECT DISTINCT expiry FROM {call_table} WHERE date = %s ORDER BY expiry", (db_date,))
        call_expiries = [row[0] for row in cursor.fetchall()]
        
        cursor.execute(f"SELECT DISTINCT expiry FROM {put_table} WHERE date = %s ORDER BY expiry", (db_date,))
        put_expiries = [row[0] for row in cursor.fetchall()]
        
        # Get some sample strikes
        cursor.execute(f"SELECT DISTINCT strike FROM {call_table} WHERE date = %s ORDER BY strike LIMIT 10", (db_date,))
        sample_strikes = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'date': date,
            'db_date': db_date,
            'call_expiries': call_expiries,
            'put_expiries': put_expiries,
            'sample_strikes': sample_strikes
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/debug_dates')
def debug_dates():
    """Debug endpoint to check what dates are available"""
    data_type = request.args.get('data_type', 'nifty_call')
    symbol = request.args.get('symbol', 'nifty')
    
    try:
        print(f"=== DEBUG_DATES ===")
        print(f"data_type: {data_type}")
        print(f"symbol: {symbol}")
        
        dates = get_available_dates(data_type, symbol)
        print(f"Returned dates: {dates}")
        print(f"Number of dates: {len(dates)}")
        if dates:
            print(f"First date: {dates[0]}")
            print(f"Last date: {dates[-1]}")
        
        return jsonify({
            'data_type': data_type,
            'symbol': symbol,
            'dates': dates,
            'count': len(dates),
            'first_date': dates[0] if dates else None,
            'last_date': dates[-1] if dates else None
        })
        
    except Exception as e:
        print(f"Error in debug_dates: {e}")
        return jsonify({'error': str(e)})

@app.route('/debug_straddle_dates')
def debug_straddle_dates():
    """Debug endpoint specifically for straddle chart dates"""
    try:
        print(f"=== DEBUG_STRADDLE_DATES ===")
        
        # Test different data types for nifty
        call_dates = get_available_dates('nifty_call', 'nifty')
        put_dates = get_available_dates('nifty_put', 'nifty')
        cash_dates = get_available_dates('nifty_cash', 'nifty')
        
        print(f"Call dates count: {len(call_dates)}")
        print(f"Put dates count: {len(put_dates)}")
        print(f"Cash dates count: {len(cash_dates)}")
        
        if call_dates:
            print(f"Call first date: {call_dates[0]}")
            print(f"Call last date: {call_dates[-1]}")
        
        if put_dates:
            print(f"Put first date: {put_dates[0]}")
            print(f"Put last date: {put_dates[-1]}")
        
        if cash_dates:
            print(f"Cash first date: {cash_dates[0]}")
            print(f"Cash last date: {cash_dates[-1]}")
        
        return jsonify({
            'call_dates': {
                'count': len(call_dates),
                'first_date': call_dates[0] if call_dates else None,
                'last_date': call_dates[-1] if call_dates else None
            },
            'put_dates': {
                'count': len(put_dates),
                'first_date': put_dates[0] if put_dates else None,
                'last_date': put_dates[-1] if put_dates else None
            },
            'cash_dates': {
                'count': len(cash_dates),
                'first_date': cash_dates[0] if cash_dates else None,
                'last_date': cash_dates[-1] if cash_dates else None
            }
        })
        
    except Exception as e:
        print(f"Error in debug_straddle_dates: {e}")
        return jsonify({'error': str(e)})

@app.route('/straddle_chart')
def straddle_chart():
    """Straddle chart analysis page with symbol, date, strike, and expiry selection"""
    return render_template('straddle_index.html')

@app.route('/options_chain')
def options_chain():
    """Options chain analysis page showing all available strikes and expiries"""
    return render_template('options_chain_index.html')

@app.route('/get_straddle_strikes')
def get_straddle_strikes():
    """Get available call and put strikes for a specific date and symbol"""
    date = request.args.get('date')
    symbol = request.args.get('symbol', 'nifty')
    
    if not date:
        return jsonify({'error': 'Date is required'})
    
    try:
        # Determine table names based on symbol
        table_map = {
            'nifty': {
                'call_table': 'nifty_call',
                'put_table': 'nifty_put'
            },
            'banknifty': {
                'call_table': 'banknifty_call',
                'put_table': 'banknifty_put'
            },
            'midcpnifty': {
                'call_table': 'midcpnifty_call',
                'put_table': 'midcpnifty_put'
            },
            'sensex': {
                'call_table': 'sensex_call',
                'put_table': 'sensex_put'
            }
        }
        
        symbol_tables = table_map.get(symbol, table_map['nifty'])
        call_table = symbol_tables['call_table']
        put_table = symbol_tables['put_table']
        
        connection = get_db_connection()
        cursor = connection.cursor()
        db_date = convert_date_to_db_format(date)
        
        # Get call strikes
        cursor.execute(f"SELECT DISTINCT strike FROM {call_table} WHERE date = %s ORDER BY strike", (db_date,))
        call_strikes = [float(row[0]) for row in cursor.fetchall()]
        
        # Get put strikes
        cursor.execute(f"SELECT DISTINCT strike FROM {put_table} WHERE date = %s ORDER BY strike", (db_date,))
        put_strikes = [float(row[0]) for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'call_strikes': call_strikes,
            'put_strikes': put_strikes
        })
        
    except Exception as e:
        print(f"Error getting straddle strikes: {e}")
        return jsonify({'error': str(e)})

@app.route('/get_straddle_expiries')
def get_straddle_expiries():
    """Get available expiry dates for call and put strikes on a specific date"""
    date = request.args.get('date')
    call_strike = request.args.get('call_strike')
    put_strike = request.args.get('put_strike')
    symbol = request.args.get('symbol', 'nifty')
    
    print(f"=== GET_STRADDLE_EXPIRIES DEBUG ===")
    print(f"Received parameters:")
    print(f"  date: {date}")
    print(f"  call_strike: {call_strike}")
    print(f"  put_strike: {put_strike}")
    print(f"  symbol: {symbol}")
    
    if not date or not call_strike or not put_strike:
        print("Missing required parameters")
        return jsonify({'error': 'Date, call strike, and put strike are required'})
    
    try:
        # Convert strikes to float
        call_strike = float(call_strike)
        put_strike = float(put_strike)
        
        # Determine table names based on symbol
        table_map = {
            'nifty': {
                'call_table': 'nifty_call',
                'put_table': 'nifty_put'
            },
            'banknifty': {
                'call_table': 'banknifty_call',
                'put_table': 'banknifty_put'
            },
            'midcpnifty': {
                'call_table': 'midcpnifty_call',
                'put_table': 'midcpnifty_put'
            },
            'sensex': {
                'call_table': 'sensex_call',
                'put_table': 'sensex_put'
            }
        }
        
        symbol_tables = table_map.get(symbol, table_map['nifty'])
        call_table = symbol_tables['call_table']
        put_table = symbol_tables['put_table']
        
        print(f"Using tables: {call_table}, {put_table}")
        
        connection = get_db_connection()
        cursor = connection.cursor()
        db_date = convert_date_to_db_format(date)
        
        print(f"Database date format: {db_date}")
        
        # Get call expiries for the selected strike
        call_query = f"SELECT DISTINCT expiry FROM {call_table} WHERE date = %s AND strike = %s ORDER BY expiry"
        print(f"Call query: {call_query} with params: {db_date}, {call_strike}")
        cursor.execute(call_query, (db_date, call_strike))
        call_expiries = [row[0] for row in cursor.fetchall()]
        print(f"Call expiries found: {call_expiries}")
        
        # Get put expiries for the selected strike
        put_query = f"SELECT DISTINCT expiry FROM {put_table} WHERE date = %s AND strike = %s ORDER BY expiry"
        print(f"Put query: {put_query} with params: {db_date}, {put_strike}")
        cursor.execute(put_query, (db_date, put_strike))
        put_expiries = [row[0] for row in cursor.fetchall()]
        print(f"Put expiries found: {put_expiries}")
        
        cursor.close()
        connection.close()
        
        # Find common expiries (both call and put should have the same expiry for straddle)
        common_expiries = list(set(call_expiries) & set(put_expiries))
        common_expiries.sort()
        
        print(f"Common expiries: {common_expiries}")
        
        # If no common expiries, try a more flexible approach
        if not common_expiries:
            print("No common expiries found, trying alternative approach...")
            # Get all expiries for the date regardless of strike
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            # Get all expiries for the date
            all_expiries_query = f"SELECT DISTINCT expiry FROM {call_table} WHERE date = %s ORDER BY expiry"
            cursor.execute(all_expiries_query, (db_date,))
            all_expiries = [row[0] for row in cursor.fetchall()]
            print(f"All expiries for date: {all_expiries}")
            
            cursor.close()
            connection.close()
            
            # Use all available expiries as fallback
            common_expiries = all_expiries
        
        return jsonify({
            'call_expiries': call_expiries,
            'put_expiries': put_expiries,
            'common_expiries': common_expiries
        })
        
    except Exception as e:
        print(f"Error getting straddle expiries: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)})

@app.route('/get_straddle_dates')
def get_straddle_dates():
    """API endpoint to get available dates for straddle strategy (intersection of call and put)"""
    symbol = request.args.get('symbol', 'nifty')
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Use our optimized get_available_dates function instead of direct queries
        call_data_type = f'{symbol}_call'
        put_data_type = f'{symbol}_put'
        
        print(f"Getting call dates using optimized function...")
        call_dates_readable = get_available_dates(call_data_type, symbol)
        print(f"Getting put dates using optimized function...")
        put_dates_readable = get_available_dates(put_data_type, symbol)
        
        # Convert readable dates back to sets for intersection
        call_dates_set = set(call_dates_readable)
        put_dates_set = set(put_dates_readable)
        
        # Find intersection dates (where both call and put data exist)
        intersection_dates_set = call_dates_set.intersection(put_dates_set)
        readable_dates = sorted(list(intersection_dates_set))
        
        print(f"Call dates: {len(call_dates_readable)}, Put dates: {len(put_dates_readable)}, Intersection: {len(readable_dates)}")
        
        cursor.close()
        connection.close()
        
        print(f"=== STRADDLE_DATES_DEBUG ===")
        print(f"Symbol: {symbol}")
        print(f"Call dates count: {len(call_dates_readable)}")
        print(f"Put dates count: {len(put_dates_readable)}")
        print(f"Intersection dates count: {len(readable_dates)}")
        
        return jsonify({
            'dates': readable_dates,
            'call_dates_count': len(call_dates_readable),
            'put_dates_count': len(put_dates_readable),
            'intersection_dates_count': len(readable_dates)
        })
        
    except Exception as e:
        print(f"Error in get_straddle_dates: {e}")
        return jsonify({'error': str(e)})

@app.route('/generate_straddle_chart', methods=['POST'])
def generate_straddle_chart():
    """Generate straddle chart based on selected parameters"""
    date = request.form.get('date')
    symbol = request.form.get('symbol', 'nifty')
    call_strike = request.form.get('callStrike')  # Fixed: match HTML form field name
    put_strike = request.form.get('putStrike')    # Fixed: match HTML form field name
    expiry = request.form.get('expiry')
    timeframe = request.form.get('timeframe', '1')  # Get timeframe parameter
    
    print(f"=== STRADDLE CHART GENERATION DEBUG ===")
    print(f"Received parameters:")
    print(f"  date: {date}")
    print(f"  symbol: {symbol}")
    print(f"  call_strike: {call_strike} (type: {type(call_strike)})")
    print(f"  put_strike: {put_strike} (type: {type(put_strike)})")
    print(f"  expiry: {expiry} (type: {type(expiry)})")
    print(f"  timeframe: '{timeframe}' (type: {type(timeframe)})")
    
    # Convert strikes to float if they're strings
    try:
        call_strike = float(call_strike) if call_strike else None
        put_strike = float(put_strike) if put_strike else None
        print(f"Converted strikes - call: {call_strike}, put: {put_strike}")
    except ValueError as e:
        print(f"Error converting strikes to float: {e}")
        return jsonify({'error': 'Invalid strike price format'})
    
    # Convert timeframe to integer
    try:
        interval_minutes = int(timeframe)
        print(f"Converted timeframe '{timeframe}' to interval_minutes: {interval_minutes}")
    except ValueError:
        interval_minutes = 1
        print(f"Failed to convert timeframe '{timeframe}', using default: {interval_minutes}")
    
    # Validate timeframe
    if interval_minutes < 1 or interval_minutes > 60:
        interval_minutes = 1
        print(f"Timeframe {interval_minutes} out of range, using default: 1")
    
    if not all([date, call_strike, put_strike, expiry]):
        return jsonify({'error': 'All parameters are required'})
    
    try:
        # Determine table names based on symbol
        table_map = {
            'nifty': {
                'call_table': 'nifty_call',
                'put_table': 'nifty_put'
            },
            'banknifty': {
                'call_table': 'banknifty_call',
                'put_table': 'banknifty_put'
            },
            'midcpnifty': {
                'call_table': 'midcpnifty_call',
                'put_table': 'midcpnifty_put'
            },
            'sensex': {
                'call_table': 'sensex_call',
                'put_table': 'sensex_put'
            }
        }
        
        symbol_tables = table_map.get(symbol, table_map['nifty'])
        call_table = symbol_tables['call_table']
        put_table = symbol_tables['put_table']
        
        # Get call data
        print(f"Getting call data for table: {call_table}, strike: {call_strike}, expiry: {expiry}")
        call_df = get_ohlc_data_for_date(date, call_table, call_strike, expiry, symbol)
        if call_df is None:
            print(f"No call data found for strike {call_strike} and expiry {expiry}")
            return jsonify({
                'error': f'No call data found for strike {call_strike} and expiry {expiry} on {date}. '
                        f'Please try a different strike price or expiry date that has available data.'
            })
        print(f"Call data retrieved: {len(call_df)} records")
        
        # Get put data
        print(f"Getting put data for table: {put_table}, strike: {put_strike}, expiry: {expiry}")
        put_df = get_ohlc_data_for_date(date, put_table, put_strike, expiry, symbol)
        if put_df is None:
            print(f"No put data found for strike {put_strike} and expiry {expiry}")
            return jsonify({
                'error': f'No put data found for strike {put_strike} and expiry {expiry} on {date}. '
                        f'Please try a different strike price or expiry date that has available data.'
            })
        print(f"Put data retrieved: {len(put_df)} records")
        
        # Create straddle data by combining call and put prices
        print("Creating straddle data...")
        straddle_df = create_straddle_data(call_df, put_df, call_strike, put_strike)
        if straddle_df is None:
            print("Failed to create straddle data")
            return jsonify({
                'error': f'Unable to combine call and put data for the selected parameters. '
                        f'This usually happens when the strike prices have very different trading times. '
                        f'Try selecting strike prices that are closer together or use the same strike for both call and put.'
            })
        print(f"Straddle data created: {len(straddle_df)} records")
        
        # Check if we have sufficient data for chart generation
        if len(straddle_df) < 2:
            print(f"Insufficient data for chart generation: only {len(straddle_df)} record(s) available")
            return jsonify({
                'error': f'Insufficient data for chart generation. Only {len(straddle_df)} data point(s) available. '
                        f'For meaningful straddle analysis, at least 2 data points are required. '
                        f'Try selecting different strike prices or a different date with more trading activity.'
            })
        
        # Resample data to selected timeframe if not 1 minute
        if interval_minutes > 1:
            straddle_df_resampled = resample_straddle_data(straddle_df, interval_minutes)
            if straddle_df_resampled is None:
                print("Failed to resample straddle data, using original data")
                straddle_df_resampled = straddle_df
            else:
                print(f"Resampled data: {len(straddle_df_resampled)} records")
                straddle_df = straddle_df_resampled
        else:
            print("Using 1-minute data (no resampling needed)")
        
        # Get indicators from request
        indicators = request.form.getlist('indicators') if request.form.get('indicators') else []
        
        # Generate straddle chart
        chart_base64 = create_straddle_chart_base64(straddle_df, date, symbol, call_strike, put_strike, expiry, indicators)
        if chart_base64 is None:
            return jsonify({
                'error': f'Unable to generate chart with the available data. '
                        f'This might be due to insufficient data points or chart generation issues. '
                        f'Please try different parameters or contact support if the issue persists.'
            })
        
        # Prepare chart data for interactive chart
        chart_data = []
        for _, row in straddle_df.iterrows():
            chart_data.append({
                'time': row['time_readable'],
                'open': float(row['straddle_open']),
                'high': float(row['straddle_high']),
                'low': float(row['straddle_low']),
                'close': float(row['straddle_close']),
                'call_price': float(row['call_close']),
                'put_price': float(row['put_close'])
            })
        
        # Calculate time frame information
        time_frame_info = calculate_time_frame(straddle_df)
        
        # Update chart title to include timeframe
        if interval_minutes == 1:
            chart_title = f'Straddle Chart - {symbol.upper()} Call {call_strike} + Put {put_strike} ({date}) - Expiry: {expiry}'
        else:
            chart_title = f'{interval_minutes}-Minute Straddle Chart - {symbol.upper()} Call {call_strike} + Put {put_strike} ({date}) - Expiry: {expiry}'
        
        return jsonify({
            'success': True,
            'chart_base64': chart_base64,
            'chart_title': chart_title,
            'record_count': len(straddle_df),
            'chart_data': chart_data,
            'time_frame': time_frame_info,
            'call_strike': call_strike,
            'put_strike': put_strike,
            'expiry': expiry,
            'timeframe': interval_minutes
        })
        
    except Exception as e:
        print(f"Error generating straddle chart: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'An unexpected error occurred while generating the straddle chart: {str(e)}. '
                    f'Please try again with different parameters or contact support if the issue persists.'
        })

def create_straddle_data(call_df, put_df, call_strike, put_strike):
    """Create straddle data by combining call and put prices"""
    try:
        print(f"=== CREATE_STRADDLE_DATA DEBUG ===")
        print(f"Call DF shape: {call_df.shape if call_df is not None else 'None'}")
        print(f"Put DF shape: {put_df.shape if put_df is not None else 'None'}")
        
        if call_df is None or put_df is None:
            print("One or both dataframes are None")
            return None
            
        # Ensure both dataframes have the same time structure
        call_df = call_df.copy()
        put_df = put_df.copy()
        
        print(f"Call DF columns: {list(call_df.columns)}")
        print(f"Put DF columns: {list(put_df.columns)}")
        
        # Create time key for merging
        call_df['time_key'] = call_df['time']
        put_df['time_key'] = put_df['time']
        
        print(f"Call DF time range: {call_df['time'].min()} to {call_df['time'].max()}")
        print(f"Put DF time range: {put_df['time'].min()} to {put_df['time'].max()}")
        print(f"Call DF unique times: {len(call_df['time'].unique())}")
        print(f"Put DF unique times: {len(put_df['time'].unique())}")
        
        # Check for overlapping time ranges
        call_times = set(call_df['time'].unique())
        put_times = set(put_df['time'].unique())
        common_times = call_times.intersection(put_times)
        print(f"Common time points: {len(common_times)}")
        
        # For different strike prices, we need a more flexible merging approach
        # First try inner join (exact time match)
        merged_df = pd.merge(call_df, put_df, on='time_key', how='inner', suffixes=('_call', '_put'))
        
        print(f"Inner join result shape: {merged_df.shape}")
        
        # If inner join fails (different strike prices often have different time data),
        # try outer join and forward fill missing values
        if len(merged_df) == 0:
            print("Inner join failed, trying outer join with forward fill...")
            merged_df = pd.merge(call_df, put_df, on='time_key', how='outer', suffixes=('_call', '_put'))
            print(f"Outer join result shape: {merged_df.shape}")
            
            # Sort by time to ensure proper forward filling
            merged_df = merged_df.sort_values('time_key')
            
            # Forward fill missing values for OHLC data
            ohlc_columns = ['open_call', 'high_call', 'low_call', 'close_call', 
                           'open_put', 'high_put', 'low_put', 'close_put']
            
            for col in ohlc_columns:
                if col in merged_df.columns:
                    merged_df[col] = merged_df[col].ffill()
            
            # Remove rows where we still don't have both call and put data
            merged_df = merged_df.dropna(subset=['open_call', 'open_put'])
            print(f"After forward fill and cleanup: {merged_df.shape}")
        
        if len(merged_df) == 0:
            print("No matching time records between call and put data after all attempts")
            print("Trying time-based interpolation approach...")
            
            # Alternative approach: Create a unified time series and interpolate
            # Get all unique time points from both datasets
            all_times = sorted(set(call_df['time_key'].tolist() + put_df['time_key'].tolist()))
            print(f"Total unique time points: {len(all_times)}")
            
            # Create a base dataframe with all time points
            base_df = pd.DataFrame({'time_key': all_times})
            
            # Merge call data
            call_merged = pd.merge(base_df, call_df, on='time_key', how='left')
            # Forward fill call data
            call_ohlc_cols = ['open', 'high', 'low', 'close']
            for col in call_ohlc_cols:
                if col in call_merged.columns:
                    call_merged[col] = call_merged[col].ffill()
            
            # Merge put data
            put_merged = pd.merge(base_df, put_df, on='time_key', how='left')
            # Forward fill put data
            for col in call_ohlc_cols:
                if col in put_merged.columns:
                    put_merged[col] = put_merged[col].ffill()
            
            # Combine call and put data
            merged_df = pd.merge(call_merged, put_merged, on='time_key', suffixes=('_call', '_put'))
            
            # Remove rows where we still don't have both call and put data
            merged_df = merged_df.dropna(subset=['open_call', 'open_put'])
            print(f"After interpolation approach: {merged_df.shape}")
            
            if len(merged_df) == 0:
                print("All merging approaches failed")
                print("Trying final fallback: use available data with minimal overlap...")
                
                # Final fallback: Use the dataset with more data points and fill missing values
                if len(call_df) >= len(put_df):
                    print("Using call data as base and filling put data")
                    base_df = call_df.copy()
                    base_df['time_key'] = base_df['time']
                    
                    # Merge put data with forward fill
                    put_merged = pd.merge(base_df[['time_key']], put_df, on='time_key', how='left')
                    for col in ['open', 'high', 'low', 'close']:
                        if col in put_merged.columns:
                            put_merged[col] = put_merged[col].ffill().bfill()
                    
                    merged_df = pd.merge(base_df, put_merged, on='time_key', suffixes=('_call', '_put'))
                else:
                    print("Using put data as base and filling call data")
                    base_df = put_df.copy()
                    base_df['time_key'] = base_df['time']
                    
                    # Merge call data with forward fill
                    call_merged = pd.merge(base_df[['time_key']], call_df, on='time_key', how='left')
                    for col in ['open', 'high', 'low', 'close']:
                        if col in call_merged.columns:
                            call_merged[col] = call_merged[col].ffill().bfill()
                    
                    merged_df = pd.merge(base_df, call_merged, on='time_key', suffixes=('_put', '_call'))
                
                # Remove rows where we still don't have both call and put data
                merged_df = merged_df.dropna(subset=['open_call', 'open_put'])
                print(f"After final fallback: {merged_df.shape}")
                
                if len(merged_df) == 0:
                    print("All approaches failed - cannot create straddle data")
                    return None
        
        # Scale down prices (convert from paise to rupees)
        merged_df['call_open'] = merged_df['open_call'] / 100
        merged_df['call_high'] = merged_df['high_call'] / 100
        merged_df['call_low'] = merged_df['low_call'] / 100
        merged_df['call_close'] = merged_df['close_call'] / 100
        
        merged_df['put_open'] = merged_df['open_put'] / 100
        merged_df['put_high'] = merged_df['high_put'] / 100
        merged_df['put_low'] = merged_df['low_put'] / 100
        merged_df['put_close'] = merged_df['close_put'] / 100
        
        # Calculate straddle prices (call + put)
        merged_df['straddle_open'] = merged_df['call_open'] + merged_df['put_open']
        merged_df['straddle_high'] = merged_df['call_high'] + merged_df['put_high']
        merged_df['straddle_low'] = merged_df['call_low'] + merged_df['put_low']
        merged_df['straddle_close'] = merged_df['call_close'] + merged_df['put_close']
        
        # Debug: Check what columns are actually available
        print(f"Available columns in merged_df: {list(merged_df.columns)}")
        
        # Keep only necessary columns - use the actual column names that exist
        try:
            result_df = merged_df[[
                'time_key', 'date_readable_call', 'time_readable_call',
                'straddle_open', 'straddle_high', 'straddle_low', 'straddle_close',
                'call_open', 'call_high', 'call_low', 'call_close',
                'put_open', 'put_high', 'put_low', 'put_close'
            ]].copy()
            print(f"Successfully selected columns, result shape: {result_df.shape}")
        except KeyError as e:
            print(f"ERROR: Missing columns: {e}")
            print("Available columns:", list(merged_df.columns))
            # Use only the columns that exist
            available_cols = ['time_key']
            for col in ['date_readable_call', 'time_readable_call', 'straddle_open', 'straddle_high', 'straddle_low', 'straddle_close', 'call_open', 'call_high', 'call_low', 'call_close', 'put_open', 'put_high', 'put_low', 'put_close']:
                if col in merged_df.columns:
                    available_cols.append(col)
                else:
                    print(f"Column '{col}' not found")
            
            result_df = merged_df[available_cols].copy()
            print(f"Using available columns: {list(result_df.columns)}")
        
        # Rename columns for consistency
        result_df.rename(columns={
            'time_key': 'time',
            'date_readable_call': 'date_readable',
            'time_readable_call': 'time_readable'
        }, inplace=True)
        
        return result_df
        
    except Exception as e:
        print(f"Error creating straddle data: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_straddle_chart_base64(df, date, symbol, call_strike, put_strike, expiry, indicators=None):
    """Create a single interactive straddle candlestick chart with indicators and return as base64 string"""
    print(f"=== STRADDLE CHART CREATION DEBUG ===")
    print(f"DataFrame is None: {df is None}")
    print(f"DataFrame length: {len(df) if df is not None else 'N/A'}")
    print(f"Indicators received: {indicators}")
    
    if df is None or len(df) == 0:
        print("ERROR: DataFrame is None or empty")
        return None
    
    try:
        # Create datetime index for proper time series plotting
        df['datetime'] = pd.to_datetime(df['date_readable'] + ' ' + df['time_readable'])
        df.set_index('datetime', inplace=True)
        
        # Set dark theme style
        plt.style.use('dark_background')
        
        # Set up the plot with dark theme - single chart only
        fig, ax = plt.subplots(1, 1, figsize=(16, 9), facecolor='#1a1a1a')
        fig.patch.set_facecolor('#1a1a1a')
        ax.set_facecolor('#1a1a1a')
        
        # Enhanced color scheme for straddle chart
        straddle_colors = {
            'bull': '#00ff88',      # Bright green for bullish straddle
            'bear': '#ff4444',      # Bright red for bearish straddle
            'edge_bull': '#00cc66', # Darker green for edges
            'edge_bear': '#cc3333', # Darker red for edges
            'shadow': '#222222',    # Shadow color for depth
        }
        
        # Plot straddle candlesticks
        for i, (idx, row) in enumerate(df.iterrows()):
            open_price = row['straddle_open']
            close_price = row['straddle_close']
            high_price = row['straddle_high']
            low_price = row['straddle_low']
            
            if close_price >= open_price:
                color = straddle_colors['bull']
                edge_color = straddle_colors['edge_bull']
                wick_color = straddle_colors['bull']
            else:
                color = straddle_colors['bear']
                edge_color = straddle_colors['edge_bear']
                wick_color = straddle_colors['bear']
            
            # Plot the wick (vertical line from low to high)
            ax.plot([i, i], [low_price, high_price], color=wick_color, linewidth=1.5, alpha=0.9)
            
            # Plot the body
            body_height = abs(close_price - open_price)
            body_bottom = min(open_price, close_price)
            
            if body_height > 0:
                # Create proper candlestick body with better proportions
                rect = patches.Rectangle((i - 0.25, body_bottom), 0.5, body_height, 
                                       facecolor=color, edgecolor=edge_color, linewidth=1.0, alpha=0.9)
                ax.add_patch(rect)
                
                # Add subtle shadow effect for depth
                shadow_rect = patches.Rectangle((i - 0.22, body_bottom - 0.02), 0.44, body_height + 0.04, 
                                              facecolor=straddle_colors['shadow'], edgecolor='none', alpha=0.3)
                ax.add_patch(shadow_rect)
            else:
                # Doji (when open = close) - horizontal line
                ax.plot([i - 0.25, i + 0.25], [open_price, open_price], color=edge_color, linewidth=2)
        
        # Plot indicators if specified
        print(f"=== STRADDLE CHART INDICATORS DEBUG ===")
        print(f"Indicators received: {indicators}")
        print(f"Indicators type: {type(indicators)}")
        
        if indicators:
            print(f"Processing {len(indicators)} indicators in straddle chart")
            for indicator in indicators:
                print(f"Processing indicator: {indicator}")
                if indicator == 'vwap':
                    print("VWAP indicator detected in straddle chart, calculating...")
                    vwap_values = calculate_vwap(df)
                    print(f"VWAP values returned: {vwap_values is not None}")
                    if vwap_values is not None:
                        print(f"Plotting VWAP line with {len(vwap_values)} points")
                        ax.plot(range(len(vwap_values)), vwap_values, color='#ff6b6b', linewidth=2, 
                               label='VWAP', alpha=0.8)
                        print("VWAP line plotted successfully in straddle chart")
                    else:
                        print("VWAP values are None, not plotting in straddle chart")
                
                elif indicator in ['sma_20', 'sma_50', 'sma_100', 'sma_200']:
                    print(f"SMA indicator detected in straddle chart: {indicator}")
                    try:
                        if 'straddle_close' not in df.columns:
                            print("ERROR: straddle_close column not found for SMA calculation")
                            print(f"Available columns: {list(df.columns)}")
                        else:
                            try:
                                period = int(indicator.split('_')[1])
                            except Exception:
                                period = 20
                            print(f"Calculating SMA with period {period}")
                            sma_values = calculate_sma(df, period=period)
                            print(f"SMA {period} values returned: {sma_values is not None}")
                            if sma_values is not None:
                                try:
                                    color_map = {
                                        20: '#ffaa00',
                                        50: '#00ccff',
                                        100: '#9b59b6',
                                        200: '#ffffff'
                                    }
                                    color = color_map.get(period, '#ffaa00')
                                    label = f'SMA (Close, {period})'
                                    print(f"Plotting SMA line: period={period}, color={color}")
                                    ax.plot(range(len(sma_values)), sma_values, 
                                            color=color, linewidth=3, label=label, 
                                            alpha=0.9, linestyle='-', zorder=90)
                                    all_values = list(sma_values) + list(df['straddle_close'])
                                    y_min = min(all_values) * 0.995
                                    y_max = max(all_values) * 1.005
                                    ax.set_ylim(y_min, y_max)
                                    print(f"SMA {period} line plotted successfully")
                                except Exception as plot_error:
                                    print(f"Error plotting SMA {period} line: {plot_error}")
                            else:
                                print(f"SMA {period} values are None, not plotting in straddle chart")
                    except Exception as sma_error:
                        print(f"Error handling SMA indicator {indicator}: {sma_error}")
                
                elif indicator == 'ema_20':
                    print("*** EMA 20 INDICATOR DETECTED ***")
                    print(f"DataFrame columns available: {list(df.columns)}")
                    print(f"DataFrame length: {len(df)}")
                    print(f"DataFrame shape: {df.shape}")
                    if 'straddle_close' in df.columns:
                        print("straddle_close column found, proceeding with EMA calculation")
                        print(f"First few straddle_close values: {df['straddle_close'].head()}")
                        ema_20_values = calculate_ema(df, period=20, price_column='straddle_close')
                        print(f"EMA 20 values returned: {ema_20_values is not None}")
                        if ema_20_values is not None:
                            print(f"*** PLOTTING EMA 20 LINE ***")
                            print(f"Number of EMA points: {len(ema_20_values)}")
                            print(f"EMA 20 values range: {min(ema_20_values):.2f} to {max(ema_20_values):.2f}")
                            print(f"First 5 EMA values: {ema_20_values[:5]}")
                            print(f"Last 5 EMA values: {ema_20_values[-5:]}")
                            
                            # Plot EMA line with very visible styling - plot AFTER candlesticks
                            ax.plot(range(len(ema_20_values)), ema_20_values, 
                                   color='#ff0000', linewidth=6, label='EMA (Close, 20)', 
                                   alpha=1.0, linestyle='-', zorder=100, marker='o', markersize=2)
                            print("*** EMA 20 LINE PLOTTED SUCCESSFULLY ***")
                            
                            # Ensure the line is visible by adjusting plot limits
                            all_values = list(ema_20_values) + list(df['straddle_close'])
                            y_min = min(all_values) * 0.995
                            y_max = max(all_values) * 1.005
                            ax.set_ylim(y_min, y_max)
                            print(f"Chart limits after EMA: x={ax.get_xlim()}, y={ax.get_ylim()}")
                            print(f"EMA line should be visible between {min(ema_20_values):.2f} and {max(ema_20_values):.2f}")
                        else:
                            print("*** ERROR: EMA 20 values are None ***")
                    else:
                        print("*** ERROR: straddle_close column not found in DataFrame ***")
                        print(f"Available columns: {list(df.columns)}")
                
                elif indicator == 'ema_50':
                    print("*** EMA 50 INDICATOR DETECTED ***")
                    print(f"DataFrame columns available: {list(df.columns)}")
                    print(f"DataFrame length: {len(df)}")
                    print(f"DataFrame shape: {df.shape}")
                    if 'straddle_close' in df.columns:
                        print("straddle_close column found, proceeding with EMA calculation")
                        print(f"First few straddle_close values: {df['straddle_close'].head()}")
                        ema_50_values = calculate_ema(df, period=50, price_column='straddle_close')
                        print(f"EMA 50 values returned: {ema_50_values is not None}")
                        if ema_50_values is not None:
                            print(f"*** PLOTTING EMA 50 LINE ***")
                            print(f"Number of EMA points: {len(ema_50_values)}")
                            print(f"EMA 50 values range: {min(ema_50_values):.2f} to {max(ema_50_values):.2f}")
                            print(f"First 5 EMA values: {ema_50_values[:5]}")
                            print(f"Last 5 EMA values: {ema_50_values[-5:]}")
                            
                            # Plot EMA line with very visible styling - plot AFTER candlesticks
                            ax.plot(range(len(ema_50_values)), ema_50_values, 
                                   color='#00ff00', linewidth=6, label='EMA (Close, 50)', 
                                   alpha=1.0, linestyle='-', zorder=100, marker='o', markersize=2)
                            print("*** EMA 50 LINE PLOTTED SUCCESSFULLY ***")
                            
                            # Ensure the line is visible by adjusting plot limits
                            all_values = list(ema_50_values) + list(df['straddle_close'])
                            y_min = min(all_values) * 0.995
                            y_max = max(all_values) * 1.005
                            ax.set_ylim(y_min, y_max)
                            print(f"Chart limits after EMA: x={ax.get_xlim()}, y={ax.get_ylim()}")
                            print(f"EMA line should be visible between {min(ema_50_values):.2f} and {max(ema_50_values):.2f}")
                        else:
                            print("*** ERROR: EMA 50 values are None ***")
                    else:
                        print("*** ERROR: straddle_close column not found in DataFrame ***")
                        print(f"Available columns: {list(df.columns)}")
                
                elif indicator == 'ema_100':
                    print("*** EMA 100 INDICATOR DETECTED ***")
                    print(f"DataFrame columns available: {list(df.columns)}")
                    print(f"DataFrame length: {len(df)}")
                    print(f"DataFrame shape: {df.shape}")
                    if 'straddle_close' in df.columns:
                        print("straddle_close column found, proceeding with EMA calculation")
                        print(f"First few straddle_close values: {df['straddle_close'].head()}")
                        ema_100_values = calculate_ema(df, period=100, price_column='straddle_close')
                        print(f"EMA 100 values returned: {ema_100_values is not None}")
                        if ema_100_values is not None:
                            print(f"*** PLOTTING EMA 100 LINE ***")
                            print(f"Number of EMA points: {len(ema_100_values)}")
                            print(f"EMA 100 values range: {min(ema_100_values):.2f} to {max(ema_100_values):.2f}")
                            print(f"First 5 EMA values: {ema_100_values[:5]}")
                            print(f"Last 5 EMA values: {ema_100_values[-5:]}")
                            
                            # Plot EMA line with very visible styling - plot AFTER candlesticks
                            ax.plot(range(len(ema_100_values)), ema_100_values, 
                                   color='#9b59b6', linewidth=6, label='EMA (Close, 100)', 
                                   alpha=1.0, linestyle='-', zorder=100, marker='o', markersize=2)
                            print("*** EMA 100 LINE PLOTTED SUCCESSFULLY ***")
                            
                            # Ensure the line is visible by adjusting plot limits
                            all_values = list(ema_100_values) + list(df['straddle_close'])
                            y_min = min(all_values) * 0.995
                            y_max = max(all_values) * 1.005
                            ax.set_ylim(y_min, y_max)
                            print(f"Chart limits after EMA: x={ax.get_xlim()}, y={ax.get_ylim()}")
                            print(f"EMA line should be visible between {min(ema_100_values):.2f} and {max(ema_100_values):.2f}")
                        else:
                            print("*** ERROR: EMA 100 values are None ***")
                    else:
                        print("*** ERROR: straddle_close column not found in DataFrame ***")
                        print(f"Available columns: {list(df.columns)}")
                
                elif indicator == 'ema_200':
                    print("*** EMA 200 INDICATOR DETECTED ***")
                    print(f"DataFrame columns available: {list(df.columns)}")
                    print(f"DataFrame length: {len(df)}")
                    print(f"DataFrame shape: {df.shape}")
                    if 'straddle_close' in df.columns:
                        print("straddle_close column found, proceeding with EMA calculation")
                        print(f"First few straddle_close values: {df['straddle_close'].head()}")
                        ema_200_values = calculate_ema(df, period=200, price_column='straddle_close')
                        print(f"EMA 200 values returned: {ema_200_values is not None}")
                        if ema_200_values is not None:
                            print(f"*** PLOTTING EMA 200 LINE ***")
                            print(f"Number of EMA points: {len(ema_200_values)}")
                            print(f"EMA 200 values range: {min(ema_200_values):.2f} to {max(ema_200_values):.2f}")
                            print(f"First 5 EMA values: {ema_200_values[:5]}")
                            print(f"Last 5 EMA values: {ema_200_values[-5:]}")
                            
                            # Plot EMA line with very visible styling - plot AFTER candlesticks
                            ax.plot(range(len(ema_200_values)), ema_200_values, 
                                   color='#e74c3c', linewidth=6, label='EMA (Close, 200)', 
                                   alpha=1.0, linestyle='-', zorder=100, marker='o', markersize=2)
                            print("*** EMA 200 LINE PLOTTED SUCCESSFULLY ***")
                            
                            # Ensure the line is visible by adjusting plot limits
                            all_values = list(ema_200_values) + list(df['straddle_close'])
                            y_min = min(all_values) * 0.995
                            y_max = max(all_values) * 1.005
                            ax.set_ylim(y_min, y_max)
                            print(f"Chart limits after EMA: x={ax.get_xlim()}, y={ax.get_ylim()}")
                            print(f"EMA line should be visible between {min(ema_200_values):.2f} and {max(ema_200_values):.2f}")
                        else:
                            print("*** ERROR: EMA 200 values are None ***")
                    else:
                        print("*** ERROR: straddle_close column not found in DataFrame ***")
                        print(f"Available columns: {list(df.columns)}")
        else:
            print("*** NO INDICATORS RECEIVED IN STRADDLE CHART ***")
        
        # Customize the straddle chart
        symbol_display = symbol.upper()
        # Note: timeframe will be added by the calling function
        title = f'{symbol_display} Straddle Chart - Call {call_strike} + Put {put_strike} ({date}) - Expiry: {expiry}'
        
        ax.set_title(title, fontsize=18, fontweight='bold', color='#ffffff', pad=20)
        ax.set_xlabel('Time', fontsize=14, color='#cccccc', fontweight='bold')
        ax.set_ylabel('Straddle Price (INR)', fontsize=14, color='#cccccc', fontweight='bold')
        # Enhanced grid styling
        ax.grid(True, alpha=0.15, color='#333333', linewidth=0.5, linestyle='-')
        ax.set_axisbelow(True)
        
        # Set x-axis limits with proper spacing
        ax.set_xlim(-0.5, len(df) - 0.5)
        
        # Adjust spacing for better candlestick visibility
        if len(df) > 50:
            # For many data points, reduce spacing
            ax.set_xlim(-0.3, len(df) - 0.7)
        elif len(df) > 20:
            # For moderate data points, standard spacing
            ax.set_xlim(-0.4, len(df) - 0.6)
        
        # Set x-axis labels for straddle chart
        n_points = len(df)
        if n_points > 30:
            step = max(1, n_points // 12)
            x_ticks = range(0, n_points, step)
            x_labels = [df.index[i].strftime('%H:%M') for i in x_ticks]
        elif n_points > 15:
            step = max(1, n_points // 10)
            x_ticks = range(0, n_points, step)
            x_labels = [df.index[i].strftime('%H:%M') for i in x_ticks]
        else:
            x_ticks = range(n_points)
            x_labels = [df.index[i].strftime('%H:%M') for i in x_ticks]
        
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels, rotation=45, color='#cccccc', fontsize=10)
        # Enhanced y-axis formatting
        ax.tick_params(axis='y', colors='#cccccc', labelsize=11)
        
        # Format y-axis labels with proper currency formatting
        def format_price(x, pos):
            return f'₹{x:,.0f}'
        
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_price))
        
        # Add straddle statistics box
        current_straddle = df['straddle_close'].iloc[-1]
        straddle_change = current_straddle - df['straddle_open'].iloc[0]
        straddle_change_pct = (straddle_change / df['straddle_open'].iloc[0]) * 100
        
        stats_text = f"""Straddle O {df['straddle_open'].iloc[0]:,.2f}
Straddle H {df['straddle_high'].max():,.2f}
Straddle L {df['straddle_low'].min():,.2f}
Straddle C {current_straddle:,.2f}
{straddle_change:+.2f} ({straddle_change_pct:+.2f}%)"""
        
        bbox_props = dict(boxstyle='round,pad=0.8', facecolor='#2a2a2a', 
                          edgecolor='#444444', alpha=0.9)
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', fontsize=12, fontweight='bold',
                color='#ffffff', bbox=bbox_props, fontfamily='monospace')
        
        # Add current price line indicator
        ax.axhline(y=current_straddle, color='#ff4444', linestyle='--', alpha=0.7, linewidth=1.5)
        
        # Style the spines
        for spine in ax.spines.values():
            spine.set_color('#444444')
            spine.set_linewidth(1.5)
        
        # Add legend for indicators
        if indicators:
            ax.legend(loc='upper left', fontsize=10, framealpha=0.8, 
                     facecolor='#2a2a2a', edgecolor='#444444')
        
        plt.tight_layout()
        
        # Convert plot to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', 
                    facecolor='#1a1a1a', edgecolor='none')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return img_base64
        
    except Exception as e:
        print(f"Error creating straddle chart: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        plt.close('all')
        plt.clf()

# ===== OPTIONS CHAIN ROUTES =====
@app.route('/get_available_dates')
def get_available_dates_route():
    """API route to get available dates for a data type and symbol"""
    data_type = request.args.get('data_type')
    symbol = request.args.get('symbol', 'nifty')
    
    if not data_type:
        return jsonify({'error': 'data_type is required'})
    
    try:
        dates = get_available_dates(data_type, symbol)
        
        if dates:
            return jsonify({
                'success': True,
                'dates': dates
            })
        else:
            return jsonify({
                'success': False,
                'dates': [],
                'error': 'No dates found for the specified data type and symbol'
            })
    
    except Exception as e:
        print(f"Error in get_available_dates_route: {e}")
        return jsonify({'error': str(e)})

def calculate_iv_skew(options_chain, underlying_price, expiry_date, risk_free_rate=0.04):
    """
    Calculate IV Skew analysis for options chain
    
    Returns:
    - iv_skew_data: Dictionary containing skew metrics and analysis
    """
    try:
        if not options_chain or not underlying_price or underlying_price <= 0:
            return {
                'skew_type': 'insufficient_data',
                'atm_iv': 0,
                'skew_slope': 0,
                'skew_curvature': 0,
                'put_call_iv_spread': 0,
                'skew_percentiles': {},
                'analysis': 'Insufficient data for IV skew calculation'
            }
        
        # Calculate time to expiry
        if expiry_date:
            from datetime import datetime
            try:
                expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
                today = datetime.now()
                days_to_expiry = max(1, (expiry - today).days)
                time_to_expiry = days_to_expiry / 365.0
                
                # Ensure reasonable time to expiry (1 day to 1 year)
                time_to_expiry = max(1/365.0, min(1.0, time_to_expiry))
            except:
                time_to_expiry = 7 / 365.0  # Default to 7 days
        else:
            time_to_expiry = 7 / 365.0  # Default to 7 days
        
        # Collect IV data for calls and puts
        call_iv_data = []
        put_iv_data = []
        strike_iv_pairs = []
        
        for row in options_chain:
            strike = row['strike']
            call_ltp = row['call']['ltp']
            put_ltp = row['put']['ltp']
            
            # Calculate moneyness (strike/underlying) - with validation
            if underlying_price > 0:
                moneyness = strike / underlying_price
                # Filter out extreme moneyness values (0.5 to 2.0 range)
                if moneyness < 0.5 or moneyness > 2.0:
                    continue
            else:
                continue
            
            # Calculate IV for calls - with intelligent price filtering
            if call_ltp > 0:
                # More intelligent price filtering based on moneyness
                max_reasonable_price = underlying_price * 0.02  # 2% of underlying
                if moneyness < 0.95:  # OTM calls
                    max_reasonable_price = underlying_price * 0.01  # 1% for OTM
                elif moneyness > 1.05:  # ITM calls
                    max_reasonable_price = underlying_price * 0.03  # 3% for ITM
                
                if call_ltp <= max_reasonable_price:
                    call_iv = calculate_implied_volatility_backend(
                        call_ltp, underlying_price, strike, time_to_expiry, risk_free_rate, 'call'
                    )
                    # More realistic IV range based on market conditions
                    if 0.01 <= call_iv <= 0.3:  # 1% to 30% IV range (more realistic)
                        call_iv_data.append({
                            'strike': strike,
                            'iv': call_iv,
                            'moneyness': moneyness,
                            'ltp': call_ltp
                        })
                        strike_iv_pairs.append({
                            'strike': strike,
                            'iv': call_iv,
                            'type': 'call',
                            'moneyness': moneyness
                        })
            
            # Calculate IV for puts - with intelligent price filtering
            if put_ltp > 0:
                # More intelligent price filtering based on moneyness
                max_reasonable_price = underlying_price * 0.02  # 2% of underlying
                if moneyness < 0.95:  # ITM puts
                    max_reasonable_price = underlying_price * 0.03  # 3% for ITM
                elif moneyness > 1.05:  # OTM puts
                    max_reasonable_price = underlying_price * 0.01  # 1% for OTM
                
                if put_ltp <= max_reasonable_price:
                    put_iv = calculate_implied_volatility_backend(
                        put_ltp, underlying_price, strike, time_to_expiry, risk_free_rate, 'put'
                    )
                    # More realistic IV range based on market conditions
                    if 0.01 <= put_iv <= 0.3:  # 1% to 30% IV range (more realistic)
                        put_iv_data.append({
                            'strike': strike,
                            'iv': put_iv,
                            'moneyness': moneyness,
                            'ltp': put_ltp
                        })
                        strike_iv_pairs.append({
                            'strike': strike,
                            'iv': put_iv,
                            'type': 'put',
                            'moneyness': moneyness
                        })
        
        if not strike_iv_pairs:
            return {
                'skew_type': 'no_data',
                'atm_iv': 0,
                'skew_slope': 0,
                'skew_curvature': 0,
                'put_call_iv_spread': 0,
                'skew_percentiles': {},
                'analysis': 'No valid IV data found'
            }
        
        # Sort by strike price
        strike_iv_pairs.sort(key=lambda x: x['strike'])
        
        # Find ATM strike and IV
        atm_strike = min(strike_iv_pairs, key=lambda x: abs(x['strike'] - underlying_price))
        atm_iv = atm_strike['iv']
        
        # Calculate skew metrics
        skew_metrics = calculate_skew_metrics(strike_iv_pairs, underlying_price, atm_iv)
        
        # Determine skew type
        skew_type = determine_skew_type(skew_metrics)
        
        # Calculate percentiles using proper interpolation
        all_ivs = [item['iv'] for item in strike_iv_pairs]
        all_ivs.sort()
        
        def percentile(data, pct):
            """Calculate percentile with linear interpolation"""
            if not data:
                return 0
            if len(data) == 1:
                return data[0]
            # Use linear interpolation for better percentile calculation
            k = (len(data) - 1) * pct
            f = int(k)
            c = k - f
            if f + 1 < len(data):
                return data[f] * (1 - c) + data[f + 1] * c
            else:
                return data[f]
        
        skew_percentiles = {
            'p25': percentile(all_ivs, 0.25),
            'p50': percentile(all_ivs, 0.5),
            'p75': percentile(all_ivs, 0.75),
            'min': min(all_ivs) if all_ivs else 0,
            'max': max(all_ivs) if all_ivs else 0
        }
        
        # Generate analysis
        analysis = generate_skew_analysis(skew_type, skew_metrics, atm_iv, skew_percentiles)
        
        # Debug information
        print(f"=== IV SKEW DEBUG ===")
        print(f"Underlying Price: {underlying_price}")
        print(f"Time to Expiry: {time_to_expiry:.4f} years")
        print(f"Data points: {len(strike_iv_pairs)}")
        print(f"ATM IV: {atm_iv:.4f} ({atm_iv*100:.2f}%)")
        print(f"Skew slope: {skew_metrics['slope']:.4f}")
        print(f"Curvature: {skew_metrics['curvature']:.4f}")
        print(f"Put-call spread: {skew_metrics['put_call_spread']:.4f} ({skew_metrics['put_call_spread']*100:.2f}%)")
        print(f"Skew type: {skew_type}")
        print(f"IV Percentiles: Min={skew_percentiles['min']:.4f}, P25={skew_percentiles['p25']:.4f}, P50={skew_percentiles['p50']:.4f}, P75={skew_percentiles['p75']:.4f}, Max={skew_percentiles['max']:.4f}")
        
        # Show sample data points for debugging
        if len(strike_iv_pairs) > 0:
            print("Sample data points (first 5 and last 5):")
            for i, point in enumerate(strike_iv_pairs[:5]):  # Show first 5 points
                print(f"  {i+1}. Strike: {point['strike']}, IV: {point['iv']:.4f} ({point['iv']*100:.2f}%), Type: {point['type']}, Moneyness: {point['moneyness']:.3f}")
            if len(strike_iv_pairs) > 10:
                print("  ...")
                for i, point in enumerate(strike_iv_pairs[-5:], len(strike_iv_pairs)-4):  # Show last 5 points
                    print(f"  {i}. Strike: {point['strike']}, IV: {point['iv']:.4f} ({point['iv']*100:.2f}%), Type: {point['type']}, Moneyness: {point['moneyness']:.3f}")
        
        return {
            'skew_type': skew_type,
            'atm_iv': round(atm_iv, 4),
            'skew_slope': round(skew_metrics['slope'], 4),
            'skew_curvature': round(skew_metrics['curvature'], 4),
            'put_call_iv_spread': round(skew_metrics['put_call_spread'], 4),
            'skew_percentiles': {k: round(v, 4) for k, v in skew_percentiles.items()},
            'analysis': analysis,
            'data_points': len(strike_iv_pairs),
            'raw_data': strike_iv_pairs[:20]  # Limit to first 20 for performance
        }
        
    except Exception as e:
        print(f"Error calculating IV skew: {e}")
        return {
            'skew_type': 'error',
            'atm_iv': 0,
            'skew_slope': 0,
            'skew_curvature': 0,
            'put_call_iv_spread': 0,
            'skew_percentiles': {},
            'analysis': f'Error in IV skew calculation: {str(e)}'
        }

def calculate_implied_volatility_backend(option_price, underlying_price, strike, time_to_expiry, risk_free_rate, option_type):
    """Backend implementation of implied volatility calculation"""
    try:
        if time_to_expiry <= 0 or option_price <= 0 or underlying_price <= 0 or strike <= 0:
            return 0
        
        # Newton-Raphson method
        sigma = 0.2  # Initial guess
        max_iterations = 50
        tolerance = 0.0001
        
        for i in range(max_iterations):
            d1 = (math.log(underlying_price / strike) + (risk_free_rate + 0.5 * sigma * sigma) * time_to_expiry) / (sigma * math.sqrt(time_to_expiry))
            d2 = d1 - sigma * math.sqrt(time_to_expiry)
            
            # Standard normal CDF approximation
            N_d1 = 0.5 * (1 + math.erf(d1 / math.sqrt(2)))
            N_d2 = 0.5 * (1 + math.erf(d2 / math.sqrt(2)))
            N_neg_d1 = 0.5 * (1 + math.erf(-d1 / math.sqrt(2)))
            N_neg_d2 = 0.5 * (1 + math.erf(-d2 / math.sqrt(2)))
            
            # Standard normal PDF
            n_d1 = math.exp(-0.5 * d1 * d1) / math.sqrt(2 * math.pi)
            
            # Black-Scholes price
            if option_type == 'call':
                theoretical_price = underlying_price * N_d1 - strike * math.exp(-risk_free_rate * time_to_expiry) * N_d2
            else:
                theoretical_price = strike * math.exp(-risk_free_rate * time_to_expiry) * N_neg_d2 - underlying_price * N_neg_d1
            
            # Vega (derivative of price w.r.t. volatility)
            vega = underlying_price * n_d1 * math.sqrt(time_to_expiry)
            
            price_diff = theoretical_price - option_price
            
            if abs(price_diff) < tolerance:
                break
            
            if abs(vega) < 1e-10:
                break
            
            sigma = sigma - price_diff / vega
            sigma = max(0.01, min(0.3, sigma))  # Clamp between 1% and 30%
        
        return max(0.01, min(0.3, sigma))  # Final clamp - realistic IV range (1% to 30%)
        
    except Exception as e:
        print(f"Error in IV calculation: {e}")
        return 0

def calculate_skew_metrics(strike_iv_pairs, underlying_price, atm_iv):
    """Calculate various skew metrics"""
    try:
        if len(strike_iv_pairs) < 3:
            return {
                'slope': 0,
                'curvature': 0,
                'put_call_spread': 0
            }
        
        # Separate calls and puts
        calls = [item for item in strike_iv_pairs if item['type'] == 'call']
        puts = [item for item in strike_iv_pairs if item['type'] == 'put']
        
        # Calculate slope (linear regression of IV vs moneyness) - Improved implementation
        if len(strike_iv_pairs) >= 2:
            x_values = [item['moneyness'] for item in strike_iv_pairs]
            y_values = [item['iv'] for item in strike_iv_pairs]
            
            n = len(x_values)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)
            
            denominator = n * sum_x2 - sum_x * sum_x
            if abs(denominator) > 1e-10:  # Avoid division by very small numbers
                slope = (n * sum_xy - sum_x * sum_y) / denominator
                # Clamp slope to reasonable range
                slope = max(-10, min(10, slope))
            else:
                slope = 0
        else:
            slope = 0
        
        # Calculate curvature (second derivative approximation) - Fixed implementation
        if len(strike_iv_pairs) >= 3:
            # Sort by moneyness
            sorted_pairs = sorted(strike_iv_pairs, key=lambda x: x['moneyness'])
            
            # Use more points for better curvature calculation
            if len(sorted_pairs) >= 5:
                # Use 5 points for better curvature estimation
                points = sorted_pairs[::max(1, len(sorted_pairs)//5)][:5]  # Take 5 evenly spaced points
            else:
                points = sorted_pairs
            
            if len(points) >= 3:
                # Calculate curvature using finite differences
                curvatures = []
                for i in range(1, len(points) - 1):
                    left = points[i-1]
                    mid = points[i]
                    right = points[i+1]
                    
                    h1 = mid['moneyness'] - left['moneyness']
                    h2 = right['moneyness'] - mid['moneyness']
                    
                    if h1 > 0 and h2 > 0 and h1 + h2 > 0:
                        # Second derivative approximation
                        curvature_point = 2 * ((right['iv'] - mid['iv']) / h2 - (mid['iv'] - left['iv']) / h1) / (h1 + h2)
                        curvatures.append(curvature_point)
                
                # Average curvature across all points and clamp to reasonable range
                curvature = sum(curvatures) / len(curvatures) if curvatures else 0
                # Clamp curvature to reasonable range (-1 to +1)
                curvature = max(-1.0, min(1.0, curvature))
            else:
                curvature = 0
        else:
            curvature = 0
        
        # Calculate put-call IV spread (average put IV - average call IV)
        if calls and puts:
            avg_call_iv = sum(call['iv'] for call in calls) / len(calls)
            avg_put_iv = sum(put['iv'] for put in puts) / len(puts)
            put_call_spread = avg_put_iv - avg_call_iv
        else:
            put_call_spread = 0
        
        return {
            'slope': slope,
            'curvature': curvature,
            'put_call_spread': put_call_spread
        }
        
    except Exception as e:
        print(f"Error calculating skew metrics: {e}")
        return {
            'slope': 0,
            'curvature': 0,
            'put_call_spread': 0
        }

def determine_skew_type(skew_metrics):
    """Determine the type of volatility skew"""
    slope = skew_metrics['slope']
    curvature = skew_metrics['curvature']
    put_call_spread = skew_metrics['put_call_spread']
    
    # Define thresholds - more realistic for options trading
    slope_threshold = 0.05  # 5% slope threshold
    curvature_threshold = 0.02  # 2% curvature threshold
    spread_threshold = 0.01  # 1% spread threshold
    
    # Check curvature first (smile/frown patterns are most distinctive)
    if curvature > curvature_threshold:
        return 'smile'
    elif curvature < -curvature_threshold:
        return 'frown'
    # Then check slope patterns
    elif abs(slope) < slope_threshold and abs(curvature) < curvature_threshold:
        return 'flat'
    elif slope < -slope_threshold:
        # Negative slope: IV decreases as strike increases (reverse skew - typical for equities)
        return 'reverse_skew'
    elif slope > slope_threshold:
        # Positive slope: IV increases as strike increases (forward skew - unusual in equities)
        return 'forward_skew'
    else:
        return 'mixed'

def generate_skew_analysis(skew_type, skew_metrics, atm_iv, skew_percentiles):
    """Generate human-readable analysis of the IV skew"""
    analysis_parts = []
    
    # Basic skew type
    skew_descriptions = {
        'flat': 'The volatility surface appears relatively flat, suggesting balanced market sentiment.',
        'reverse_skew': 'Reverse skew detected - higher IV for lower strikes, typical equity fear pattern indicating demand for downside protection.',
        'forward_skew': 'Forward skew detected - higher IV for higher strikes, unusual pattern suggesting increased call demand or concern about upside volatility.',
        'smile': 'Volatility smile pattern - higher IV for both deep ITM and OTM options, suggesting tail risk concerns.',
        'frown': 'Volatility frown pattern - lower IV for extreme strikes, ATM options are most expensive.',
        'mixed': 'Mixed volatility patterns detected across the strike range.'
    }
    
    analysis_parts.append(skew_descriptions.get(skew_type, 'Unusual volatility pattern detected.'))
    
    # ATM IV level
    if atm_iv > 0.4:
        analysis_parts.append(f"Very high ATM IV ({atm_iv:.1%}) suggests extreme market uncertainty.")
    elif atm_iv > 0.25:
        analysis_parts.append(f"High ATM IV ({atm_iv:.1%}) suggests elevated market uncertainty.")
    elif atm_iv < 0.10:
        analysis_parts.append(f"Low ATM IV ({atm_iv:.1%}) suggests calm market conditions.")
    else:
        analysis_parts.append(f"Moderate ATM IV ({atm_iv:.1%}) indicates normal market volatility.")
    
    # Skew slope
    slope = skew_metrics['slope']
    if abs(slope) > 0.05:
        if slope < 0:
            analysis_parts.append(f"Negative slope ({slope:.3f}) shows increasing IV for lower strikes.")
        else:
            analysis_parts.append(f"Positive slope ({slope:.3f}) shows increasing IV for higher strikes.")
    
    # Put-call spread
    spread = skew_metrics['put_call_spread']
    if abs(spread) > 0.01:
        if spread > 0:
            # Put IV > Call IV: Classic fear/bearish pattern (demand for downside protection)
            analysis_parts.append(f"Put IV exceeds Call IV by {spread:.1%}, indicating bearish sentiment.")
        else:
            # Call IV > Put IV: Unusual pattern, could indicate call buying pressure or low put demand
            analysis_parts.append(f"Call IV exceeds Put IV by {abs(spread):.1%}, indicating unusual call demand or complacency.")
    
    return " ".join(analysis_parts)

def create_iv_skew_chart_base64(options_chain, underlying_price, expiry_date, symbol='NIFTY'):
    """Create IV Skew chart and return as base64 string"""
    try:
        if not options_chain or not underlying_price or underlying_price <= 0:
            return None
        
        # Calculate IV skew data
        iv_skew_data = calculate_iv_skew(options_chain, underlying_price, expiry_date)
        
        if iv_skew_data['skew_type'] in ['no_data', 'insufficient_data']:
            return None
        
        # Set dark theme style
        plt.style.use('dark_background')
        
        # Create figure with dark theme
        fig, ax = plt.subplots(figsize=(14, 8), facecolor='#1a1a1a')
        ax.set_facecolor('#1a1a1a')
        
        # Extract strike prices and IV values for plotting
        strikes = []
        iv_values = []
        call_ivs = []
        put_ivs = []
        
        for row in options_chain:
            strike = row['strike']
            call_ltp = row['call']['ltp']
            put_ltp = row['put']['ltp']
            
            if call_ltp > 0 and put_ltp > 0:
                # Calculate time to expiry
                if expiry_date:
                    try:
                        from datetime import datetime
                        expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
                        today = datetime.now()
                        days_to_expiry = max(1, (expiry - today).days)
                        time_to_expiry = days_to_expiry / 365.0
                        time_to_expiry = max(1/365.0, min(1.0, time_to_expiry))
                    except:
                        time_to_expiry = 7 / 365.0
                else:
                    time_to_expiry = 7 / 365.0
                
                # Calculate IV for calls and puts
                call_iv = calculate_implied_volatility_backend(
                    call_ltp, underlying_price, strike, time_to_expiry, 0.04, 'call'
                )
                put_iv = calculate_implied_volatility_backend(
                    put_ltp, underlying_price, strike, time_to_expiry, 0.04, 'put'
                )
                
                if 0.01 <= call_iv <= 0.3 and 0.01 <= put_iv <= 0.3:
                    strikes.append(strike)
                    # Use average IV for the curve
                    avg_iv = (call_iv + put_iv) / 2
                    iv_values.append(avg_iv * 100)  # Convert to percentage
                    call_ivs.append(call_iv * 100)
                    put_ivs.append(put_iv * 100)
        
        if len(strikes) < 3:
            return None
        
        # Sort by strike price
        sorted_data = sorted(zip(strikes, iv_values, call_ivs, put_ivs))
        strikes, iv_values, call_ivs, put_ivs = zip(*sorted_data)
        
        # Plot the IV skew curve
        ax.plot(strikes, iv_values, 'b-', linewidth=2.5, label='IV Skew', alpha=0.9)
        
        # Add scatter points for better visibility
        ax.scatter(strikes, iv_values, color='blue', s=30, alpha=0.7, zorder=5)
        
        # Add vertical line for current underlying price
        ax.axvline(x=underlying_price, color='red', linestyle='--', linewidth=2, 
                  label=f'Current Price: {underlying_price:.2f}', alpha=0.8)
        
        # Find and mark the minimum IV point
        min_iv_idx = iv_values.index(min(iv_values))
        min_iv_strike = strikes[min_iv_idx]
        min_iv_value = iv_values[min_iv_idx]
        
        # Mark minimum IV point
        ax.axvline(x=min_iv_strike, color='blue', linestyle='--', linewidth=1.5, 
                  alpha=0.6, label=f'Min IV: {min_iv_strike}')
        ax.scatter([min_iv_strike], [min_iv_value], color='blue', s=100, 
                  marker='o', edgecolor='white', linewidth=2, zorder=6)
        
        # Add tooltip-style annotations for key points
        ax.annotate(f'{min_iv_value:.2f}%', 
                   xy=(min_iv_strike, min_iv_value), 
                   xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='blue', alpha=0.7),
                   fontsize=9, color='white', weight='bold')
        
        # Formatting
        ax.set_xlabel('Strike Price', fontsize=12, color='white', weight='bold')
        ax.set_ylabel('Implied Volatility (%)', fontsize=12, color='white', weight='bold')
        ax.set_title(f'IV Skew for {symbol} - {expiry_date}', fontsize=14, color='white', weight='bold', pad=20)
        
        # Grid
        ax.grid(True, alpha=0.3, color='gray')
        ax.set_axisbelow(True)
        
        # Legend
        ax.legend(loc='upper right', framealpha=0.8, facecolor='#2a2a2a', 
                 edgecolor='white', fontsize=10)
        
        # Set axis limits with some padding
        x_margin = (max(strikes) - min(strikes)) * 0.05
        y_margin = (max(iv_values) - min(iv_values)) * 0.1
        ax.set_xlim(min(strikes) - x_margin, max(strikes) + x_margin)
        ax.set_ylim(min(iv_values) - y_margin, max(iv_values) + y_margin)
        
        # Format y-axis as percentage
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}%'))
        
        # Add skew metrics as text
        skew_text = f"Skew Type: {iv_skew_data['skew_type'].replace('_', ' ').title()}\n"
        skew_text += f"ATM IV: {iv_skew_data['atm_iv']*100:.2f}%\n"
        skew_text += f"Slope: {iv_skew_data['skew_slope']:.4f}\n"
        skew_text += f"Curvature: {iv_skew_data['skew_curvature']:.4f}"
        
        ax.text(0.02, 0.98, skew_text, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', 
               facecolor='#2a2a2a', alpha=0.8, edgecolor='white'),
               color='white')
        
        # Tight layout
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                    facecolor='#1a1a1a', edgecolor='none')
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close(fig)
        
        return chart_base64
        
    except Exception as e:
        print(f"Error creating IV skew chart: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_underlying_asset_price(date, symbol='nifty'):
    """Get the current underlying asset price (spot price) from cash tables"""
    try:
        connection = get_db_connection()
        if not connection:
            print("Failed to connect to database for underlying price")
            return None
            
        cursor = connection.cursor()
        db_date = convert_date_to_db_format(date)
        
        if not db_date:
            print("Invalid date format for underlying price")
            cursor.close()
            connection.close()
            return None
        
        # Map symbols to cash tables
        cash_table_map = {
            'nifty': 'nifty_cash',
            'banknifty': 'banknifty_cash', 
            'midcpnifty': 'midcpnifty_cash',
            'sensex': 'sensex_cash'
        }
        
        cash_table = cash_table_map.get(symbol, 'nifty_cash')
        print(f"Looking for underlying price in table: {cash_table} for symbol: {symbol}")
        
        # Get the latest close price (LTP) from cash table
        query = f"""
        SELECT close 
        FROM {cash_table} 
        WHERE date = %s 
        ORDER BY time DESC 
        LIMIT 1
        """
        
        cursor.execute(query, (db_date,))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if result and result[0]:
            # Apply the same scaling factor used elsewhere in the code (divide by 100)
            underlying_price = float(result[0]) / 100
            # Validate the price is reasonable
            if underlying_price > 0 and underlying_price < 1000000:  # Reasonable range check
                print(f"Retrieved underlying price for {symbol} on {date}: {underlying_price}")
                return underlying_price
            else:
                print(f"Invalid underlying price for {symbol} on {date}: {underlying_price}")
                return None
        else:
            print(f"No underlying price data found for {symbol} on {date}")
            return None
            
    except Exception as e:
        print(f"Error getting underlying asset price: {e}")
        return None

def validate_options_chain_inputs(date, symbol, expiry=None):
    """Validate inputs for options chain data retrieval"""
    try:
        # Validate date format
        datetime.strptime(date, '%Y-%m-%d')
        
        # Validate symbol
        valid_symbols = ['nifty', 'banknifty', 'midcpnifty', 'sensex']
        if symbol not in valid_symbols:
            raise ValueError(f"Invalid symbol: {symbol}")
        
        # Validate expiry if provided
        if expiry:
            datetime.strptime(expiry, '%Y-%m-%d')
        
        return True
    except ValueError as e:
        print(f"Validation error: {e}")
        return False

def validate_option_data(row):
    """Validate option data quality"""
    try:
        strike = float(row[0])
        ltp = float(row[1]) if row[1] is not None else 0
        volume = int(row[2]) if row[2] is not None else 0
        
        # Check for reasonable ranges
        if strike <= 0:
            return False
        if ltp < 0:
            return False
        if volume < 0:
            return False
            
        return True
    except (ValueError, TypeError):
        return False

def get_available_times_for_date(date, symbol, table_name):
    """Get all available times for a specific date from database"""
    try:
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        db_date = convert_date_to_db_format(date)
        
        if not db_date:
            return []
        
        query = f"SELECT DISTINCT time FROM {table_name} WHERE date = %s ORDER BY time"
        cursor.execute(query, (db_date,))
        results = cursor.fetchall()
        
        times = [row[0] for row in results if row[0] is not None]
        
        cursor.close()
        connection.close()
        
        return sorted(times)
        
    except Exception as e:
        print(f"Error getting available times: {e}")
        return []

def calculate_time_range_for_interval(interval_minutes, date, symbol, table_name):
    """Calculate time range for historical data with 100% success rate"""
    try:
        # Get all available times for the date
        available_times = get_available_times_for_date(date, symbol, table_name)
        
        if not available_times:
            return None, None, "No data available for this date"
        
        # Get the latest time
        latest_time = max(available_times)
        
        # Calculate start time for the interval
        start_time = latest_time - (interval_minutes * 60)  # Convert minutes to seconds
        
        # Ensure start_time is not negative
        if start_time < 0:
            start_time = min(available_times)
        
        # Find the closest available start time
        closest_start_time = min(available_times, key=lambda x: abs(x - start_time))
        
        return closest_start_time, latest_time, "Success"
        
    except Exception as e:
        print(f"Error calculating time range: {e}")
        return None, None, f"Error: {str(e)}"

@app.route('/get_options_chain_data')
def get_options_chain_data():
    """Get options chain data for a specific date, symbol, and expiry - CLEAN IMPLEMENTATION"""
    date = request.args.get('date')
    symbol = request.args.get('symbol', 'nifty')
    expiry = request.args.get('expiry')
    time_interval = request.args.get('time_interval', 'latest')  # New parameter
    
    # Basic validation
    if not date:
        return jsonify({'error': 'Date is required'})
    
    connection = None
    cursor = None
    try:
        # Table mapping
        table_map = {
            'nifty': {'call_table': 'nifty_call', 'put_table': 'nifty_put'},
            'banknifty': {'call_table': 'banknifty_call', 'put_table': 'banknifty_put'},
            'midcpnifty': {'call_table': 'midcpnifty_call', 'put_table': 'midcpnifty_put'},
            'sensex': {'call_table': 'sensex_call', 'put_table': 'sensex_put'}
        }
        
        symbol_tables = table_map.get(symbol, table_map['nifty'])
        call_table = symbol_tables['call_table']
        put_table = symbol_tables['put_table']
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Failed to connect to database'})
        
        cursor = connection.cursor()
        db_date = convert_date_to_db_format(date)
        
        if not db_date:
            return jsonify({'error': 'Invalid date format'})
        
        # Build conditions
        base_condition = "date = %s"
        query_params = [db_date]
        
        if expiry:
            db_expiry = convert_date_to_db_format(expiry)
            base_condition += " AND expiry = %s"
            query_params.append(db_expiry)
        
        # SIMPLE QUERY: Get current day data with proper LTP calculation
        call_query = f"""
        SELECT 
            strike,
            (SELECT close FROM {call_table} t2 
             WHERE t2.strike = t1.strike AND t2.date = t1.date 
             ORDER BY t2.time DESC LIMIT 1) as ltp,
            SUM(volume) as volume,
            MIN(open) as day_open,
            MAX(close) as day_close
        FROM {call_table} t1
        WHERE {base_condition}
        GROUP BY strike 
        ORDER BY strike
        """
        
        put_query = f"""
        SELECT 
            strike,
            (SELECT close FROM {put_table} t2 
             WHERE t2.strike = t1.strike AND t2.date = t1.date 
             ORDER BY t2.time DESC LIMIT 1) as ltp,
            SUM(volume) as volume,
            MIN(open) as day_open,
            MAX(close) as day_close
        FROM {put_table} t1
        WHERE {base_condition}
        GROUP BY strike 
        ORDER BY strike
        """
        
        # Handle time interval with 100% success rate
        if time_interval == "latest":
            # Execute existing queries
            cursor.execute(call_query, query_params)
            call_results = cursor.fetchall()
            
            cursor.execute(put_query, query_params)
            put_results = cursor.fetchall()
        else:
            # Handle time interval
            try:
                interval_minutes = int(time_interval)
                if interval_minutes <= 0:
                    raise ValueError("Invalid time interval")
            except ValueError:
                # Fallback to latest data
                print(f"Invalid time interval '{time_interval}', using latest data")
                time_interval = "latest"
                # Recursive call with latest
                return get_options_chain_data()
            
            # Calculate time range
            start_time, end_time, status = calculate_time_range_for_interval(
                interval_minutes, date, symbol, call_table
            )
            
            if start_time is None:
                # Fallback to latest data
                print(f"Time interval failed ({status}), using latest data")
                time_interval = "latest"
                # Recursive call with latest
                return get_options_chain_data()
            
            # Build time-filtered conditions
            time_base_condition = "date = %s AND time BETWEEN %s AND %s"
            time_query_params = [db_date, start_time, end_time]
            
            if expiry:
                db_expiry = convert_date_to_db_format(expiry)
                time_base_condition += " AND expiry = %s"
                time_query_params.append(db_expiry)
            
            # Time-filtered call query - Fixed GROUP BY issue
            time_call_query = f"""
            SELECT 
                strike,
                MAX(close) as ltp,
                SUM(volume) as volume,
                MIN(open) as day_open,
                MAX(close) as day_close
            FROM {call_table}
            WHERE {time_base_condition}
            GROUP BY strike 
            ORDER BY strike
            """
            
            # Time-filtered put query - Fixed GROUP BY issue
            time_put_query = f"""
            SELECT 
                strike,
                MAX(close) as ltp,
                SUM(volume) as volume,
                MIN(open) as day_open,
                MAX(close) as day_close
            FROM {put_table}
            WHERE {time_base_condition}
            GROUP BY strike 
            ORDER BY strike
            """
            
            # Execute time-filtered queries
            cursor.execute(time_call_query, time_query_params)
            call_results = cursor.fetchall()
            
            cursor.execute(time_put_query, time_query_params)
            put_results = cursor.fetchall()
        
        print(f"Call results: {len(call_results)}, Put results: {len(put_results)}")
        
        # Get previous day data for comparison
        prev_date_query = f"SELECT DISTINCT date FROM {call_table} WHERE date < %s ORDER BY date DESC LIMIT 1"
        cursor.execute(prev_date_query, [db_date])
        prev_date_result = cursor.fetchone()
        
        prev_call_data = {}
        prev_put_data = {}
        
        if prev_date_result:
            prev_date = prev_date_result[0]
            print(f"Previous trading day: {prev_date}")
            
            # Get previous day call data
            prev_call_query = f"""
            SELECT strike, MAX(close) as prev_close
            FROM {call_table} 
            WHERE date = %s
            GROUP BY strike
            """
            cursor.execute(prev_call_query, [prev_date])
            prev_call_results = cursor.fetchall()
            prev_call_data = {row[0]: row[1] for row in prev_call_results}
            
            # Get previous day put data
            prev_put_query = f"""
            SELECT strike, MAX(close) as prev_close
            FROM {put_table} 
            WHERE date = %s
            GROUP BY strike
            """
            cursor.execute(prev_put_query, [prev_date])
            prev_put_results = cursor.fetchall()
            prev_put_data = {row[0]: row[1] for row in prev_put_results}
        
        # Process call options
        call_data = {}
        for row in call_results:
            strike = float(row[0])
            ltp = float(row[1]) if row[1] is not None else 0
            volume = int(row[2]) if row[2] is not None else 0
            day_open = float(row[3]) if row[3] is not None else 0
            
            # Calculate change: Current LTP vs Previous day's close (standard options chain practice)
            prev_close = prev_call_data.get(strike, 0)
            if prev_close > 0:
                change = ltp - prev_close
                change_percent = (change / prev_close) * 100
            else:
                # No previous day data - use day open as fallback
                change = ltp - day_open
                change_percent = (change / day_open) * 100 if day_open > 0 else 0
            
            call_data[strike] = {
                'ltp': ltp,
                'volume': volume,
                'change': change,
                'change_percent': change_percent
            }
            
            if ltp > 0:
                print(f"CALL - Strike {strike}: prev_close={prev_close}, ltp={ltp}, change={change:.2f}, change%={change_percent:.2f}")
        
        # Process put options
        put_data = {}
        for row in put_results:
            strike = float(row[0])
            ltp = float(row[1]) if row[1] is not None else 0
            volume = int(row[2]) if row[2] is not None else 0
            day_open = float(row[3]) if row[3] is not None else 0
            
            # Calculate change: Current LTP vs Previous day's close (standard options chain practice)
            prev_close = prev_put_data.get(strike, 0)
            if prev_close > 0:
                change = ltp - prev_close
                change_percent = (change / prev_close) * 100
            else:
                # No previous day data - use day open as fallback
                change = ltp - day_open
                change_percent = (change / day_open) * 100 if day_open > 0 else 0
            
            put_data[strike] = {
                'ltp': ltp,
                'volume': volume,
                'change': change,
                'change_percent': change_percent
            }
            
            if ltp > 0:
                print(f"PUT - Strike {strike}: prev_close={prev_close}, ltp={ltp}, change={change:.2f}, change%={change_percent:.2f}")
        
        # Build options chain
        all_strikes = sorted(set(list(call_data.keys()) + list(put_data.keys())))
        options_chain = []
        
        for strike in all_strikes:
            call_info = call_data.get(strike, {'ltp': 0, 'volume': 0, 'change': 0, 'change_percent': 0})
            put_info = put_data.get(strike, {'ltp': 0, 'volume': 0, 'change': 0, 'change_percent': 0})
            
            options_chain.append({
                'strike': strike,
                'call': call_info,
                'put': put_info
            })
        
        # Summary statistics
        call_positive = sum(1 for row in options_chain if row['call']['change'] > 0)
        call_negative = sum(1 for row in options_chain if row['call']['change'] < 0)
        call_zero = sum(1 for row in options_chain if row['call']['change'] == 0)
        
        put_positive = sum(1 for row in options_chain if row['put']['change'] > 0)
        put_negative = sum(1 for row in options_chain if row['put']['change'] < 0)
        put_zero = sum(1 for row in options_chain if row['put']['change'] == 0)
        
        print(f"SUMMARY - Call: +{call_positive}, -{call_negative}, 0{call_zero} | Put: +{put_positive}, -{put_negative}, 0{put_zero}")
        
        # Get underlying asset price
        underlying_price = get_underlying_asset_price(date, symbol)
        
        # Calculate IV Skew Analysis
        iv_skew_data = calculate_iv_skew(options_chain, underlying_price, expiry)
        
        print(f"=== OPTIONS CHAIN API RESPONSE DEBUG ===")
        print(f"Date: {date}")
        print(f"Symbol: {symbol}")
        print(f"Underlying Price: {underlying_price}")
        print(f"Total Strikes: {len(all_strikes)}")
        print(f"Options Chain Length: {len(options_chain)}")
        print(f"IV Skew Data: {iv_skew_data}")
        
        return jsonify({
            'success': True,
            'options_chain': options_chain,
            'total_strikes': len(all_strikes),
            'underlying_price': underlying_price,
            'iv_skew': iv_skew_data,
            'time_interval': time_interval,
            'time_interval_info': {
                'interval': time_interval,
                'description': f"{time_interval} minute interval" if time_interval != "latest" else "Latest data"
            }
        })
        
    except Exception as e:
        print(f"Error in get_options_chain_data: {e}")
        return jsonify({'error': str(e)})
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/get_iv_skew_chart')
def get_iv_skew_chart():
    """Generate IV Skew chart for a specific date, symbol, and expiry"""
    date = request.args.get('date')
    symbol = request.args.get('symbol', 'nifty')
    expiry = request.args.get('expiry')
    
    if not date or not expiry:
        return jsonify({'error': 'Date and expiry are required'})
    
    try:
        # Get options chain data first
        options_chain_response = get_options_chain_data()
        if isinstance(options_chain_response, tuple):
            # Handle tuple response (error case)
            return jsonify({'error': 'Failed to get options chain data'})
        
        options_chain_data = options_chain_response.get_json()
        if not options_chain_data.get('success'):
            return jsonify({'error': 'Failed to get options chain data'})
        
        options_chain = options_chain_data['options_chain']
        underlying_price = options_chain_data['underlying_price']
        
        if not options_chain or not underlying_price:
            return jsonify({'error': 'No options chain data available'})
        
        # Generate IV skew chart
        chart_base64 = create_iv_skew_chart_base64(
            options_chain, underlying_price, expiry, symbol.upper()
        )
        
        if not chart_base64:
            return jsonify({'error': 'Failed to generate IV skew chart'})
        
        return jsonify({
            'success': True,
            'chart_base64': chart_base64,
            'underlying_price': underlying_price,
            'symbol': symbol.upper(),
            'expiry': expiry,
            'date': date
        })
        
    except Exception as e:
        print(f"Error generating IV skew chart: {e}")
        return jsonify({'error': str(e)})

@app.route('/test_underlying_prices')
def test_underlying_prices():
    """Test endpoint to verify underlying price retrieval for all symbols"""
    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'Date is required'})
    
    symbols = ['nifty', 'banknifty', 'midcpnifty', 'sensex']
    results = {}
    
    for symbol in symbols:
        price = get_underlying_asset_price(date, symbol)
        results[symbol] = {
            'price': price,
            'status': 'success' if price else 'no_data'
        }
    
    return jsonify({
        'date': date,
        'results': results
    })

@app.route('/get_options_expiries')
def get_options_expiries():
    """Get available expiry dates for options on a specific date and symbol"""
    date = request.args.get('date')
    symbol = request.args.get('symbol', 'nifty')
    
    if not date:
        return jsonify({'error': 'Date is required'})
    
    try:
        # Determine table names based on symbol
        table_map = {
            'nifty': {
                'call_table': 'nifty_call',
                'put_table': 'nifty_put'
            },
            'banknifty': {
                'call_table': 'banknifty_call',
                'put_table': 'banknifty_put'
            },
            'midcpnifty': {
                'call_table': 'midcpnifty_call',
                'put_table': 'midcpnifty_put'
            },
            'sensex': {
                'call_table': 'sensex_call',
                'put_table': 'sensex_put'
            }
        }
        
        symbol_tables = table_map.get(symbol, table_map['nifty'])
        call_table = symbol_tables['call_table']
        put_table = symbol_tables['put_table']
        
        connection = get_db_connection()
        cursor = connection.cursor()
        db_date = convert_date_to_db_format(date)
        
        # Get expiries from both call and put tables
        cursor.execute(f"SELECT DISTINCT expiry FROM {call_table} WHERE date = %s UNION SELECT DISTINCT expiry FROM {put_table} WHERE date = %s ORDER BY expiry", (db_date, db_date))
        expiry_results = cursor.fetchall()
        
        # Convert expiry dates to readable format
        expiries = []
        for row in expiry_results:
            if row[0]:  # Check if expiry is not None
                readable_expiry = convert_db_date_to_readable(row[0])
                expiries.append({
                    'value': readable_expiry,
                    'display': readable_expiry
                })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'expiries': expiries
        })
        
    except Exception as e:
        print(f"Error in get_options_expiries: {e}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
