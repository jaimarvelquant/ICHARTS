#!/usr/bin/env python3
"""
Debug script to check database data for August 14, 2025
"""

import mysql.connector
import pandas as pd
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': "106.51.63.60",
    'user': "mahesh",
    'password': "mahesh_123",
    'database': "historicaldb"
}

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

def debug_august_data():
    """Debug August 14, 2025 data"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Test date: August 14, 2025
        test_date = "2025-08-14"
        db_date = convert_date_to_db_format(test_date)
        
        print(f"=== DEBUGGING AUGUST 2025 DATA ===")
        print(f"Test date: {test_date}")
        print(f"Database date format: {db_date}")
        
        # Check if data exists for this date
        cursor.execute("SELECT COUNT(*) FROM banknifty_cash WHERE date = %s", (db_date,))
        count = cursor.fetchone()[0]
        print(f"Total records for {test_date}: {count}")
        
        if count > 0:
            # Get first few records
            cursor.execute("SELECT * FROM banknifty_cash WHERE date = %s ORDER BY time LIMIT 5", (db_date,))
            results = cursor.fetchall()
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            print(f"Columns: {columns}")
            
            print(f"\nFirst 5 records:")
            for i, row in enumerate(results):
                print(f"Record {i+1}:")
                for j, col in enumerate(columns):
                    if col in ['open', 'high', 'low', 'close']:
                        print(f"  {col}: {row[j]}")
                    elif col == 'time':
                        readable_time = convert_db_time_to_readable(row[j])
                        print(f"  {col}: {row[j]} ({readable_time})")
                    else:
                        print(f"  {col}: {row[j]}")
                print()
            
            # Check for the specific time 43500 (12:05:00)
            cursor.execute("SELECT * FROM banknifty_cash WHERE date = %s AND time = %s", (db_date, 43500))
            specific_result = cursor.fetchone()
            
            if specific_result:
                print(f"Specific record for time 43500 (12:05:00):")
                for j, col in enumerate(columns):
                    if col in ['open', 'high', 'low', 'close']:
                        print(f"  {col}: {specific_result[j]}")
                    elif col == 'time':
                        readable_time = convert_db_time_to_readable(specific_result[j])
                        print(f"  {col}: {specific_result[j]} ({readable_time})")
                    else:
                        print(f"  {col}: {specific_result[j]}")
            else:
                print("No record found for time 43500 (12:05:00)")
                
        else:
            print(f"No data found for {test_date}")
            
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_august_data()