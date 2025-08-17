#!/usr/bin/env python3
"""
🎤 Beautiful Voice-Enabled Chart Creator with Visual Display
======================================================================
This system SPEAKS to you AND shows beautiful visual charts!
"""

from flask import Flask, render_template, request, jsonify
import plotly.graph_objects as go
import plotly.utils
import json
import webbrowser
import threading
import time
import os

app = Flask(__name__)

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

def create_beautiful_chart(dataset_name, chart_type="bar", custom_colors=None):
    """Create a beautiful Plotly chart"""
    if dataset_name not in SAMPLE_DATASETS:
        return None
    
    dataset = SAMPLE_DATASETS[dataset_name]
    data = dataset['data']
    colors = custom_colors if custom_colors else dataset['colors']
    
    if chart_type == "bar":
        fig = go.Figure(data=[
            go.Bar(
                x=list(data.keys()),
                y=list(data.values()),
                marker_color=colors,
                text=list(data.values()),
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Value: %{y}<extra></extra>'
            )
        ])
    elif chart_type == "line":
        fig = go.Figure(data=[
            go.Scatter(
                x=list(data.keys()),
                y=list(data.values()),
                mode='lines+markers',
                line=dict(color='#6C5CE7', width=4),
                marker=dict(size=10, color=colors),
                text=list(data.values()),
                textposition='top center'
            )
        ])
    elif chart_type == "pie":
        fig = go.Figure(data=[
            go.Pie(
                labels=list(data.keys()),
                values=list(data.values()),
                marker_colors=colors,
                textinfo='label+percent',
                textposition='inside',
                hole=0.3
            )
        ])
    else:
        # Default to bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=list(data.keys()),
                y=list(data.values()),
                marker_color=colors,
                text=list(data.values()),
                textposition='auto'
            )
        ])
    
    # Beautiful styling
    fig.update_layout(
        title={
            'text': f'📊 {dataset_name.title()} Data Chart',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': '#2D3436'}
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14, color='#2D3436'),
        margin=dict(l=50, r=50, t=80, b=50),
        showlegend=False,
        height=500
    )
    
    fig.update_xaxes(
        gridcolor='rgba(128,128,128,0.2)',
        showgrid=True,
        zeroline=False
    )
    
    fig.update_yaxes(
        gridcolor='rgba(128,128,128,0.2)',
        showgrid=True,
        zeroline=False
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/')
def index():
    return render_template('beautiful_chart.html')

@app.route('/api/datasets')
def get_datasets():
    return jsonify(list(SAMPLE_DATASETS.keys()))

@app.route('/api/create_chart', methods=['POST'])
def create_chart():
    data = request.json
    dataset_name = data.get('dataset')
    chart_type = data.get('chart_type', 'bar')
    custom_colors = data.get('colors')
    
    chart_json = create_beautiful_chart(dataset_name, chart_type, custom_colors)
    
    if chart_json:
        return jsonify({
            'success': True,
            'chart': chart_json,
            'dataset_info': SAMPLE_DATASETS[dataset_name]
        })
    else:
        return jsonify({'success': False, 'error': 'Dataset not found'})

@app.route('/api/voice_command', methods=['POST'])
def process_voice_command():
    data = request.json
    command = data.get('command', '').lower()
    
    response = {
        'message': '',
        'action': 'none',
        'dataset': None,
        'chart_type': 'bar'
    }
    
    # Process voice commands
    if any(word in command for word in ['sales', 'revenue', 'money']):
        response['message'] = "Great! I found the sales dataset. I'll create a beautiful chart for you now."
        response['action'] = 'create_chart'
        response['dataset'] = 'sales'
    elif any(word in command for word in ['weather', 'temperature', 'climate']):
        response['message'] = "Perfect! I found the weather dataset. I'll create a beautiful chart for you now."
        response['action'] = 'create_chart'
        response['dataset'] = 'weather'
    elif any(word in command for word in ['student', 'performance', 'score', 'grade']):
        response['message'] = "Excellent! I found the student performance dataset. I'll create a beautiful chart for you now."
        response['action'] = 'create_chart'
        response['dataset'] = 'students'
    elif 'bar' in command:
        response['message'] = "I'll change the chart to a beautiful bar chart."
        response['action'] = 'change_type'
        response['chart_type'] = 'bar'
    elif 'line' in command:
        response['message'] = "I'll change the chart to a beautiful line chart."
        response['action'] = 'change_type'
        response['chart_type'] = 'line'
    elif 'pie' in command:
        response['message'] = "I'll change the chart to a beautiful pie chart."
        response['action'] = 'change_type'
        response['chart_type'] = 'pie'
    else:
        response['message'] = "I'm not sure what you want. Please say 'sales', 'weather', or 'students' to create a chart."
    
    return jsonify(response)

def open_browser():
    """Open browser automatically after a short delay"""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    # Open browser automatically
    threading.Thread(target=open_browser).start()
    
    print("🎤 Beautiful Voice-Enabled Chart Creator Starting...")
    print("🌐 Opening browser automatically...")
    print("🎯 Speak to create charts - they will be displayed visually!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)