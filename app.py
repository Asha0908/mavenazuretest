from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import plotly.utils
import json
import os
import uuid
from datetime import datetime
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
CORS(app)

# Global variables
UPLOAD_FOLDER = 'uploads'
DATASETS_FOLDER = 'datasets'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATASETS_FOLDER, exist_ok=True)

# Pre-loaded sample datasets
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_chart(data, chart_type, x_column, y_column, color_column=None, title=None):
    """Create different types of charts based on user input"""
    
    if chart_type.lower() in ['bar', 'bar chart']:
        if color_column:
            fig = px.bar(data, x=x_column, y=y_column, color=color_column, title=title or f"{y_column} by {x_column}")
        else:
            fig = px.bar(data, x=x_column, y=y_column, title=title or f"{y_column} by {x_column}")
    
    elif chart_type.lower() in ['line', 'line chart']:
        if color_column:
            fig = px.line(data, x=x_column, y=y_column, color=color_column, title=title or f"{y_column} over {x_column}")
        else:
            fig = px.line(data, x=x_column, y=y_column, title=title or f"{y_column} over {x_column}")
    
    elif chart_type.lower() in ['scatter', 'scatter plot']:
        if color_column:
            fig = px.scatter(data, x=x_column, y=y_column, color=color_column, title=title or f"{y_column} vs {x_column}")
        else:
            fig = px.scatter(data, x=x_column, y=y_column, title=title or f"{y_column} vs {x_column}")
    
    elif chart_type.lower() in ['pie', 'pie chart']:
        fig = px.pie(data, values=y_column, names=x_column, title=title or f"Distribution of {y_column}")
    
    elif chart_type.lower() in ['histogram', 'hist']:
        fig = px.histogram(data, x=x_column, title=title or f"Distribution of {x_column}")
    
    else:
        # Default to bar chart
        fig = px.bar(data, x=x_column, y=y_column, title=title or f"{y_column} by {x_column}")
    
    # Customize the layout
    fig.update_layout(
        template="plotly_white",
        font=dict(size=14),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/datasets')
def get_datasets():
    """Get list of available datasets"""
    datasets = []
    
    # Add sample datasets
    for key, dataset in SAMPLE_DATASETS.items():
        datasets.append({
            'id': key,
            'name': dataset['name'],
            'description': dataset['description'],
            'columns': dataset['columns'],
            'type': 'sample'
        })
    
    # Add uploaded datasets
    for filename in os.listdir(UPLOAD_FOLDER):
        if allowed_file(filename):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                if filename.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                datasets.append({
                    'id': filename,
                    'name': filename,
                    'description': f'Uploaded dataset with {len(df)} rows and {len(df.columns)} columns',
                    'columns': df.columns.tolist(),
                    'type': 'uploaded'
                })
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    return jsonify(datasets)

@app.route('/api/dataset/<dataset_id>')
def get_dataset(dataset_id):
    """Get specific dataset data"""
    try:
        if dataset_id in SAMPLE_DATASETS:
            # Return sample dataset
            dataset = SAMPLE_DATASETS[dataset_id]
            df = pd.DataFrame(dataset['data'], columns=dataset['columns'])
        else:
            # Return uploaded dataset
            file_path = os.path.join(UPLOAD_FOLDER, dataset_id)
            if dataset_id.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        
        return jsonify({
            'success': True,
            'data': df.to_dict('records'),
            'columns': df.columns.tolist(),
            'shape': df.shape
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/upload', methods=['POST'])
def upload_dataset():
    """Upload a new dataset"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if file and allowed_file(file.filename):
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'Dataset uploaded successfully'
        })
    
    return jsonify({'success': False, 'error': 'Invalid file type'})

@app.route('/api/chart', methods=['POST'])
def generate_chart():
    """Generate chart based on voice commands"""
    try:
        data = request.json
        dataset_id = data.get('dataset_id')
        chart_type = data.get('chart_type', 'bar')
        x_column = data.get('x_column')
        y_column = data.get('y_column')
        color_column = data.get('color_column')
        title = data.get('title')
        
        # Get dataset data
        if dataset_id in SAMPLE_DATASETS:
            dataset = SAMPLE_DATASETS[dataset_id]
            df = pd.DataFrame(dataset['data'], columns=dataset['columns'])
        else:
            file_path = os.path.join(UPLOAD_FOLDER, dataset_id)
            if dataset_id.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        
        # Validate columns
        if x_column not in df.columns:
            return jsonify({'success': False, 'error': f'Column {x_column} not found in dataset'})
        if y_column and y_column not in df.columns:
            return jsonify({'success': False, 'error': f'Column {y_column} not found in dataset'})
        if color_column and color_column not in df.columns:
            return jsonify({'success': False, 'error': f'Column {color_column} not found in dataset'})
        
        # Generate chart
        chart_json = create_chart(df, chart_type, x_column, y_column, color_column, title)
        
        return jsonify({
            'success': True,
            'chart': chart_json,
            'dataset_info': {
                'rows': len(df),
                'columns': df.columns.tolist()
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/voice-command', methods=['POST'])
def process_voice_command():
    """Process voice commands and return chart configuration"""
    try:
        command = request.json.get('command', '').lower()
        
        # Simple voice command parsing
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
        
        elif 'color' in command or 'colour' in command:
            response['message'] = 'I can add colors to your chart based on different columns. Which column would you like to use for coloring?'
            response['chart_config'] = {'needs_color': True}
        
        elif 'title' in command:
            response['message'] = 'What would you like to title your chart?'
            response['chart_config'] = {'needs_title': True}
        
        else:
            response['message'] = 'I can help you create charts! Try saying "show me the sales dataset" or "create a bar chart".'
            response['suggestions'] = ['show sales data', 'create bar chart', 'weather line chart']
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)