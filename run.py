#!/usr/bin/env python3
"""
Startup script for Voice-Enabled Chart Creator
This script handles the startup process and provides helpful information.
"""

import os
import sys
import subprocess
import webbrowser
import time

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'flask', 'pandas', 'plotly', 'numpy', 'matplotlib', 'seaborn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\n📦 Installing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies.")
            print("Please run manually: pip install -r requirements.txt")
            return False
    
    return True

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = ['uploads', 'datasets', 'templates']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")

def start_application():
    """Start the Flask application"""
    print("\n🚀 Starting Voice-Enabled Chart Creator...")
    print("=" * 50)
    
    # Check if templates directory exists and has the HTML file
    if not os.path.exists('templates/index.html'):
        print("❌ Error: templates/index.html not found!")
        print("Make sure all project files are in place.")
        return False
    
    # Create necessary directories
    create_directories()
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    print("\n✅ All checks passed!")
    print("\n🎯 Starting the application...")
    print("📱 The web interface will open automatically in your browser")
    print("🎤 Microphone access will be requested for voice commands")
    print("\n💡 Voice Command Examples:")
    print("   • 'Show me the sales dataset'")
    print("   • 'Create a bar chart'")
    print("   • 'Use month and sales for axes'")
    print("   • 'Add colors by region'")
    
    # Wait a moment for user to read
    time.sleep(3)
    
    # Open browser automatically
    try:
        webbrowser.open('http://localhost:5000')
        print("\n🌐 Opening browser...")
    except:
        print("\n🌐 Please open your browser and go to: http://localhost:5000")
    
    # Start the Flask app
    try:
        from app import app
        print("\n🎉 Application started successfully!")
        print("📍 Access at: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the application")
        print("\n" + "="*50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False

def main():
    """Main function"""
    print("🎤 Voice-Enabled Chart Creator")
    print("=" * 35)
    print("A real-time, interactive chart creation app")
    print("that responds to voice commands!")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found!")
        print("Please run this script from the project directory.")
        return
    
    # Start the application
    try:
        start_application()
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
        print("👋 Thanks for using Voice Chart Creator!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the error and try again.")

if __name__ == "__main__":
    main()