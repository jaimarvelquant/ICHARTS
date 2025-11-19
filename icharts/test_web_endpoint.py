#!/usr/bin/env python3
"""
Test script to test the web application endpoint directly
"""

import requests
import json

def test_web_endpoint():
    """Test the web application endpoint"""
    try:
        print("=== TESTING WEB APPLICATION ENDPOINT ===")
        
        # Test the generate_chart endpoint
        url = "http://localhost:5000/generate_chart"
        
        # Prepare form data
        form_data = {
            'date': '2025-08-14',
            'chart_type': 'candlestick',
            'timeframe': '1',
            'data_type': 'banknifty_cash',
            'symbol': 'banknifty'
        }
        
        print(f"Testing endpoint: {url}")
        print(f"Form data: {form_data}")
        
        # Make POST request
        response = requests.post(url, data=form_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response received successfully")
            
            if 'chart_data' in result:
                chart_data = result['chart_data']
                print(f"Chart data length: {len(chart_data)}")
                
                # Find 12:05:00 data
                time_12_05 = [item for item in chart_data if item['time'] == '12:05']
                
                if time_12_05:
                    data = time_12_05[0]
                    print(f"\n12:05:00 OHLC values from web app:")
                    print(f"  Open: {data['open']}")
                    print(f"  High: {data['high']}")
                    print(f"  Low: {data['low']}")
                    print(f"  Close: {data['close']}")
                    
                    # Expected values
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
                    open_match = abs(data['open'] - expected_open) < 0.01
                    high_match = abs(data['high'] - expected_high) < 0.01
                    low_match = abs(data['low'] - expected_low) < 0.01
                    close_match = abs(data['close'] - expected_close) < 0.01
                    
                    print(f"\nValues match:")
                    print(f"  Open: {'✅' if open_match else '❌'}")
                    print(f"  High: {'✅' if high_match else '❌'}")
                    print(f"  Low: {'✅' if low_match else '❌'}")
                    print(f"  Close: {'✅' if close_match else '❌'}")
                    
                    if open_match and high_match and low_match and close_match:
                        print("\n🎉 SUCCESS: Web application is working correctly!")
                        return True
                    else:
                        print("\n❌ FAILURE: Web application still has issues")
                        return False
                else:
                    print("ERROR: No 12:05:00 data found in chart data")
                    return False
            else:
                print("ERROR: No chart_data in response")
                print(f"Response: {result}")
                return False
        else:
            print(f"ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_web_endpoint()
    if success:
        print("\n✅ Web application endpoint is working correctly.")
    else:
        print("\n❌ Web application endpoint still has issues.")
