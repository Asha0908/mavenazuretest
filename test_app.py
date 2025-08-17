#!/usr/bin/env python3
"""
Test script for Voice-Enabled Chart Creator
Tests the core functionality and API endpoints.
"""

import requests
import json
import time
import sys

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Voice Chart Creator API")
    print("=" * 40)
    
    # Test 1: Check if server is running
    print("\n1️⃣ Testing server availability...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running with: python app.py")
        return False
    
    # Test 2: Get available datasets
    print("\n2️⃣ Testing datasets endpoint...")
    try:
        response = requests.get(f"{base_url}/api/datasets", timeout=5)
        if response.status_code == 200:
            datasets = response.json()
            print(f"✅ Found {len(datasets)} datasets:")
            for dataset in datasets:
                print(f"   • {dataset['name']} ({dataset['type']})")
        else:
            print(f"❌ Datasets endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing datasets: {e}")
        return False
    
    # Test 3: Get specific dataset
    print("\n3️⃣ Testing dataset retrieval...")
    try:
        response = requests.get(f"{base_url}/api/dataset/sales", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Sales dataset loaded: {data['shape'][0]} rows, {data['shape'][1]} columns")
            else:
                print(f"❌ Dataset loading failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Dataset endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing dataset retrieval: {e}")
        return False
    
    # Test 4: Test voice command processing
    print("\n4️⃣ Testing voice command processing...")
    try:
        test_command = "show me the sales dataset"
        response = requests.post(f"{base_url}/api/voice-command", 
                               json={"command": test_command}, 
                               timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Voice command processed: {data['message']}")
                if data['suggestions']:
                    print(f"   Suggestions: {', '.join(data['suggestions'])}")
            else:
                print(f"❌ Voice command failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Voice command endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing voice commands: {e}")
        return False
    
    # Test 5: Test chart generation
    print("\n5️⃣ Testing chart generation...")
    try:
        chart_data = {
            "dataset_id": "sales",
            "chart_type": "bar",
            "x_column": "Month",
            "y_column": "Sales",
            "color_column": "Region",
            "title": "Test Sales Chart"
        }
        
        response = requests.post(f"{base_url}/api/chart", 
                               json=chart_data, 
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ Chart generated successfully!")
                print(f"   Dataset info: {data['dataset_info']['rows']} rows, {len(data['dataset_info']['columns'])} columns")
            else:
                print(f"❌ Chart generation failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Chart endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing chart generation: {e}")
        return False
    
    print("\n🎉 All tests passed! The application is working correctly.")
    return True

def test_demo_mode():
    """Test the demo script functionality"""
    print("\n🎬 Testing Demo Mode")
    print("=" * 25)
    
    try:
        # Import and run demo functions
        from demo import demo_chart_creation, demo_voice_commands
        
        print("✅ Demo functions imported successfully")
        print("💡 Run 'python demo.py' to see the demo in action")
        
    except ImportError as e:
        print(f"❌ Demo import failed: {e}")
        print("Make sure all dependencies are installed")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Voice-Enabled Chart Creator - Test Suite")
    print("=" * 50)
    
    # Check if required packages are installed
    try:
        import flask
        import pandas
        import plotly
        print("✅ All required packages are installed")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Install dependencies with: pip install -r requirements.txt")
        return False
    
    # Test demo mode
    if not test_demo_mode():
        return False
    
    # Test API endpoints (only if server is running)
    print("\n🌐 Testing API endpoints...")
    print("Note: This requires the Flask server to be running")
    print("Start the server with: python app.py")
    
    choice = input("\nDo you want to test the API endpoints? (y/n): ").lower().strip()
    
    if choice in ['y', 'yes']:
        if test_api_endpoints():
            print("\n🎊 All tests completed successfully!")
            print("\nYour Voice-Enabled Chart Creator is ready to use!")
            print("\nNext steps:")
            print("1. Open a new terminal")
            print("2. Run: python app.py")
            print("3. Open browser: http://localhost:5000")
            print("4. Start creating charts with your voice! 🎤")
        else:
            print("\n❌ Some tests failed. Check the errors above.")
    else:
        print("\n✅ Basic tests completed. API tests skipped.")
        print("\nTo test the full application:")
        print("1. Run: python app.py")
        print("2. Open browser: http://localhost:5000")
        print("3. Test voice commands and chart generation!")

if __name__ == "__main__":
    main()