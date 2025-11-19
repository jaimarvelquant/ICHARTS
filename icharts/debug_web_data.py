#!/usr/bin/env python3
"""
Debug script to test the web application data processing
"""

import sys
import os
sys.path.append('.')

from All import get_ohlc_data_for_date, resample_ohlc_data
import pandas as pd

def debug_web_data_processing():
    """Debug the exact data processing used by the web app"""
    try:
        print("=== DEBUGGING WEB APPLICATION DATA PROCESSING ===")
        
        # Test the exact same parameters as the web app
        date = "2025-08-14"
        data_type = "banknifty_cash"
        symbol = "banknifty"
        interval_minutes = 1
        
        print(f"Parameters:")
        print(f"  date: {date}")
        print(f"  data_type: {data_type}")
        print(f"  symbol: {symbol}")
        print(f"  interval_minutes: {interval_minutes}")
        
        # Step 1: Get data from database
        print(f"\nStep 1: Fetching data from database...")
        df = get_ohlc_data_for_date(date, data_type, symbol=symbol)
        
        if df is None:
            print("ERROR: No data returned from database")
            return False
            
        print(f"Data fetched: {len(df)} records")
        
        # Step 2: Resample data
        print(f"\nStep 2: Resampling data...")
        df_resampled = resample_ohlc_data(df, interval_minutes)
        
        if df_resampled is None:
            print("ERROR: Resampling failed")
            return False
            
        print(f"Resampling completed: {len(df_resampled)} records")
        
        # Step 3: Check specific time 12:05:00
        print(f"\nStep 3: Checking 12:05:00 data...")
        time_12_05 = df_resampled[df_resampled['time_readable'] == '12:05']
        
        if len(time_12_05) > 0:
            row = time_12_05.iloc[0]
            print(f"12:05:00 OHLC values:")
            print(f"  Open: {row['open']}")
            print(f"  High: {row['high']}")
            print(f"  Low: {row['low']}")
            print(f"  Close: {row['close']}")
            
            # Expected values (after scaling by 100)
            expected_open = 5531285 / 100  # 55312.85
            expected_high = 5532255 / 100  # 55322.55
            expected_low = 5530910 / 100   # 55309.10
            expected_close = 5532255 / 100 # 55322.55
            
            print(f"\nExpected values:")
            print(f"  Open: {expected_open}")
            print(f"  High: {expected_high}")
            print(f"  Low: {expected_low}")
            print(f"  Close: {expected_close}")
            
            # Check if values match
            open_match = abs(row['open'] - expected_open) < 0.01
            high_match = abs(row['high'] - expected_high) < 0.01
            low_match = abs(row['low'] - expected_low) < 0.01
            close_match = abs(row['close'] - expected_close) < 0.01
            
            print(f"\nValues match:")
            print(f"  Open: {'✅' if open_match else '❌'}")
            print(f"  High: {'✅' if high_match else '❌'}")
            print(f"  Low: {'✅' if low_match else '❌'}")
            print(f"  Close: {'✅' if close_match else '❌'}")
            
            if open_match and high_match and low_match and close_match:
                print("\n🎉 SUCCESS: All values match expected values!")
                return True
            else:
                print("\n❌ FAILURE: Some values don't match expected values")
                
                # Additional debugging
                print(f"\nAdditional debugging:")
                print(f"  Open difference: {abs(row['open'] - expected_open):.2f}")
                print(f"  High difference: {abs(row['high'] - expected_high):.2f}")
                print(f"  Low difference: {abs(row['low'] - expected_low):.2f}")
                print(f"  Close difference: {abs(row['close'] - expected_close):.2f}")
                
                return False
        else:
            print("ERROR: No data found for 12:05:00")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_web_data_processing()
    if success:
        print("\n✅ Web application data processing is working correctly.")
    else:
        print("\n❌ Web application data processing still has issues.")
