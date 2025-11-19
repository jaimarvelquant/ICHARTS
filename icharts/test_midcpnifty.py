#!/usr/bin/env python3
"""
Quick test to check midcpnifty database data
"""

import mysql.connector
from datetime import datetime

def test_midcpnifty():
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
        
        print("=== TESTING MIDCPNIFTY DATES ===")
        
        # Test midcpnifty_cash table
        print("\n1. Testing midcpnifty_cash table:")
        cursor.execute("SELECT DISTINCT date FROM midcpnifty_cash ORDER BY date ASC")
        cash_dates = cursor.fetchall()
        print(f"   Total unique dates: {len(cash_dates)}")
        if cash_dates:
            print(f"   First date: {cash_dates[0][0]}")
            print(f"   Last date: {cash_dates[-1][0]}")
        
        # Test midcpnifty_call table
        print("\n2. Testing midcpnifty_call table:")
        cursor.execute("SELECT DISTINCT date FROM midcpnifty_call ORDER BY date ASC")
        call_dates = cursor.fetchall()
        print(f"   Total unique dates: {len(call_dates)}")
        if call_dates:
            print(f"   First date: {call_dates[0][0]}")
            print(f"   Last date: {call_dates[-1][0]}")
        
        # Test midcpnifty_put table
        print("\n3. Testing midcpnifty_put table:")
        cursor.execute("SELECT DISTINCT date FROM midcpnifty_put ORDER BY date ASC")
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
    test_midcpnifty()
