#!/usr/bin/env python3
"""Simple test to check data fixes"""

print("Starting simple test...")

try:
    print("Importing All module...")
    from All import get_ohlc_data_for_date
    print("Import successful!")
    
    print("Testing nifty_cash data...")
    data = get_ohlc_data_for_date('2024-01-01', 'nifty_cash', symbol='nifty')
    if data is not None:
        print(f"✓ nifty_cash data: {len(data)} rows")
        if len(data) > 0:
            print(f"  Sample: O={data.iloc[0]['open']:.2f}, H={data.iloc[0]['high']:.2f}, L={data.iloc[0]['low']:.2f}, C={data.iloc[0]['close']:.2f}")
    else:
        print("✗ nifty_cash data: No data found")
    
    print("Testing nifty_future data...")
    data = get_ohlc_data_for_date('2024-01-01', 'nifty_future', symbol='nifty')
    if data is not None:
        print(f"✓ nifty_future data: {len(data)} rows")
        if len(data) > 0:
            print(f"  Sample: O={data.iloc[0]['open']:.2f}, H={data.iloc[0]['high']:.2f}, L={data.iloc[0]['low']:.2f}, C={data.iloc[0]['close']:.2f}")
    else:
        print("✗ nifty_future data: No data found")
        
    print("Testing nifty_call data...")
    data = get_ohlc_data_for_date('2024-01-01', 'nifty_call', '25000', '2024-01-25', 'nifty')
    if data is not None:
        print(f"✓ nifty_call data: {len(data)} rows")
        if len(data) > 0:
            print(f"  Sample: O={data.iloc[0]['open']:.2f}, H={data.iloc[0]['high']:.2f}, L={data.iloc[0]['low']:.2f}, C={data.iloc[0]['close']:.2f}")
    else:
        print("✗ nifty_call data: No data found")
        
    print("Test completed!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
