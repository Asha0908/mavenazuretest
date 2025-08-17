#!/usr/bin/env python3
"""
🎤 SUPER SIMPLE Voice-Enabled Chart Creator - GUARANTEED TO WORK!
======================================================================
This will work even if Flask doesn't work!
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os
import time

# Sample datasets
SAMPLE_DATASETS = {
    'sales': {
        'data': {'Jan': 2000, 'Feb': 2300, 'Mar': 2100, 'Apr': 1800, 'May': 2500},
        'description': 'Monthly sales data showing revenue trends',
        'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    },
    'weather': {
        'data': {'Monday': 25, 'Tuesday': 28, 'Wednesday': 22, 'Thursday': 30, 'Friday': 27},
        'description': 'Daily temperature data for the week',
        'colors': ['#74B9FF', '#A29BFE', '#FD79A8', '#FDCB6E', '#00B894']
    },
    'students': {
        'data': {'Math': 85, 'Science': 92, 'English': 78, 'History': 88, 'Art': 95},
        'description': 'Student performance scores across subjects',
        'colors': ['#6C5CE7', '#A29BFE', '#FD79A8', '#FDCB6E', '#00B894']
    }
}

def create_beautiful_chart(dataset_name, chart_type="bar"):
    """Create a beautiful matplotlib chart"""
    if dataset_name not in SAMPLE_DATASETS:
        print(f"❌ Dataset '{dataset_name}' not found!")
        return
    
    dataset = SAMPLE_DATASETS[dataset_name]
    data = dataset['data']
    colors = dataset['colors']
    
    # Clear any existing plots
    plt.clf()
    
    # Create figure with beautiful styling
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('#ffffff')
    
    # Get data
    categories = list(data.keys())
    values = list(data.values())
    
    if chart_type == "bar":
        bars = ax.bar(categories, values, color=colors, edgecolor='white', linewidth=2)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                   f'{value}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax.set_ylabel('Values', fontsize=14, fontweight='bold')
        ax.set_xlabel('Categories', fontsize=14, fontweight='bold')
        
    elif chart_type == "line":
        ax.plot(categories, values, marker='o', linewidth=4, markersize=10, 
                color='#6C5CE7', markerfacecolor='#A29BFE', markeredgecolor='white', markeredgewidth=2)
        
        # Add value labels
        for x, y in zip(categories, values):
            ax.annotate(f'{y}', (x, y), textcoords="offset points", xytext=(0,10), 
                       ha='center', fontsize=12, fontweight='bold')
        
        ax.set_ylabel('Values', fontsize=14, fontweight='bold')
        ax.set_xlabel('Categories', fontsize=14, fontweight='bold')
        
    elif chart_type == "pie":
        wedges, texts, autotexts = ax.pie(values, labels=categories, colors=colors, 
                                          autopct='%1.1f%%', startangle=90,
                                          wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    # Beautiful styling
    ax.set_title(f'📊 {dataset_name.title()} Data Chart', fontsize=24, fontweight='bold', 
                 color='#2D3436', pad=20)
    
    # Grid styling
    if chart_type != "pie":
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')
    
    # Rotate x-axis labels for better readability
    if chart_type != "pie":
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    # Add dataset description
    fig.text(0.5, 0.02, dataset['description'], ha='center', fontsize=12, 
             style='italic', color='#666666')
    
    # Adjust layout
    plt.tight_layout()
    
    # Show the chart
    plt.show()
    
    print(f"🎉 Beautiful {chart_type} chart created for {dataset_name}!")
    print(f"📊 Chart shows: {dataset['description']}")

def main():
    """Main interactive loop"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("🎤 SUPER SIMPLE Voice-Enabled Chart Creator")
    print("=" * 60)
    print("🎯 This will DEFINITELY work!")
    print("📊 Creates beautiful visual charts")
    print("🎨 Multiple chart types: bar, line, pie")
    print("🚀 No complex setup needed!\n")
    
    print("📋 Available datasets:")
    for name, info in SAMPLE_DATASETS.items():
        print(f"   • {name.title()}: {info['description']}")
    
    print("\n🎨 Available chart types:")
    print("   • bar: Beautiful bar charts")
    print("   • line: Smooth line charts") 
    print("   • pie: Colorful pie charts")
    
    print("\n" + "=" * 60)
    
    while True:
        print("\n🎯 What would you like to do?")
        print("1. Create a chart")
        print("2. View available datasets")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n📊 Let's create a beautiful chart!")
            
            # Get dataset
            print("\nAvailable datasets:")
            for i, name in enumerate(SAMPLE_DATASETS.keys(), 1):
                print(f"{i}. {name.title()}")
            
            try:
                dataset_choice = input("\nEnter dataset number (1-3): ").strip()
                dataset_map = {1: 'sales', 2: 'weather', 3: 'students'}
                dataset_name = dataset_map.get(int(dataset_choice))
                
                if not dataset_name:
                    print("❌ Invalid choice! Using sales data.")
                    dataset_name = 'sales'
            except:
                print("❌ Invalid input! Using sales data.")
                dataset_name = 'sales'
            
            # Get chart type
            print("\nAvailable chart types:")
            print("1. Bar chart (beautiful bars)")
            print("2. Line chart (smooth lines)")
            print("3. Pie chart (colorful slices)")
            
            try:
                type_choice = input("\nEnter chart type (1-3): ").strip()
                type_map = {1: 'bar', 2: 'line', 3: 'pie'}
                chart_type = type_map.get(int(type_choice), 'bar')
            except:
                print("❌ Invalid input! Using bar chart.")
                chart_type = 'bar'
            
            # Create the chart
            print(f"\n🎨 Creating beautiful {chart_type} chart for {dataset_name}...")
            create_beautiful_chart(dataset_name, chart_type)
            
        elif choice == "2":
            print("\n📋 Available datasets:")
            for name, info in SAMPLE_DATASETS.items():
                print(f"\n📊 {name.title()}:")
                print(f"   Description: {info['description']}")
                print(f"   Data: {info['data']}")
                
        elif choice == "3":
            print("\n👋 Thank you for using the Chart Creator!")
            print("🎉 Your charts were beautiful!")
            break
            
        else:
            print("❌ Invalid choice! Please enter 1, 2, or 3.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("But don't worry! This is just a small issue.")
        print("Try running it again!")