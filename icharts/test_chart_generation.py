#!/usr/bin/env python3
"""
Test script to test chart generation directly
"""

import sys
import os
sys.path.append('.')

from All import get_ohlc_data_for_date, resample_ohlc_data, create_candlestick_chart_base64

def test_chart_generation():
    """Test chart generation directly"""
    try:
        print("=== TESTING CHART GENERATION ===")
        
        # Test parameters
        date = "2025-08-14"
        data_type = "nifty_cash"
        symbol = "nifty"
        interval_minutes = 1
        
        print(f"Parameters:")
        print(f"  date: {date}")
        print(f"  data_type: {data_type}")
        print(f"  symbol: {symbol}")
        print(f"  interval_minutes: {interval_minutes}")
        
        # Step 1: Get data
        print(f"\nStep 1: Fetching data...")
        df = get_ohlc_data_for_date(date, data_type, symbol=symbol)
        
        if df is None:
            print("ERROR: No data returned")
            return False
            
        print(f"Data fetched: {len(df)} records")
        
        # Step 2: Resample data
        print(f"\nStep 2: Resampling data...")
        df_resampled = resample_ohlc_data(df, interval_minutes)
        
        if df_resampled is None:
            print("ERROR: Resampling failed")
            return False
            
        print(f"Resampling completed: {len(df_resampled)} records")
        
        # Step 3: Generate chart
        print(f"\nStep 3: Generating chart...")
        chart_base64 = create_candlestick_chart_base64(df_resampled, date, interval_minutes, data_type, symbol)
        
        if chart_base64 is None:
            print("ERROR: Chart generation failed")
            return False
            
        print(f"Chart generated successfully: {len(chart_base64)} characters")
        
        # Step 4: Check specific time 12:05:00
        print(f"\nStep 4: Checking 12:05:00 data...")
        time_12_05 = df_resampled[df_resampled['time_readable'] == '12:05']
        
        if len(time_12_05) > 0:
            row = time_12_05.iloc[0]
            print(f"12:05:00 OHLC values:")
            print(f"  Open: {row['open']}")
            print(f"  High: {row['high']}")
            print(f"  Low: {row['low']}")
            print(f"  Close: {row['close']}")
            
            # Check if values are reasonable
            if row['low'] < 1000 or row['close'] < 1000:
                print("❌ WARNING: Low or Close values are too small!")
                return False
            else:
                print("✅ Values look reasonable")
                return True
        else:
            print("ERROR: No 12:05:00 data found")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chart_generation()
    if success:
        print("\n✅ Chart generation is working correctly.")
    else:
        print("\n❌ Chart generation has issues.")
