#!/usr/bin/env python3
"""
Demo script for Voice-Enabled Chart Creator
This script demonstrates the core functionality without running the full web server.
"""

import pandas as pd
import json
from app import SAMPLE_DATASETS, create_chart

def demo_chart_creation():
    """Demonstrate chart creation with sample datasets"""
    print("🎤 Voice-Enabled Chart Creator - Demo Mode")
    print("=" * 50)
    
    # Show available datasets
    print("\n📊 Available Sample Datasets:")
    for key, dataset in SAMPLE_DATASETS.items():
        print(f"  • {dataset['name']} ({key})")
        print(f"    Columns: {', '.join(dataset['columns'])}")
        print(f"    Rows: {len(dataset['data'])}")
        print()
    
    # Demo 1: Sales Bar Chart
    print("📈 Demo 1: Sales Bar Chart")
    print("-" * 30)
    
    sales_df = pd.DataFrame(SAMPLE_DATASETS['sales']['data'], 
                           columns=SAMPLE_DATASETS['sales']['columns'])
    
    print(f"Dataset: {SAMPLE_DATASETS['sales']['name']}")
    print(f"Data:\n{sales_df}")
    print()
    
    # Create bar chart
    chart_json = create_chart(sales_df, 'bar', 'Month', 'Sales', 'Region', 'Monthly Sales by Region')
    print("✅ Bar chart generated successfully!")
    print(f"Chart data length: {len(chart_json)} characters")
    print()
    
    # Demo 2: Weather Line Chart
    print("🌤️ Demo 2: Weather Line Chart")
    print("-" * 30)
    
    weather_df = pd.DataFrame(SAMPLE_DATASETS['weather']['data'], 
                             columns=SAMPLE_DATASETS['weather']['columns'])
    
    print(f"Dataset: {SAMPLE_DATASETS['weather']['name']}")
    print(f"Data:\n{weather_df}")
    print()
    
    # Create line chart
    chart_json = create_chart(weather_df, 'line', 'Date', 'Temperature', 'City', 'Temperature Over Time by City')
    print("✅ Line chart generated successfully!")
    print(f"Chart data length: {len(chart_json)} characters")
    print()
    
    # Demo 3: Student Performance Scatter Plot
    print("🎓 Demo 3: Student Performance Scatter Plot")
    print("-" * 40)
    
    students_df = pd.DataFrame(SAMPLE_DATASETS['students']['data'], 
                              columns=SAMPLE_DATASETS['students']['columns'])
    
    print(f"Dataset: {SAMPLE_DATASETS['students']['name']}")
    print(f"Data:\n{students_df}")
    print()
    
    # Create scatter plot
    chart_json = create_chart(students_df, 'scatter', 'Math', 'Science', 'Grade', 'Math vs Science Scores by Grade')
    print("✅ Scatter plot generated successfully!")
    print(f"Chart data length: {len(chart_json)} characters")
    print()
    
    # Demo 4: Pie Chart
    print("🥧 Demo 4: Sales Distribution Pie Chart")
    print("-" * 35)
    
    # Aggregate sales by product
    sales_by_product = sales_df.groupby('Product')['Sales'].sum().reset_index()
    print(f"Aggregated data:\n{sales_by_product}")
    print()
    
    # Create pie chart
    chart_json = create_chart(sales_by_product, 'pie', 'Product', 'Sales', None, 'Sales Distribution by Product')
    print("✅ Pie chart generated successfully!")
    print(f"Chart data length: {len(chart_json)} characters")
    print()
    
    print("🎉 All demos completed successfully!")
    print("\nTo run the full application:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the app: python app.py")
    print("3. Open browser: http://localhost:5000")
    print("4. Use voice commands or manual controls to create charts!")

def demo_voice_commands():
    """Show example voice commands that would work in the web app"""
    print("\n🎤 Voice Command Examples:")
    print("=" * 30)
    
    commands = [
        "Show me the sales dataset",
        "Create a bar chart",
        "Use month for X axis and sales for Y axis",
        "Add colors by region",
        "Title it Monthly Sales Overview",
        "Show me the weather data",
        "Create a line chart",
        "Use temperature and humidity",
        "Color by city",
        "Show student performance",
        "Create a scatter plot",
        "Use math and science scores"
    ]
    
    for i, command in enumerate(commands, 1):
        print(f"{i:2d}. \"{command}\"")
    
    print("\n💡 Tips:")
    print("• Speak clearly and naturally")
    print("• Use specific dataset names (sales, weather, students)")
    print("• Specify chart types (bar, line, scatter, pie, histogram)")
    print("• Mention column names for axes and colors")

if __name__ == "__main__":
    try:
        demo_chart_creation()
        demo_voice_commands()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")