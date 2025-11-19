#!/usr/bin/env python3
"""Test script to verify data type fixes"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'icharts'))

from All import get_ohlc_data_for_date, resample_ohlc_data
import pandas as pd

def test_data_types():
    """Test all data types to ensure they work properly"""
    print("=== Testing Data Type Fixes ===\n")
    
    # Test dates - try a few different ones
    test_dates = ['2024-01-01', '2023-12-01', '2023-11-01']
    
    for date in test_dates:
        print(f"Testing date: {date}")
        
        # Test call data
        print("  Testing nifty_call...")
        call_data = get_ohlc_data_for_date(date, 'nifty_call', '25000', '2024-01-25', 'nifty')
        if call_data is not None and len(call_data) > 0:
            print(f"    ✓ Call data: {len(call_data)} rows")
            print(f"    Sample OHLC: O={call_data.iloc[0]['open']:.2f}, H={call_data.iloc[0]['high']:.2f}, L={call_data.iloc[0]['low']:.2f}, C={call_data.iloc[0]['close']:.2f}")
        else:
            print("    ✗ Call data: No data found")
        
        # Test put data
        print("  Testing nifty_put...")
        put_data = get_ohlc_data_for_date(date, 'nifty_put', '25000', '2024-01-25', 'nifty')
        if put_data is not None and len(put_data) > 0:
            print(f"    ✓ Put data: {len(put_data)} rows")
            print(f"    Sample OHLC: O={put_data.iloc[0]['open']:.2f}, H={put_data.iloc[0]['high']:.2f}, L={put_data.iloc[0]['low']:.2f}, C={put_data.iloc[0]['close']:.2f}")
        else:
            print("    ✗ Put data: No data found")
        
        # Test spot data
        print("  Testing nifty_cash...")
        spot_data = get_ohlc_data_for_date(date, 'nifty_cash', symbol='nifty')
        if spot_data is not None and len(spot_data) > 0:
            print(f"    ✓ Spot data: {len(spot_data)} rows")
            print(f"    Sample OHLC: O={spot_data.iloc[0]['open']:.2f}, H={spot_data.iloc[0]['high']:.2f}, L={spot_data.iloc[0]['low']:.2f}, C={spot_data.iloc[0]['close']:.2f}")
        else:
            print("    ✗ Spot data: No data found")
        
        # Test future data
        print("  Testing nifty_future...")
        future_data = get_ohlc_data_for_date(date, 'nifty_future', symbol='nifty')
        if future_data is not None and len(future_data) > 0:
            print(f"    ✓ Future data: {len(future_data)} rows")
            print(f"    Sample OHLC: O={future_data.iloc[0]['open']:.2f}, H={future_data.iloc[0]['high']:.2f}, L={future_data.iloc[0]['low']:.2f}, C={future_data.iloc[0]['close']:.2f}")
        else:
            print("    ✗ Future data: No data found")
        
        print()

if __name__ == "__main__":
    test_data_types()
