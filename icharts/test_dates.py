#!/usr/bin/env python3
"""
Quick test to debug the date issue in straddle chart
"""

import mysql.connector
from datetime import datetime

def test_dates():
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
        
        print("=== TESTING DATES ===")
        
        # Test nifty_call table
        print("\n1. Testing nifty_call table:")
        cursor.execute("SELECT DISTINCT date FROM nifty_call ORDER BY date ASC")
        call_dates = cursor.fetchall()
        print(f"   Total unique dates: {len(call_dates)}")
        if call_dates:
            print(f"   First date: {call_dates[0][0]}")
            print(f"   Last date: {call_dates[-1][0]}")
        
        # Test nifty_cash table
        print("\n2. Testing nifty_cash table:")
        cursor.execute("SELECT DISTINCT date FROM nifty_cash ORDER BY date ASC")
        cash_dates = cursor.fetchall()
        print(f"   Total unique dates: {len(cash_dates)}")
        if cash_dates:
            print(f"   First date: {cash_dates[0][0]}")
            print(f"   Last date: {cash_dates[-1][0]}")
        
        # Test nifty_put table
        print("\n3. Testing nifty_put table:")
        cursor.execute("SELECT DISTINCT date FROM nifty_put ORDER BY date ASC")
        put_dates = cursor.fetchall()
        print(f"   Total unique dates: {len(put_dates)}")
        if put_dates:
            print(f"   First date: {put_dates[0][0]}")
            print(f"   Last date: {put_dates[-1][0]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_dates()
