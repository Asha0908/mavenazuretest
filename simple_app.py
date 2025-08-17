#!/usr/bin/env python3
"""
Simplified Voice-Enabled Chart Creator
This version works with minimal dependencies and can be easily run.
"""

import json
import os
from datetime import datetime

# Sample datasets (built-in)
SAMPLE_DATASETS = {
    'sales': {
        'name': 'Sales Data',
        'description': 'Monthly sales data for different products',
        'columns': ['Month', 'Product', 'Sales', 'Region'],
        'data': [
            ['Jan', 'Laptop', 1200, 'North'],
            ['Jan', 'Phone', 800, 'North'],
            ['Feb', 'Laptop', 1400, 'South'],
            ['Feb', 'Phone', 900, 'South'],
            ['Mar', 'Laptop', 1100, 'East'],
            ['Mar', 'Phone', 1000, 'East']
        ]
    },
    'weather': {
        'name': 'Weather Data',
        'description': 'Daily temperature and humidity data',
        'columns': ['Date', 'Temperature', 'Humidity', 'City'],
        'data': [
            ['2024-01-01', 25, 60, 'Mumbai'],
            ['2024-01-02', 28, 55, 'Mumbai'],
            ['2024-01-03', 30, 50, 'Delhi'],
            ['2024-01-04', 32, 45, 'Delhi'],
            ['2024-01-05', 27, 65, 'Chennai'],
            ['2024-01-06', 29, 58, 'Chennai']
        ]
    },
    'students': {
        'name': 'Student Performance',
        'description': 'Student scores in different subjects',
        'columns': ['Student', 'Math', 'Science', 'English', 'Grade'],
        'data': [
            ['Alice', 85, 90, 88, 'A'],
            ['Bob', 78, 85, 92, 'B'],
            ['Charlie', 92, 88, 85, 'A'],
            ['Diana', 75, 80, 78, 'C'],
            ['Eve', 88, 92, 90, 'A'],
            ['Frank', 82, 78, 85, 'B']
        ]
    }
}

def create_simple_chart(data, chart_type, x_column, y_column, color_column=None, title=None):
    """Create a simple text-based chart representation"""
    
    if not title:
        title = f"{y_column} by {x_column}"
    
    chart_output = []
    chart_output.append(f"📊 {title}")
    chart_output.append("=" * (len(title) + 4))
    chart_output.append("")
    
    if chart_type.lower() in ['bar', 'bar chart']:
        # Group data by x_column
        grouped_data = {}
        for row in data:
            x_val = row[data['columns'].index(x_column)]
            y_val = row[data['columns'].index(y_column)]
            if x_val not in grouped_data:
                grouped_data[x_val] = 0
            grouped_data[x_val] += y_val
        
        # Find max value for scaling
        max_val = max(grouped_data.values()) if grouped_data else 1
        
        # Create bar chart
        for x_val, y_val in sorted(grouped_data.items()):
            bar_length = int((y_val / max_val) * 40)  # Scale to 40 characters
            bar = "█" * bar_length
            chart_output.append(f"{x_val:10} | {bar} {y_val}")
    
    elif chart_type.lower() in ['line', 'line chart']:
        # Simple line chart representation
        chart_output.append("Line Chart Data Points:")
        for row in data:
            x_val = row[data['columns'].index(x_column)]
            y_val = row[data['columns'].index(y_column)]
            chart_output.append(f"  {x_val} → {y_val}")
    
    elif chart_type.lower() in ['pie', 'pie chart']:
        # Calculate percentages
        total = sum(row[data['columns'].index(y_column)] for row in data)
        chart_output.append("Pie Chart Distribution:")
        for row in data:
            x_val = row[data['columns'].index(x_column)]
            y_val = row[data['columns'].index(y_column)]
            percentage = (y_val / total) * 100
            chart_output.append(f"  {x_val}: {percentage:.1f}% ({y_val})")
    
    elif chart_type.lower() in ['scatter', 'scatter plot']:
        chart_output.append("Scatter Plot Data Points:")
        for row in data:
            x_val = row[data['columns'].index(x_column)]
            y_val = row[data['columns'].index(y_column)]
            chart_output.append(f"  ({x_val}, {y_val})")
    
    else:
        # Default to table view
        chart_output.append("Data Table:")
        chart_output.append("-" * 50)
        chart_output.append(f"{x_column:15} | {y_column:15}")
        chart_output.append("-" * 50)
        for row in data:
            x_val = row[data['columns'].index(x_column)]
            y_val = row[data['columns'].index(y_column)]
            chart_output.append(f"{str(x_val):15} | {str(y_val):15}")
    
    return "\n".join(chart_output)

def process_voice_command(command):
    """Process voice commands and return chart configuration"""
    command = command.lower()
    
    response = {
        'success': True,
        'message': '',
        'suggestions': [],
        'chart_config': {}
    }
    
    if 'dataset' in command or 'data' in command:
        if 'sales' in command:
            response['message'] = 'I found the sales dataset. What type of chart would you like?'
            response['suggestions'] = ['bar chart', 'line chart', 'pie chart']
            response['chart_config'] = {'dataset_id': 'sales'}
        elif 'weather' in command:
            response['message'] = 'I found the weather dataset. What type of chart would you like?'
            response['suggestions'] = ['line chart', 'scatter plot', 'bar chart']
            response['chart_config'] = {'dataset_id': 'weather'}
        elif 'student' in command or 'performance' in command:
            response['message'] = 'I found the student performance dataset. What type of chart would you like?'
            response['suggestions'] = ['bar chart', 'scatter plot', 'histogram']
            response['chart_config'] = {'dataset_id': 'students'}
        else:
            response['message'] = 'I have several datasets available: sales, weather, and student performance. Which one would you like to use?'
            response['suggestions'] = ['sales', 'weather', 'students']
    
    elif 'chart' in command or 'graph' in command:
        if 'bar' in command:
            response['message'] = 'Great! I\'ll create a bar chart. Which columns should I use for X and Y axes?'
            response['chart_config'] = {'chart_type': 'bar'}
        elif 'line' in command:
            response['message'] = 'Perfect! I\'ll create a line chart. Which columns should I use for X and Y axes?'
            response['chart_config'] = {'chart_type': 'line'}
        elif 'pie' in command:
            response['message'] = 'Excellent choice! I\'ll create a pie chart. Which column should I use for the values?'
            response['chart_config'] = {'chart_type': 'pie'}
        elif 'scatter' in command:
            response['message'] = 'Great! I\'ll create a scatter plot. Which columns should I use for X and Y axes?'
            response['chart_config'] = {'chart_type': 'scatter'}
        else:
            response['message'] = 'I can create bar charts, line charts, pie charts, scatter plots, and histograms. Which type would you prefer?'
            response['suggestions'] = ['bar chart', 'line chart', 'pie chart', 'scatter plot', 'histogram']
    
    else:
        response['message'] = 'I can help you create charts! Try saying "show me the sales dataset" or "create a bar chart".'
        response['suggestions'] = ['show sales data', 'create bar chart', 'weather line chart']
    
    return response

def interactive_demo():
    """Interactive demo of the voice chart creator"""
    print("🎤 Voice-Enabled Chart Creator - Interactive Demo")
    print("=" * 55)
    print("This demo simulates voice commands and chart creation.")
    print("Type your commands as if you were speaking them!")
    print()
    
    current_dataset = None
    current_chart_type = None
    
    while True:
        print("\n" + "="*50)
        print("🎤 What would you like to do? (or type 'quit' to exit)")
        print("💡 Try: 'show me the sales dataset', 'create a bar chart', etc.")
        
        command = input("\n🎤 Command: ").strip()
        
        if command.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Thanks for using Voice Chart Creator!")
            break
        
        if not command:
            continue
        
        # Process the command
        response = process_voice_command(command)
        
        print(f"\n🤖 Assistant: {response['message']}")
        
        if response['suggestions']:
            print("\n💡 Suggestions:")
            for i, suggestion in enumerate(response['suggestions'], 1):
                print(f"   {i}. {suggestion}")
        
        # Update current state
        if 'dataset_id' in response['chart_config']:
            current_dataset = response['chart_config']['dataset_id']
            print(f"\n📊 Selected dataset: {SAMPLE_DATASETS[current_dataset]['name']}")
        
        if 'chart_type' in response['chart_config']:
            current_chart_type = response['chart_config']['chart_type']
            print(f"\n📈 Chart type set to: {current_chart_type}")
        
        # If we have both dataset and chart type, ask for columns
        if current_dataset and current_chart_type:
            dataset = SAMPLE_DATASETS[current_dataset]
            print(f"\n📋 Available columns: {', '.join(dataset['columns'])}")
            
            # Ask for X and Y columns
            print("\n🎯 Let's configure the chart:")
            x_col = input(f"X-axis column ({', '.join(dataset['columns'])}): ").strip()
            y_col = input(f"Y-axis column ({', '.join(dataset['columns'])}): ").strip()
            
            if x_col and y_col and x_col in dataset['columns'] and y_col in dataset['columns']:
                # Generate the chart
                print("\n🎨 Generating your chart...")
                print("="*50)
                
                chart = create_simple_chart(dataset, current_chart_type, x_col, y_col, None, f"{y_col} by {x_col}")
                print(chart)
                
                print("\n🎉 Chart created successfully!")
                
                # Reset for next chart
                current_dataset = None
                current_chart_type = None
            else:
                print("❌ Invalid column names. Please try again.")

def show_sample_datasets():
    """Display available sample datasets"""
    print("\n📊 Available Sample Datasets:")
    print("=" * 35)
    
    for key, dataset in SAMPLE_DATASETS.items():
        print(f"\n🔹 {dataset['name']} ({key})")
        print(f"   Description: {dataset['description']}")
        print(f"   Columns: {', '.join(dataset['columns'])}")
        print(f"   Rows: {len(dataset['data'])}")
        print(f"   Sample data:")
        for i, row in enumerate(dataset['data'][:3]):  # Show first 3 rows
            print(f"     {i+1}. {row}")
        if len(dataset['data']) > 3:
            print(f"     ... and {len(dataset['data']) - 3} more rows")

def main():
    """Main function"""
    print("🎤 Voice-Enabled Chart Creator")
    print("=" * 35)
    print("A real-time, interactive chart creation app")
    print("that responds to voice commands!")
    print()
    
    while True:
        print("\n🎯 Choose an option:")
        print("1. 🎤 Start Interactive Demo (Voice Commands)")
        print("2. 📊 View Sample Datasets")
        print("3. 🚀 Run Full Web Application")
        print("4. 📖 View Instructions")
        print("5. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            interactive_demo()
        elif choice == '2':
            show_sample_datasets()
        elif choice == '3':
            print("\n🚀 To run the full web application:")
            print("1. Install dependencies: pip install -r requirements.txt")
            print("2. Run: python app.py")
            print("3. Open browser: http://localhost:5000")
            print("4. Use voice commands or manual controls!")
            input("\nPress Enter to continue...")
        elif choice == '4':
            print("\n📖 Instructions:")
            print("=" * 20)
            print("🎤 Voice Commands:")
            print("• 'Show me the sales dataset'")
            print("• 'Create a bar chart'")
            print("• 'Use month and sales for axes'")
            print("• 'Add colors by region'")
            print("\n💡 Tips:")
            print("• Speak naturally and clearly")
            print("• Use specific dataset names")
            print("• Specify chart types")
            print("• Mention column names")
            input("\nPress Enter to continue...")
        elif choice == '5':
            print("\n👋 Thanks for using Voice Chart Creator!")
            print("🎉 Good luck with your project submission!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()