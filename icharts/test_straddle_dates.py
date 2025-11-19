#!/usr/bin/env python3
"""
Test script to find intersection dates for straddle strategies
"""

import mysql.connector
from datetime import datetime

def test_straddle_dates():
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
        
        print("=== STRADDLE DATES ANALYSIS ===")
        
        # Test NIFTY straddle (call + put)
        print("\n🔵 NIFTY STRADDLE (Call + Put):")
        cursor.execute("SELECT DISTINCT date FROM nifty_call ORDER BY date ASC")
        call_dates = set([row[0] for row in cursor.fetchall()])
        
        cursor.execute("SELECT DISTINCT date FROM nifty_put ORDER BY date ASC")
        put_dates = set([row[0] for row in cursor.fetchall()])
        
        # Find intersection dates
        intersection_dates = call_dates.intersection(put_dates)
        intersection_dates = sorted(list(intersection_dates))
        
        print(f"   Call dates: {len(call_dates)}")
        print(f"   Put dates: {len(put_dates)}")
        print(f"   Intersection dates: {len(intersection_dates)}")
        print(f"   Call only dates: {len(call_dates - put_dates)}")
        print(f"   Put only dates: {len(put_dates - call_dates)}")
        
        if intersection_dates:
            print(f"   First intersection date: {intersection_dates[0]}")
            print(f"   Last intersection date: {intersection_dates[-1]}")
        
        # Test BANKNIFTY straddle
        print("\n🟡 BANKNIFTY STRADDLE (Call + Put):")
        cursor.execute("SELECT DISTINCT date FROM banknifty_call ORDER BY date ASC")
        call_dates = set([row[0] for row in cursor.fetchall()])
        
        cursor.execute("SELECT DISTINCT date FROM banknifty_put ORDER BY date ASC")
        put_dates = set([row[0] for row in cursor.fetchall()])
        
        intersection_dates = call_dates.intersection(put_dates)
        intersection_dates = sorted(list(intersection_dates))
        
        print(f"   Call dates: {len(call_dates)}")
        print(f"   Put dates: {len(put_dates)}")
        print(f"   Intersection dates: {len(intersection_dates)}")
        
        # Test MIDCPNIFTY straddle
        print("\n🟢 MIDCPNIFTY STRADDLE (Call + Put):")
        cursor.execute("SELECT DISTINCT date FROM midcpnifty_call ORDER BY date ASC")
        call_dates = set([row[0] for row in cursor.fetchall()])
        
        cursor.execute("SELECT DISTINCT date FROM midcpnifty_put ORDER BY date ASC")
        put_dates = set([row[0] for row in cursor.fetchall()])
        
        intersection_dates = call_dates.intersection(put_dates)
        intersection_dates = sorted(list(intersection_dates))
        
        print(f"   Call dates: {len(call_dates)}")
        print(f"   Put dates: {len(put_dates)}")
        print(f"   Intersection dates: {len(intersection_dates)}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_straddle_dates()
