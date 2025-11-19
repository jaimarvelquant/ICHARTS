#!/usr/bin/env python3
"""
Comprehensive test for all symbols and their data types
"""

import mysql.connector
from datetime import datetime

def test_all_symbols():
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
        
        print("=== TESTING ALL SYMBOLS AND DATA TYPES ===")
        
        # Test NIFTY
        print("\n🔵 NIFTY SYMBOL:")
        symbols = ['nifty_cash', 'nifty_future', 'nifty_call', 'nifty_put']
        for symbol in symbols:
            try:
                cursor.execute(f"SELECT DISTINCT date FROM {symbol} ORDER BY date ASC")
                dates = cursor.fetchall()
                if dates:
                    print(f"   {symbol}: {len(dates)} trading days ({dates[0][0]} to {dates[-1][0]})")
                else:
                    print(f"   {symbol}: No data")
            except Exception as e:
                print(f"   {symbol}: Error - {e}")
        
        # Test BANKNIFTY
        print("\n🟡 BANKNIFTY SYMBOL:")
        symbols = ['banknifty_cash', 'banknifty_future', 'banknifty_call', 'banknifty_put']
        for symbol in symbols:
            try:
                cursor.execute(f"SELECT DISTINCT date FROM {symbol} ORDER BY date ASC")
                dates = cursor.fetchall()
                if dates:
                    print(f"   {symbol}: {len(dates)} trading days ({dates[0][0]} to {dates[-1][0]})")
                else:
                    print(f"   {symbol}: No data")
            except Exception as e:
                print(f"   {symbol}: Error - {e}")
        
        # Test MIDCPNIFTY
        print("\n🟢 MIDCPNIFTY SYMBOL:")
        symbols = ['midcpnifty_cash', 'midcpnifty_future', 'midcpnifty_call', 'midcpnifty_put']
        for symbol in symbols:
            try:
                cursor.execute(f"SELECT DISTINCT date FROM {symbol} ORDER BY date ASC")
                dates = cursor.fetchall()
                if dates:
                    print(f"   {symbol}: {len(dates)} trading days ({dates[0][0]} to {dates[-1][0]})")
                else:
                    print(f"   {symbol}: No data")
            except Exception as e:
                print(f"   {symbol}: Error - {e}")
        
        # Test SENSEX
        print("\n🔴 SENSEX SYMBOL:")
        symbols = ['sensex_cash', 'sensex_future', 'sensex_call', 'sensex_put']
        for symbol in symbols:
            try:
                cursor.execute(f"SELECT DISTINCT date FROM {symbol} ORDER BY date ASC")
                dates = cursor.fetchall()
                if dates:
                    print(f"   {symbol}: {len(dates)} trading days ({dates[0][0]} to {dates[-1][0]})")
                else:
                    print(f"   {symbol}: No data")
            except Exception as e:
                print(f"   {symbol}: Error - {e}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_all_symbols()
