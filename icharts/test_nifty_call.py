#!/usr/bin/env python3
"""
Test script for NIFTY Call Options database connection and data retrieval
"""

import mysql.connector
from datetime import datetime

def test_database_connection():
    """Test basic database connection"""
    host = "106.51.63.60"
    user = "mahesh"
    password = "mahesh_123"
    database = "historicaldb"
    
    try:
        print("🔌 Testing database connection...")
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        print("✅ Database connection successful!")
        
        cursor = connection.cursor()
        
        # Test 1: Check if nifty_call table exists
        print("\n📋 Checking if nifty_call table exists...")
        cursor.execute("SHOW TABLES LIKE 'nifty_call'")
        tables = cursor.fetchall()
        
        if tables:
            print("✅ nifty_call table found!")
            
            # Test 2: Check table structure
            print("\n🏗️  Checking table structure...")
            cursor.execute("DESCRIBE nifty_call")
            columns = cursor.fetchall()
            
            print("Table columns:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
            # Test 3: Check sample data
            print("\n📊 Checking sample data...")
            cursor.execute("SELECT COUNT(*) FROM nifty_call")
            total_records = cursor.fetchone()[0]
            print(f"Total records: {total_records}")
            
            if total_records > 0:
                # Test 4: Check available dates
                print("\n📅 Checking available dates...")
                cursor.execute("SELECT DISTINCT date FROM nifty_call ORDER BY date DESC LIMIT 5")
                dates = cursor.fetchall()
                
                print("Available dates:")
                for date in dates:
                    print(f"  - {date[0]}")
                
                # Test 5: Check available strikes for first date
                if dates:
                    first_date = dates[0][0]
                    print(f"\n🎯 Checking strikes for date: {first_date}")
                    cursor.execute("SELECT DISTINCT strike FROM nifty_call WHERE date = %s ORDER BY strike LIMIT 10", (first_date,))
                    strikes = cursor.fetchall()
                    
                    print("Available strikes:")
                    for strike in strikes:
                        print(f"  - {strike[0]}")
                    
                    # Test 6: Check sample OHLC data
                    if strikes:
                        first_strike = strikes[0][0]
                        print(f"\n📈 Checking sample OHLC data for strike: {first_strike}")
                        cursor.execute("SELECT * FROM nifty_call WHERE date = %s AND strike = %s ORDER BY time LIMIT 3", (first_date, first_strike))
                        sample_data = cursor.fetchall()
                        
                        print("Sample data:")
                        for row in sample_data:
                            print(f"  - {row}")
        
        else:
            print("❌ nifty_call table not found!")
            print("\n🔍 Checking what tables exist...")
            cursor.execute("SHOW TABLES")
            all_tables = cursor.fetchall()
            
            print("Available tables:")
            for table in all_tables:
                print(f"  - {table[0]}")
            
            # Check if there are similar tables
            print("\n🔍 Looking for tables with 'nifty' or 'call' in name...")
            cursor.execute("SHOW TABLES LIKE '%nifty%'")
            nifty_tables = cursor.fetchall()
            
            if nifty_tables:
                print("Tables with 'nifty' in name:")
                for table in nifty_tables:
                    print(f"  - {table[0]}")
            
            cursor.execute("SHOW TABLES LIKE '%call%'")
            call_tables = cursor.fetchall()
            
            if call_tables:
                print("Tables with 'call' in name:")
                for table in call_tables:
                    print(f"  - {table[0]}")
        
        cursor.close()
        connection.close()
        print("\n✅ Database test completed!")
        
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_alternative_table_names():
    """Test alternative table names that might exist"""
    host = "106.51.63.60"
    user = "mahesh"
    password = "mahesh_123"
    database = "historicaldb"
    
    alternative_tables = [
        'nifty_options',
        'nifty_calls',
        'options_data',
        'call_options',
        'nifty_ce',  # CE = Call European
        'futures_data'
    ]
    
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        
        print("\n🔍 Checking alternative table names...")
        for table_name in alternative_tables:
            cursor.execute("SHOW TABLES LIKE %s", (table_name,))
            tables = cursor.fetchall()
            
            if tables:
                print(f"✅ Found table: {table_name}")
                
                # Check structure
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                
                print(f"  Columns in {table_name}:")
                for col in columns:
                    print(f"    - {col[0]} ({col[1]})")
                
                # Check sample data
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  Total records: {count}")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")

if __name__ == "__main__":
    print("🚀 NIFTY Call Options Database Test")
    print("=" * 50)
    
    test_database_connection()
    test_alternative_table_names()
    
    print("\n" + "=" * 50)
    print("�� Test completed!")
