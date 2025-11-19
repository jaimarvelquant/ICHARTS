#!/usr/bin/env python3
"""
Test script to verify the fix for August 2025 data
"""

import sys
import os
sys.path.append('.')

from All import get_ohlc_data_for_date, resample_ohlc_data

def test_august_data():
    """Test August 14, 2025 data processing"""
    try:
        print("=== TESTING AUGUST 2025 DATA FIX ===")
        
        # Test date: August 14, 2025
        test_date = "2025-08-14"
        data_type = "banknifty_cash"
        symbol = "banknifty"
        
        print(f"Fetching data for {test_date}...")
        df = get_ohlc_data_for_date(test_date, data_type, symbol=symbol)
        
        if df is None:
            print("ERROR: No data returned from database")
            return False
            
        print(f"Data fetched successfully: {len(df)} records")
        
        # Test resampling
        print("Testing resampling...")
        resampled_df = resample_ohlc_data(df, 1)  # 1-minute intervals
        
        if resampled_df is None:
            print("ERROR: Resampling failed")
            return False
            
        print(f"Resampling successful: {len(resampled_df)} records")
        
        # Check the specific time 12:05:00
        print("\nChecking 12:05:00 data...")
        time_12_05 = resampled_df[resampled_df['time_readable'] == '12:05']
        
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
            print(f"  Open: {'OK' if open_match else 'FAIL'}")
            print(f"  High: {'OK' if high_match else 'FAIL'}")
            print(f"  Low: {'OK' if low_match else 'FAIL'}")
            print(f"  Close: {'OK' if close_match else 'FAIL'}")
            
            if open_match and high_match and low_match and close_match:
                print("\nSUCCESS: All values match expected values!")
                return True
            else:
                print("\nFAILURE: Some values don't match expected values")
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
    success = test_august_data()
    if success:
        print("\nTest passed! The fix is working correctly.")
    else:
        print("\nTest failed! The issue persists.")
