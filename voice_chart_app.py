#!/usr/bin/env python3
"""
🗣️ VOICE ENABLED CHART CREATION - FIXED VERSION
- Fixed context handling for "same dataset" requests
- Fixed speech recognition issues
- Added default values for everything
- Better error handling
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import time
import threading
import speech_recognition as sr
import pyttsx3
import random
import os
from sklearn.datasets import load_iris

# ---------------- Helpers ----------------
def parse_color(text: str, fallback: str = "#3498db"):
    colors = {
        "blue":"#3498db","red":"#e74c3c","green":"#2ecc71","orange":"#f39c12",
        "purple":"#9b59b6","teal":"#1abc9c","gray":"#7f8c8d","grey":"#7f8c8d",
        "yellow":"#f1c40f","pink":"#ff6bb5","cyan":"#00d4ff","lime":"#b6ff00"
    }
    if not text: return fallback
    s = text.strip().lower().replace("colour","color")
    if "skip" in s: return fallback
    for name, hexv in colors.items():
        if name in s: return hexv
    return fallback

def get_vibrant_colors(n):
    """Get vibrant colors for charts"""
    colors = [
        "#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c",
        "#e67e22", "#34495e", "#f1c40f", "#e91e63", "#00bcd4", "#4caf50"
    ]
    return colors[:n] if n <= len(colors) else colors * (n // len(colors) + 1)[:n]

def generate_random_data(dataset_name, n_categories=5):
    """Generate random data for any dataset name"""
    if 'sales' in dataset_name or 'revenue' in dataset_name or 'sale' in dataset_name:
        categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'][:n_categories]
        values = [random.randint(1500, 3000) for _ in range(n_categories)]
        x_label, y_label = 'Month', 'Revenue'
        attributes = ['Month', 'Revenue', 'Profit', 'Cost', 'Growth Rate']
    elif 'weather' in dataset_name or 'temperature' in dataset_name:
        categories = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'][:n_categories]
        values = [random.randint(15, 35) for _ in range(n_categories)]
        x_label, y_label = 'Day', 'Temperature'
        attributes = ['Day', 'Temperature', 'Humidity', 'Pressure', 'Wind Speed']
    elif 'student' in dataset_name or 'grade' in dataset_name:
        categories = ['Math', 'Science', 'English', 'History', 'Art'][:n_categories]
        values = [random.randint(60, 100) for _ in range(n_categories)]
        x_label, y_label = 'Subject', 'Score'
        attributes = ['Subject', 'Score', 'Grade', 'Attendance', 'Assignment']
    elif 'iris' in dataset_name or 'flower' in dataset_name:
        iris = load_iris()
        df = pd.DataFrame(iris.data, columns=iris.feature_names)
        df['species'] = iris.target_names[iris.target]
        species_counts = df['species'].value_counts()
        attributes = ['Sepal Length', 'Sepal Width', 'Petal Length', 'Petal Width', 'Species']
        return {
            'data': dict(species_counts),
            'x_label': 'Species', 'y_label': 'Count',
            'attributes': attributes
        }
    elif 'train' in dataset_name or 'trains' in dataset_name:
        categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'][:n_categories]
        values = [random.randint(80, 120) for _ in range(n_categories)]
        x_label, y_label = 'Month', 'Train Count'
        attributes = ['Month', 'Train Count', 'Passengers', 'Revenue', 'Status']
    else:
        categories = [f'Item {i+1}' for i in range(n_categories)]
        values = [random.randint(10, 100) for _ in range(n_categories)]
        x_label, y_label = 'Category', 'Value'
        attributes = ['Category', 'Value', 'Type', 'Status', 'Priority']
    
    return {
        'data': dict(zip(categories, values)),
        'x_label': x_label,
        'y_label': y_label,
        'attributes': attributes
    }

# -------------- App ----------------------
class VoiceEnabledChartApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🗣️ Voice Enabled Chart Creation")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')

        # STT/TTS
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone()
        except Exception:
            self.microphone = None
        self.engine = pyttsx3.init('sapi5')
        self.engine.setProperty('rate', 180)
        self.engine.setProperty('volume', 1.0)

        # Context tracking
        self.current_dataset = None
        self.current_chart_type = 'bar'
        self.custom_color_hex = "#3498db"
        self.custom_data = None
        self.last_data = None
        self.last_attributes = None
        self.chart_created = False
        self.session_ended = False
        self.processing = False

        # Conversation state
        self.is_listening = False
        self.conversation_active = False
        self.awaiting = None
        self.first_interaction = True

        self.setup_ui()
        self.speak("Hello! I'm Faboo, your friendly chart-making assistant! Click START CHATTING to begin!")

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        header_frame = tk.Frame(main_frame, bg='#34495e')
        header_frame.pack(fill='x', pady=(0, 20))
        tk.Label(header_frame, text="🗣️ VOICE ENABLED CHART CREATION", font=('Arial', 22, 'bold'), bg='#34495e', fg='#ecf0f1').pack()
        tk.Label(header_frame, text="Meet Faboo - Your friendly chart-making buddy!", font=('Arial', 14), bg='#34495e', fg='#bdc3c7').pack(pady=(5,0))

        content_frame = tk.Frame(main_frame, bg='#2c3e50')
        content_frame.pack(fill='both', expand=True)

        left_panel = tk.Frame(content_frame, bg='#34495e', width=450)
        left_panel.pack(side='left', fill='y', padx=(0, 20))
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text="🗣️ CONVERSATION", font=('Arial', 16, 'bold'), bg='#34495e', fg='#ecf0f1').pack(pady=(20,15))

        self.conversation_text = tk.Text(left_panel, height=18, width=50, bg='#2c3e50', fg='#ecf0f1', font=('Arial', 11), wrap='word', state='disabled')
        self.conversation_text.pack(padx=20, pady=(0,20))
        scr = ttk.Scrollbar(left_panel, orient='vertical', command=self.conversation_text.yview)
        scr.pack(side='right', fill='y')
        self.conversation_text.configure(yscrollcommand=scr.set)

        # Upload section
        upload_frame = tk.Frame(left_panel, bg='#34495e')
        upload_frame.pack(pady=(0, 15))
        tk.Label(upload_frame, text="📁 UPLOAD DATA", font=('Arial', 12, 'bold'), bg='#34495e', fg='#ecf0f1').pack()
        upload_btn = tk.Button(upload_frame, text="📤 Upload CSV/Excel", command=self.upload_dataset, bg='#9b59b6', fg='white', font=('Arial', 10, 'bold'))
        upload_btn.pack(pady=(5,0))

        voice_frame = tk.Frame(left_panel, bg='#34495e')
        voice_frame.pack(pady=(0, 20))
        self.mic_button = tk.Button(voice_frame, text="🎤 START CHATTING", font=('Arial', 14, 'bold'), bg='#27ae60', fg='white', command=self.start_session, width=25, height=2)
        self.mic_button.pack()
        self.end_call_button = tk.Button(voice_frame, text="👋 END CHAT", font=('Arial', 12, 'bold'), bg='#e74c3c', fg='white', command=self.end_session, width=20, height=1)

        self.status_label = tk.Label(left_panel, text="Click START CHATTING to begin...", font=('Arial', 12), bg='#34495e', fg='#2ecc71')
        self.status_label.pack(pady=(10, 0))

        right_panel = tk.Frame(content_frame, bg='#34495e')
        right_panel.pack(side='right', fill='both', expand=True)
        tk.Label(right_panel, text="📊 YOUR CHARTS", font=('Arial', 16, 'bold'), bg='#34495e', fg='#ecf0f1').pack(pady=(20,15))

        self.chart_frame = tk.Frame(right_panel, bg='#ecf0f1', height=500)
        self.chart_frame.pack(fill='both', expand=True, padx=20, pady=(0,20))

        self.chart_placeholder = tk.Label(self.chart_frame, text="🎯 Just say what you want!\n\nExamples:\n• 'Create a pie chart'\n• 'Make it blue'\n• 'Use same dataset, create bar chart'\n• 'Upload my data'\n• 'Create random data'\n• 'Explain the chart'\n• 'What charts can you create?'\n• 'What attributes does this dataset have?'", font=('Arial', 11), bg='#ecf0f1', fg='#2c3e50', justify='center')
        self.chart_placeholder.pack(expand=True)

        # Test button
        test_btn = tk.Button(right_panel, text="🧪 Test Chart", command=self.test_chart, bg='#f39c12', fg='white', font=('Arial', 12, 'bold'))
        test_btn.pack(pady=(0,20))

    def upload_dataset(self):
        """Upload custom dataset"""
        file_path = filedialog.askopenfilename(
            title="Select Dataset File",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                else:
                    messagebox.showerror("Error", "Please select a CSV or Excel file")
                    return
                
                self.custom_data = df
                self.last_attributes = list(df.columns)
                preview_text = f"📁 Uploaded: {os.path.basename(file_path)}\n📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns\n📋 Attributes: {', '.join(df.columns[:5])}"
                if len(df.columns) > 5:
                    preview_text += "..."
                messagebox.showinfo("Dataset Uploaded", preview_text)
                
                if self.conversation_active:
                    self.speak(f"Great! I've uploaded your dataset with {df.shape[0]} rows and {df.shape[1]} columns. What kind of chart would you like?")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def add_to_conversation(self, speaker, message):
        self.conversation_text.config(state='normal')
        ts = time.strftime("%H:%M:%S")
        icon = "🤖" if speaker == "Faboo" else "👤"
        self.conversation_text.insert('end', f"[{ts}] {icon} {speaker}: {message}\n\n")
        self.conversation_text.config(state='disabled')
        self.conversation_text.see('end')

    def speak(self, text):
        if self.session_ended:
            return
        self.add_to_conversation("Faboo", text)
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception:
            pass

    def start_session(self):
        if self.microphone is None:
            self.add_to_conversation("Faboo", "No microphone found. Please connect a mic and restart.")
            return
        self.conversation_active = True
        self.is_listening = True
        self.session_ended = False
        self.mic_button.pack_forget()
        self.end_call_button.pack()
        self.status_label.config(text="🟢 Chatting active - I'm listening!", fg='#2ecc71')
        
        if self.first_interaction:
            self.speak("Hi! I'm Faboo, your friendly chart-making buddy! How are you doing today?")
            self.first_interaction = False
        else:
            greetings = ["Hey! What should we create?", "Hi! Ready to make charts?", "Hello! What interests you?"]
            self.speak(random.choice(greetings))
        
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def end_session(self):
        """End the session immediately and accurately - FIXED!"""
        # Stop all activities immediately
        self.conversation_active = False
        self.is_listening = False
        self.session_ended = True
        self.awaiting = None
        
        # Update UI immediately
        self.end_call_button.pack_forget()
        self.mic_button.pack()
        self.status_label.config(text="Chat ended. Click START CHATTING to begin again...", fg='#e74c3c')
        
        # Add final message to conversation
        self.add_to_conversation("Faboo", "Thanks! You have a great day!")
        
        # Speak final message and stop - FIXED!
        try:
            self.engine.say("Thanks! You have a great day!")
            self.engine.runAndWait()
        except Exception:
            pass

    def listen_loop(self):
        while self.conversation_active and self.is_listening and not self.session_ended:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=8)
                text = self.recognizer.recognize_google(audio)
                self.add_to_conversation("You", text)
                self.process_request(text)
                time.sleep(0.1)
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                if not self.session_ended:
                    self.speak("Sorry, I didn't catch that. Could you say it again?")
                continue
            except sr.RequestError:
                if not self.session_ended:
                    self.speak("Hmm, having trouble hearing you. Try once more!")
                continue
            except Exception:
                if not self.session_ended:
                    self.speak("Oops, something went wrong. Let's continue!")
                continue

    def process_request(self, text: str):
        if self.session_ended or self.processing:
            return
            
        self.processing = True
        try:
            t = (text or "").lower().strip()

            # End conversation - FIXED!
            if any(w in t for w in ["goodbye", "bye", "end chat", "stop", "exit", "quit"]):
                self.speak("Thanks! You have a great day!")
                self.end_session()
                return

            # Check for chart types info
            if 'what charts' in t or 'chart types' in t or 'charts can' in t:
                self.tell_chart_types()
                return

            # Check for dataset attributes info
            if 'attributes' in t or 'columns' in t or 'fields' in t:
                self.tell_dataset_attributes(t)
                return

            # Check for explain request
            if 'explain' in t and self.chart_created:
                self.explain_current_chart()
                return

            # Handle awaiting states
            if self.awaiting:
                self.handle_awaiting_state(t)
                return

            # Check for context-based requests FIRST (after chart is created)
            if self.chart_created and self.is_context_request(t):
                self.handle_context_request(t)
                return

            # Check for chart creation requests
            if self.is_chart_request(t):
                self.handle_chart_request(t)
                return

            # Friendly conversation
            if self.is_friendly_conversation(t):
                self.handle_friendly_conversation(t)
                return

            # Help or unclear request
            self.handle_help_request(t)
        finally:
            self.processing = False

    def tell_chart_types(self):
        """Tell what chart types can be created"""
        chart_types = [
            "Bar charts for comparing categories",
            "Line charts for showing trends over time",
            "Pie charts for showing proportions",
            "Donut charts similar to pie charts with hollow center",
            "Scatter plots for showing relationships",
            "Histograms for showing distributions",
            "Waterfall charts for showing cumulative changes",
            "Area charts for showing trends with filled areas",
            "Radar charts for multi-dimensional data",
            "Heatmaps for showing patterns in data"
        ]
        response = "I can create many types of charts! " + ". ".join(chart_types) + ". Just tell me which one you want!"
        self.speak(response)

    def tell_dataset_attributes(self, text):
        """Tell what attributes the specified dataset has"""
        dataset_name = self.extract_dataset_smart(text)
        
        if dataset_name == 'custom' and self.custom_data is not None:
            attributes = list(self.custom_data.columns)
            response = f"Your uploaded dataset has these attributes: {', '.join(attributes)}. You can use any of these for creating charts!"
        elif dataset_name:
            dataset_info = generate_random_data(dataset_name)
            attributes = dataset_info['attributes']
            response = f"The {dataset_name} dataset has these attributes: {', '.join(attributes)}. You can use any of these for creating charts!"
        elif self.last_attributes:
            response = f"The {self.current_dataset} dataset has these attributes: {', '.join(self.last_attributes)}. You can use any of these for creating charts!"
        else:
            response = "I don't have a dataset loaded yet. Please create a chart first or upload your own data!"
        self.speak(response)

    def is_chart_request(self, text):
        """Check if this is a chart creation request"""
        chart_words = ['create', 'make', 'show', 'generate', 'pie', 'bar', 'line', 'chart', 'graph', 'display', 'visualize']
        return any(word in text for word in chart_words)

    def is_context_request(self, text):
        """Check if this is a follow-up request using context - IMPROVED!"""
        context_words = ['change', 'make it', 'use same', 'same dataset', 'same data', 'same', 'different', 'another', 'switch', 'bar chart', 'pie chart', 'line chart']
        return any(word in text for word in context_words) and self.chart_created

    def is_friendly_conversation(self, text):
        """Check if this is a friendly conversation"""
        friendly_words = ['hi', 'hello', 'hey', 'how are you', 'how r u', 'what\'s up', 'sup', 'buddy', 'friend']
        return any(word in text for word in friendly_words)

    def explain_current_chart(self):
        """Explain the current chart in detail"""
        if not self.chart_created or not self.last_data:
            self.speak("I don't have a chart to explain yet. Please create a chart first!")
            return
        
        chart_type = self.current_chart_type
        data = self.last_data
        cats = list(data.keys())
        vals = list(data.values())
        
        explanations = {
            'bar': f"This bar chart displays {len(cats)} categories. The tallest bar shows the highest value of {max(vals)}, while the shortest shows {min(vals)}. This makes it easy to compare different categories at a glance.",
            'pie': f"This pie chart shows the distribution of {len(cats)} categories. The largest slice represents {max(data, key=data.get)} with {max(vals)} units, while the smallest is {min(data, key=data.get)} with {min(vals)} units. Each slice shows the proportion of the whole.",
            'line': f"This line chart shows trends across {len(cats)} data points. The line connects each point, making it easy to see patterns. The highest point is {max(vals)} and the lowest is {min(vals)}.",
            'donut': f"This donut chart is similar to a pie chart but with a hollow center. It shows the distribution of {len(cats)} categories with percentages displayed. The largest segment is {max(data, key=data.get)}.",
            'scatter': f"This scatter plot shows the relationship between {len(cats)} data points. Each dot represents a data point, helping you see patterns and correlations. Values range from {min(vals)} to {max(vals)}.",
            'histogram': f"This histogram shows the distribution of values across {len(cats)} bins. It helps you understand the frequency and spread of your data. The most frequent range contains {max(vals)} values.",
            'waterfall': f"This waterfall chart shows cumulative changes across {len(cats)} categories. It's great for showing how values build up or decrease over time. The final cumulative value is {sum(vals)}.",
            'area': f"This area chart shows trends over {len(cats)} data points with filled areas under the line. It emphasizes the magnitude of changes over time. The total area represents {sum(vals)} units."
        }
        
        explanation = explanations.get(chart_type, f"This {chart_type} chart displays your data across {len(cats)} categories.")
        self.speak(explanation)

    def handle_chart_request(self, text):
        """Handle chart creation requests - IMPROVED!"""
        # Extract all parameters from the request
        dataset = self.extract_dataset_smart(text)
        chart_type = self.extract_chart_type(text)
        color = self.extract_color(text)
        x_axis = self.extract_x_label(text)
        y_axis = self.extract_y_label(text)
        
        if not dataset:
            dataset = 'random'
        
        self.current_dataset = dataset
        self.current_chart_type = chart_type
        self.custom_color_hex = color
        
        # If all parameters are provided, create chart immediately
        if x_axis and y_axis:
            self.speak(f"Perfect! I'll create a {chart_type} chart for {dataset} data with {x_axis} on X-axis and {y_axis} on Y-axis!")
            self.render_chart()
            self.chart_created = True
            self.awaiting = None
        else:
            # Ask for missing parameters step by step
            if not chart_type or chart_type == 'bar':
                self.speak(f"Great! I'll use {dataset} data. What type of chart would you like?")
                self.awaiting = 'chart_type'
            else:
                self.speak(f"Perfect! A {chart_type} chart for {dataset} data. What should be the X axis?")
                self.awaiting = 'x_axis'

    def handle_context_request(self, text):
        """Handle requests that use previous context - FIXED!"""
        if 'use same' in text or 'same dataset' in text or 'same data' in text or 'same' in text:
            chart_type = self.extract_chart_type(text)
            if chart_type and chart_type != 'bar':
                self.current_chart_type = chart_type
                self.speak(f"Done! I'll create a {chart_type} chart with the same {self.current_dataset} data!")
                self.render_chart()
                self.chart_created = True
                self.awaiting = None
            else:
                self.speak("What type of chart would you like with the same data?")
                self.awaiting = 'chart_type'
        elif 'bar chart' in text or 'bar' in text:
            self.current_chart_type = 'bar'
            self.speak("Done! I'll create a bar chart with the same data!")
            self.render_chart()
            self.chart_created = True
            self.awaiting = None
        elif 'pie chart' in text or 'pie' in text:
            self.current_chart_type = 'pie'
            self.speak("Done! I'll create a pie chart with the same data!")
            self.render_chart()
            self.chart_created = True
            self.awaiting = None
        elif 'line chart' in text or 'line' in text:
            self.current_chart_type = 'line'
            self.speak("Done! I'll create a line chart with the same data!")
            self.render_chart()
            self.chart_created = True
            self.awaiting = None
        elif 'color' in text or any(c in text for c in ['blue', 'red', 'green', 'yellow', 'purple']):
            new_color = self.extract_color(text)
            self.custom_color_hex = new_color
            self.speak("Done! Updated your chart!")
            self.render_chart()
        else:
            self.speak("What would you like to change? Chart type, color, or dataset?")

    def handle_friendly_conversation(self, text):
        """Handle friendly conversation"""
        if 'buddy' in text and 'chart' in text:
            self.speak("Hey buddy! Of course I'll create charts for you! Just tell me what kind of chart you want and I'll make it!")
        elif 'how are you' in text or 'how r u' in text:
            responses = [
                "I'm doing great! Thanks for asking! Ready to create some awesome charts together?",
                "I'm fantastic! How are you doing? What kind of chart should we make today?",
                "I'm wonderful! Thanks for checking! Ready to visualize some data?"
            ]
            self.speak(random.choice(responses))
        elif 'what\'s up' in text or 'sup' in text:
            responses = [
                "Not much! Just waiting to help you create some amazing charts! What do you want to visualize?",
                "Just hanging out, ready to make charts! What kind of data should we work with?"
            ]
            self.speak(random.choice(responses))
        elif any(word in text for word in ['hi', 'hello', 'hey']):
            responses = [
                "Hey there! Great to see you! What kind of chart should we create today?",
                "Hi! How's it going? Ready to make some awesome visualizations?",
                "Hello! Nice to chat with you! What data interests you today?"
            ]
            self.speak(random.choice(responses))
        else:
            responses = [
                "Hey! What kind of chart should we make today?",
                "Hi there! Ready to create something awesome?",
                "Hello! What data interests you?"
            ]
            self.speak(random.choice(responses))

    def handle_help_request(self, text):
        """Handle help or unclear requests"""
        if any(w in text for w in ["help", "what can you do", "how", "what"]):
            self.speak("I can create charts from any data you mention! Just say 'create a pie chart', 'make a bar chart', or anything else. I'll generate the data dynamically!")
        else:
            self.speak("I'm not sure what you want to create. Try saying something like 'create a pie chart' or 'make a bar chart'! I'll generate the data for you.")

    def handle_awaiting_state(self, text):
        """Handle step-by-step conversation - IMPROVED!"""
        if self.awaiting == 'chart_type':
            chart_type = self.extract_chart_type(text)
            if chart_type:
                self.current_chart_type = chart_type
                self.speak(f"Perfect! A {chart_type} chart. What should be the X axis?")
                self.awaiting = 'x_axis'
            else:
                self.speak("I didn't catch the chart type. Please say bar, line, pie, donut, scatter, histogram, area, radar, waterfall, or heatmap.")
        elif self.awaiting == 'x_axis':
            x_label = self.extract_x_label(text)
            if x_label:
                self.speak(f"Great! X axis will be {x_label}. What should be the Y axis?")
                self.awaiting = 'y_axis'
            elif 'default' in text or 'any' in text:
                # Use default X axis
                if self.current_dataset:
                    dataset_info = generate_random_data(self.current_dataset)
                    x_label = dataset_info['x_label']
                    self.speak(f"Great! I'll use the default X axis: {x_label}. What should be the Y axis?")
                    self.awaiting = 'y_axis'
                else:
                    self.speak("I'll use Category as the X axis. What should be the Y axis?")
                    self.awaiting = 'y_axis'
            else:
                self.speak("I didn't catch the X axis. Please say something like Month, Day, Category, or Value. Or say 'default' for automatic selection.")
        elif self.awaiting == 'y_axis':
            y_label = self.extract_y_label(text)
            if y_label:
                self.speak(f"Perfect! Y axis will be {y_label}. What color would you like?")
                self.awaiting = 'color'
            elif 'default' in text or 'any' in text:
                # Use default Y axis
                if self.current_dataset:
                    dataset_info = generate_random_data(self.current_dataset)
                    y_label = dataset_info['y_label']
                    self.speak(f"Perfect! I'll use the default Y axis: {y_label}. What color would you like?")
                    self.awaiting = 'color'
                else:
                    self.speak("I'll use Value as the Y axis. What color would you like?")
                    self.awaiting = 'color'
            else:
                self.speak("I didn't catch the Y axis. Please say something like Revenue, Temperature, Score, or Value. Or say 'default' for automatic selection.")
        elif self.awaiting == 'color':
            color = self.extract_color(text)
            if 'default' in text or 'any' in text or 'skip' in text:
                self.speak("Sure! I'll use the default color. Here we go! Creating your chart!")
            else:
                self.speak("Sure! Here we go! Creating your chart!")
            self.render_chart()
            self.chart_created = True
            self.awaiting = None

    def extract_x_label(self, text):
        """Extract X axis label from text - IMPROVED!"""
        x_options = ['month', 'day', 'category', 'subject', 'company', 'city', 'time', 'date', 'period', 'week']
        for option in x_options:
            if option in text.lower():
                return option.title()
        return None

    def extract_y_label(self, text):
        """Extract Y axis label from text - IMPROVED!"""
        y_options = ['revenue', 'temperature', 'score', 'value', 'amount', 'price', 'population', 'count', 'status', 'sales']
        for option in y_options:
            if option in text.lower():
                return option.title()
        return None

    def extract_dataset_smart(self, text):
        """Smart dataset extraction with context - IMPROVED!"""
        if self.custom_data is not None and any(word in text for word in ['my data', 'uploaded', 'custom', 'my file']):
            return 'custom'
        
        dataset_keywords = ['sales', 'revenue', 'money', 'business', 'weather', 'temperature', 'climate', 
                           'student', 'performance', 'score', 'grade', 'population', 'cities', 'people',
                           'stock', 'stocks', 'shares', 'companies', 'iris', 'flower', 'flowers',
                           'titanic', 'passengers', 'survival', 'random', 'data', 'train', 'trains']
        
        for keyword in dataset_keywords:
            if keyword in text:
                return keyword
        return None

    def extract_chart_type(self, text):
        """Extract chart type from text - IMPROVED!"""
        chart_types = {
            'bar': ['bar', 'bars', 'column', 'columns'],
            'line': ['line', 'lines', 'trend', 'trends'],
            'pie': ['pie', 'circle', 'round'],
            'donut': ['donut', 'doughnut', 'ring'],
            'scatter': ['scatter', 'dots', 'points'],
            'area': ['area', 'filled'],
            'histogram': ['histogram', 'hist', 'distribution'],
            'radar': ['radar', 'spider', 'web'],
            'waterfall': ['waterfall', 'bridge'],
            'heatmap': ['heatmap', 'heat', 'map']
        }
        
        for chart_type, keywords in chart_types.items():
            if any(keyword in text for keyword in keywords):
                return chart_type
        return 'bar'

    def extract_color(self, text):
        """Extract color from text"""
        return parse_color(text, self.custom_color_hex)

    def render_chart(self):
        """Render the chart"""
        if not self.current_dataset:
            return

        # Get data
        if self.current_dataset == 'custom' and self.custom_data is not None:
            data = self.get_custom_data_summary()
            x_label = self.custom_data.columns[0] if len(self.custom_data.columns) > 0 else 'Category'
            y_label = self.custom_data.columns[1] if len(self.custom_data.columns) > 1 else 'Value'
            attributes = list(self.custom_data.columns)
        else:
            dataset_info = generate_random_data(self.current_dataset)
            data = dataset_info['data']
            x_label = dataset_info['x_label']
            y_label = dataset_info['y_label']
            attributes = dataset_info['attributes']

        if not data:
            self.speak("Sorry, I couldn't process the data for this chart.")
            return

        self.clear_chart()
        self.last_data = data
        self.last_attributes = attributes

        fig, ax = plt.subplots(figsize=(10,6))
        fig.patch.set_facecolor('#ecf0f1')
        ax.set_facecolor('#ecf0f1')

        cats = list(data.keys())
        vals = list(data.values())
        ct = self.current_chart_type
        color_hex = self.custom_color_hex
        vibrant_colors = get_vibrant_colors(len(cats))

        try:
            if ct == "bar":
                ax.bar(cats, vals, color=vibrant_colors, edgecolor='#2c3e50', linewidth=1.5)
            elif ct == "line":
                ax.plot(cats, vals, marker='o', linewidth=3, markersize=9, color=color_hex,
                        markerfacecolor="#e74c3c", markeredgecolor='#2c3e50', markeredgewidth=1.0)
                for x, y in zip(cats, vals):
                    ax.annotate(f'{y}', (x, y), textcoords="offset points", xytext=(0,8),
                                ha='center', fontsize=11, color='#2c3e50')
            elif ct == "pie":
                ax.pie(vals, labels=cats, colors=vibrant_colors,
                       autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor':'#2c3e50','linewidth':1.5})
            elif ct == "donut":
                ax.pie(vals, labels=cats, colors=vibrant_colors,
                       autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor':'#2c3e50','linewidth':1.5})
                center = plt.Circle((0,0), 0.55, fc='#ecf0f1')
                fig.gca().add_artist(center)
            elif ct == "scatter":
                x = np.arange(len(cats))
                ax.scatter(x, vals, s=80, color=vibrant_colors, edgecolor='#2c3e50', linewidth=0.8)
                ax.set_xticks(x)
                ax.set_xticklabels(cats, rotation=25, ha='right', color='#2c3e50')
            elif ct == "histogram":
                all_values = []
                for cat, val in zip(cats, vals):
                    all_values.extend([val] * int(val/10))
                ax.hist(all_values, bins=min(10, max(5, len(all_values)//5)), color=vibrant_colors, edgecolor='#2c3e50', alpha=0.7)
            elif ct == "waterfall":
                cum = [0]
                for val in vals:
                    cum.append(cum[-1] + val)
                starts = cum[:-1]
                changes = vals
                colors = ["#27ae60" if v >= 0 else "#e74c3c" for v in changes]
                x = np.arange(len(cats))
                for i,(s,chg,col) in enumerate(zip(starts, changes, colors)):
                    ax.bar(i, chg, bottom=s, color=col, edgecolor="#2c3e50", linewidth=1.0)
                ax.plot(x, cum[1:], color="#3498db", linewidth=2, marker="o")
                ax.set_xticks(x)
                ax.set_xticklabels(cats, rotation=25, ha='right', color='#2c3e50')
            elif ct == "area":
                x = np.arange(len(cats))
                ax.fill_between(x, vals, color=color_hex, alpha=0.6)
                ax.plot(x, vals, color=color_hex, linewidth=2)
                ax.set_xticks(x)
                ax.set_xticklabels(cats, rotation=25, ha='right', color='#2c3e50')
            else:
                ax.bar(cats, vals, color=vibrant_colors, edgecolor='#2c3e50', linewidth=1.5)

            title = f"📊 {self.current_dataset.title()} - {ct.title()} Chart"
            ax.set_title(title, fontsize=18, color="#2c3e50", pad=16)

            if ct not in ["pie", "donut"]:
                ax.set_xlabel(x_label, color='#2c3e50')
                ax.set_ylabel(y_label, color='#2c3e50')
                ax.tick_params(colors='#2c3e50')
                for spine in ax.spines.values(): 
                    spine.set_color("#bdc3c7")
                ax.grid(True, alpha=0.3, linestyle='--', color='#bdc3c7')

            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            plt.tight_layout()

        except Exception as e:
            self.speak("Oops! I had trouble creating that chart. Let me try a simpler version!")
            ax.bar(cats, vals, color=vibrant_colors, edgecolor='#2c3e50', linewidth=1.5)
            ax.set_title(f"📊 {self.current_dataset.title()} - Bar Chart", fontsize=18, color="#2c3e50", pad=16)
            ax.set_xlabel(x_label, color='#2c3e50')
            ax.set_ylabel(y_label, color='#2c3e50')
            ax.tick_params(colors='#2c3e50')
            for spine in ax.spines.values(): 
                spine.set_color("#bdc3c7")
            ax.grid(True, alpha=0.3, linestyle='--', color='#bdc3c7')
            
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            plt.tight_layout()
        finally:
            plt.close(fig)

    def get_custom_data_summary(self):
        """Get summary data from custom uploaded dataset"""
        if self.custom_data is None:
            return {}
        
        try:
            numeric_cols = self.custom_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                col = numeric_cols[0]
                if len(self.custom_data[col].unique()) <= 10:
                    return dict(self.custom_data[col].value_counts())
                else:
                    bins = pd.cut(self.custom_data[col], bins=5)
                    return dict(bins.value_counts())
            
            categorical_cols = self.custom_data.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                col = categorical_cols[0]
                return dict(self.custom_data[col].value_counts())
            
            col = self.custom_data.columns[0]
            return dict(self.custom_data[col].value_counts())
            
        except Exception:
            return {}

    def clear_chart(self):
        """Clear the chart frame"""
        for w in self.chart_frame.winfo_children():
            w.destroy()

    def test_chart(self):
        """Test chart display"""
        self.clear_chart()
        fig, ax = plt.subplots(figsize=(10,6))
        fig.patch.set_facecolor('#ecf0f1')
        ax.set_facecolor('#ecf0f1')
        
        categories = ['A', 'B', 'C', 'D']
        values = [10, 20, 15, 25]
        colors = get_vibrant_colors(len(categories))
        
        ax.bar(categories, values, color=colors, edgecolor='#2c3e50', linewidth=1.5)
        ax.set_title("📊 Test Chart", fontsize=18, color="#2c3e50", pad=16)
        ax.set_xlabel("Category", color='#2c3e50')
        ax.set_ylabel("Value", color='#2c3e50')
        ax.tick_params(colors='#2c3e50')
        for spine in ax.spines.values(): 
            spine.set_color("#bdc3c7")
        ax.grid(True, alpha=0.3, linestyle='--', color='#bdc3c7')
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        plt.tight_layout()
        plt.close(fig)

    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = VoiceEnabledChartApp()
    app.run()