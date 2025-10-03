#!/usr/bin/env python3
"""
🗣️ ENHANCED FRIENDLY VOICE CHART CREATOR
- Natural greeting and conversation flow
- One-go chart generation OR step-by-step fallback
- Custom dataset upload functionality
- Multiple built-in datasets (Iris, Titanic, etc.)
- Smart conversation handling
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import time
import threading
import speech_recognition as sr
import pyttsx3
from PIL import Image, ImageTk
import re
import random
import os
from sklearn.datasets import load_iris, load_wine, load_breast_cancer
from sklearn.preprocessing import LabelEncoder

# ---------------- Helpers ----------------
def closest_choice(spoken: str, choices: list[str], cutoff: float = 0.55):
    if not spoken or not choices:
        return None
    s = spoken.lower().strip()
    lc = [c.lower() for c in choices]
    for c in choices:
        if c.lower() == s or c.lower() in s or s in c.lower():
            return c
    best = None; best_score = 0
    for c in choices:
        cl = c.lower()
        score = 0
        for token in s.split():
            if token in cl: score += len(token)
        if s and cl.startswith(s[: max(1, len(s)//2)]): score += 2
        if score > best_score:
            best_score = score; best = c
    return best if best_score >= max(1, len(s)//3) else None

NAMED_COLORS = {
    "blue":"#3498db","red":"#e74c3c","green":"#2ecc71","orange":"#f39c12",
    "purple":"#9b59b6","teal":"#1abc9c","gray":"#7f8c8d","grey":"#7f8c8d",
    "yellow":"#f1c40f","pink":"#ff6bb5","cyan":"#00d4ff","lime":"#b6ff00",
    "white":"#ffffff","black":"#000000","navy":"#2c3e50","maroon":"#8b0000"
}

def parse_color(text: str, fallback: str = "#00d4ff"):
    if not text: return fallback
    s = text.strip().lower().replace("colour","color")
    if "skip" in s: return fallback
    for name, hexv in NAMED_COLORS.items():
        if name in s: return hexv
    s = s.replace(" ","")
    if s.startswith("#") and len(s) in (4,7): return s
    if len(s) in (3,6):
        try:
            int(s, 16)
            return "#" + s
        except: pass
    return fallback

def palette_variants(base_hex: str, n: int):
    base_hex = base_hex.lstrip("#")
    if len(base_hex) == 3:
        base_hex = "".join([c*2 for c in base_hex])
    r = int(base_hex[0:2],16); g = int(base_hex[2:4],16); b = int(base_hex[4:6],16)
    out = []
    for i in range(n):
        f = 0.3 + 0.7*(i/(max(1,n-1)))
        out.append("#%02x%02x%02x" % (int(r*f), int(g*f), int(b*f)))
    return out

# -------------- App ----------------------
class EnhancedVoiceChartApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🗣️ Enhanced Friendly Voice Chart Creator")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a2e')

        # STT/TTS
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone()
        except Exception:
            self.microphone = None
        self.engine = pyttsx3.init('sapi5')
        self.engine.setProperty('rate', 170)
        self.engine.setProperty('volume', 1.0)

        # Data
        self.SAMPLE_DATASETS = {
            'sales': {
                'data': {'Jan': 2000, 'Feb': 2300, 'Mar': 2100, 'Apr': 1800, 'May': 2500, 'Jun': 2700},
                'description': 'Monthly sales revenue trends',
                'default_x_label': 'Month',
                'default_y_label': 'Revenue',
                'keywords': ['sales', 'revenue', 'money', 'business', 'income', 'earnings']
            },
            'weather': {
                'data': {'Monday': 25, 'Tuesday': 28, 'Wednesday': 22, 'Thursday': 30, 'Friday': 27},
                'description': 'Daily temperature for the week',
                'default_x_label': 'Day',
                'default_y_label': 'Temperature',
                'keywords': ['weather', 'temperature', 'climate', 'hot', 'cold', 'degrees']
            },
            'students': {
                'data': {'Math': 85, 'Science': 92, 'English': 78, 'History': 88, 'Art': 95},
                'description': 'Student performance by subject',
                'default_x_label': 'Subject',
                'default_y_label': 'Score',
                'keywords': ['student', 'performance', 'score', 'grade', 'subject', 'marks', 'grades']
            },
            'population': {
                'data': {'Tokyo': 37, 'Delhi': 32, 'Shanghai': 28, 'São Paulo': 22, 'Mexico City': 21},
                'description': 'Population of major cities (millions)',
                'default_x_label': 'City',
                'default_y_label': 'Population (Millions)',
                'keywords': ['population', 'cities', 'people', 'demographics']
            },
            'stock': {
                'data': {'Apple': 150, 'Google': 2800, 'Microsoft': 300, 'Amazon': 3200, 'Tesla': 800},
                'description': 'Stock prices of major companies',
                'default_x_label': 'Company',
                'default_y_label': 'Price ($)',
                'keywords': ['stock', 'stocks', 'shares', 'companies', 'market', 'investing']
            },
            'iris': {
                'data': self.load_iris_data(),
                'description': 'Iris flower measurements',
                'default_x_label': 'Species',
                'default_y_label': 'Sepal Length',
                'keywords': ['iris', 'flower', 'flowers', 'petal', 'sepal', 'botany']
            },
            'titanic': {
                'data': self.load_titanic_data(),
                'description': 'Titanic passenger survival data',
                'default_x_label': 'Class',
                'default_y_label': 'Survival Rate',
                'keywords': ['titanic', 'passengers', 'survival', 'ship', 'disaster']
            }
        }

        self.current_dataset = None
        self.current_chart_type = 'bar'
        self.custom_color_hex = "#00d4ff"
        self.custom_x_label = None
        self.custom_y_label = None
        self.custom_data = None  # For uploaded datasets

        # Conversation
        self.is_listening = False
        self.conversation_active = False
        self.last_heard = ""
        self.conversation_count = 0
        self.awaiting = None  # None | 'chart_type' | 'x_axis' | 'y_axis' | 'color' | 'dataset'
        self.first_interaction = True

        self.setup_ui()
        self.speak("Hello! I'm your friendly chart-making buddy! Click START CHATTING to begin our conversation!")

    def load_iris_data(self):
        """Load Iris dataset"""
        iris = load_iris()
        df = pd.DataFrame(iris.data, columns=iris.feature_names)
        df['species'] = iris.target_names[iris.target]
        
        # Create sample data for visualization
        species_counts = df['species'].value_counts()
        return dict(species_counts)

    def load_titanic_data(self):
        """Load Titanic dataset"""
        # Create sample Titanic data
        titanic_data = {
            'First Class': 0.63,
            'Second Class': 0.47,
            'Third Class': 0.24
        }
        return titanic_data

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        header_frame = tk.Frame(main_frame, bg='#1a1a2e')
        header_frame.pack(fill='x', pady=(0, 20))
        tk.Label(header_frame, text="🗣️ ENHANCED FRIENDLY VOICE CHART CREATOR", font=('Arial', 24, 'bold'), bg='#1a1a2e', fg='#00d4ff').pack()
        tk.Label(header_frame, text="Say everything at once OR let me guide you step-by-step!", font=('Arial', 14), bg='#1a1a2e', fg='#ffffff').pack(pady=(5,0))

        content_frame = tk.Frame(main_frame, bg='#1a1a2e')
        content_frame.pack(fill='both', expand=True)

        left_panel = tk.Frame(content_frame, bg='#16213e', width=450)
        left_panel.pack(side='left', fill='y', padx=(0, 20))
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text="🗣️ OUR CONVERSATION", font=('Arial', 16, 'bold'), bg='#16213e', fg='#00d4ff').pack(pady=(20,15))

        self.conversation_text = tk.Text(left_panel, height=18, width=50, bg='#0f3460', fg='#ffffff', font=('Arial', 11), wrap='word', state='disabled')
        self.conversation_text.pack(padx=20, pady=(0,20))
        scr = ttk.Scrollbar(left_panel, orient='vertical', command=self.conversation_text.yview)
        scr.pack(side='right', fill='y')
        self.conversation_text.configure(yscrollcommand=scr.set)

        # Upload section
        upload_frame = tk.Frame(left_panel, bg='#16213e')
        upload_frame.pack(pady=(0, 15))
        tk.Label(upload_frame, text="📁 UPLOAD YOUR DATA", font=('Arial', 12, 'bold'), bg='#16213e', fg='#00d4ff').pack()
        upload_btn = tk.Button(upload_frame, text="📤 Upload CSV/Excel", command=self.upload_dataset, bg='#6C5CE7', fg='white', font=('Arial', 10, 'bold'))
        upload_btn.pack(pady=(5,0))

        voice_frame = tk.Frame(left_panel, bg='#16213e')
        voice_frame.pack(pady=(0, 20))
        self.mic_button = tk.Button(voice_frame, text="🎤 START CHATTING", font=('Arial', 14, 'bold'), bg='#00d4ff', fg='#1a1a2e', command=self.start_session, width=25, height=2)
        self.mic_button.pack()
        self.end_call_button = tk.Button(voice_frame, text="👋 END CHAT", font=('Arial', 12, 'bold'), bg='#ff6b6b', fg='white', command=self.end_session, width=20, height=1)

        self.status_label = tk.Label(left_panel, text="Click START CHATTING to begin our conversation...", font=('Arial', 12), bg='#16213e', fg='#00ff88')
        self.status_label.pack(pady=(10, 0))

        right_panel = tk.Frame(content_frame, bg='#16213e')
        right_panel.pack(side='right', fill='both', expand=True)
        tk.Label(right_panel, text="📊 YOUR CHARTS", font=('Arial', 16, 'bold'), bg='#16213e', fg='#00d4ff').pack(pady=(20,15))

        self.chart_frame = tk.Frame(right_panel, bg='#0f3460', height=500)
        self.chart_frame.pack(fill='both', expand=True, padx=20, pady=(0,20))

        self.chart_placeholder = tk.Label(self.chart_frame, text="🎯 Just say what you want!\n\nExamples:\n• 'Show me sales data as a pie chart'\n• 'Make a blue bar chart for weather'\n• 'I want a line chart for student grades'\n• 'Create a donut chart with red colors'\n• 'Upload my data and make a scatter plot'\n• 'Use iris dataset for a histogram'", font=('Arial', 12), bg='#0f3460', fg='#ffffff', justify='center')
        self.chart_placeholder.pack(expand=True)

        quick_frame = tk.Frame(right_panel, bg='#16213e')
        quick_frame.pack(pady=(0,20))
        tk.Label(quick_frame, text="Quick Examples:", font=('Arial', 12, 'bold'), bg='#16213e', fg='#ffffff').pack()
        btns = tk.Frame(quick_frame, bg='#16213e'); btns.pack(pady=(10,0))
        tk.Button(btns, text="💰 Sales", command=lambda: self.quick_create('sales'), bg='#FF6B6B', fg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=3)
        tk.Button(btns, text="🌤️ Weather", command=lambda: self.quick_create('weather'), bg='#74B9FF', fg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=3)
        tk.Button(btns, text="📚 Students", command=lambda: self.quick_create('students'), bg='#6C5CE7', fg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=3)
        tk.Button(btns, text="🏙️ Cities", command=lambda: self.quick_create('population'), bg='#00B894', fg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=3)
        tk.Button(btns, text="🌸 Iris", command=lambda: self.quick_create('iris'), bg='#E17055', fg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=3)

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
                
                # Store the dataframe
                self.custom_data = df
                
                # Show preview
                preview_text = f"📁 Uploaded: {os.path.basename(file_path)}\n"
                preview_text += f"📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
                preview_text += f"📋 Columns: {', '.join(df.columns[:5])}"
                if len(df.columns) > 5:
                    preview_text += "..."
                
                messagebox.showinfo("Dataset Uploaded", preview_text)
                
                if self.conversation_active:
                    self.speak(f"Great! I've uploaded your dataset with {df.shape[0]} rows and {df.shape[1]} columns. What kind of chart would you like to create?")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def add_to_conversation(self, speaker, message):
        self.conversation_text.config(state='normal')
        ts = time.strftime("%H:%M:%S")
        tag = 'system' if speaker == "Chart Buddy" else 'user'
        icon = "🤖" if tag == 'system' else "👤"
        self.conversation_text.insert('end', f"[{ts}] {icon} {speaker}: {message}\n\n", tag)
        self.conversation_text.tag_config('system', foreground='#00d4ff')
        self.conversation_text.tag_config('user', foreground='#00ff88')
        self.conversation_text.config(state='disabled')
        self.conversation_text.see('end')

    def speak(self, text):
        self.add_to_conversation("Chart Buddy", text)
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception:
            pass

    def start_session(self):
        if self.microphone is None:
            self.add_to_conversation("Chart Buddy", "No microphone found. Please connect a mic and restart.")
            return
        self.conversation_active = True
        self.is_listening = True
        self.mic_button.pack_forget()
        self.end_call_button.pack()
        self.status_label.config(text="🟢 Chatting active - I'm listening!", fg='#00ff88')
        
        # Natural greeting and first question
        if self.first_interaction:
            self.speak("Hello! Welcome! I'm your friendly chart-making buddy. What kind of chart would you like to create today? You can tell me everything at once - like 'show me sales data as a pie chart' - or I can guide you step by step!")
            self.first_interaction = False
        else:
            greetings = [
                "Hey! What should we create today?",
                "Hi! Ready to make some charts?",
                "Hello! What data interests you?",
                "Hey there! What kind of chart are you thinking about?"
            ]
            self.speak(random.choice(greetings))
        
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def end_session(self):
        self.conversation_active = False
        self.is_listening = False
        self.awaiting = None
        self.end_call_button.pack_forget()
        self.mic_button.pack()
        self.status_label.config(text="Chat ended. Click START CHATTING to begin again...", fg='#ff6b6b')
        self.speak("Thanks for chatting! Hope you enjoyed creating charts together!")

    def listen_loop(self):
        while self.conversation_active and self.is_listening:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                self.last_heard = text
                self.add_to_conversation("You", text)
                self.process_natural_request(text)
                time.sleep(0.2)
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't catch that. Could you say it again?")
                continue
            except sr.RequestError:
                self.speak("Hmm, having trouble hearing you. Try once more!")
                continue
            except Exception:
                self.speak("Oops, something went wrong. Let's continue!")
                continue

    def process_natural_request(self, text: str):
        t = (text or "").lower().strip()
        self.conversation_count += 1

        # End conversation
        if any(w in t for w in ["goodbye", "bye", "end chat", "end session", "stop", "exit", "quit", "see you", "talk later"]):
            self.speak("Goodbye! It was fun creating charts with you!")
            self.end_session()
            return

        # Handle awaiting states (step-by-step mode)
        if self.awaiting:
            self.handle_awaiting_state(t)
            return

        # Extract all preferences in one go
        dataset = self.extract_dataset(t)
        chart_type = self.extract_chart_type(t)
        color = self.extract_color(t)
        x_label = self.extract_x_label(t)
        y_label = self.extract_y_label(t)

        # Check if user gave complete information
        complete_info = dataset and chart_type != 'bar'  # bar is default, so if they didn't specify, it's incomplete

        if dataset and complete_info:
            # User gave complete info - create chart immediately
            self.create_chart_from_preferences(dataset, chart_type, color, x_label, y_label)
        elif dataset:
            # User gave dataset but incomplete info - ask for specifics
            self.speak(f"Great! I see you want to work with {dataset} data. What type of chart would you like? You can say bar, line, pie, donut, scatter, histogram, area, radar, waterfall, or heatmap.")
            self.awaiting = 'chart_type'
        else:
            # No dataset identified - ask for help
            if any(w in t for w in ["help", "what can you do", "how", "what"]):
                self.speak("I can create charts from sales, weather, student, population, stock, iris, or titanic data! You can also upload your own CSV or Excel file. Just tell me what you want, like 'show me sales as a pie chart' or 'make a blue bar chart for weather'.")
            elif any(w in t for w in ["hello", "hi", "hey"]):
                responses = [
                    "Hey! What kind of chart should we make?",
                    "Hi there! Ready to create something awesome?",
                    "Hello! What data interests you today?"
                ]
                self.speak(random.choice(responses))
            else:
                self.speak("I'm not sure what you want to create. Try saying something like 'show me sales data' or 'make a weather chart'! You can also upload your own data file.")

    def handle_awaiting_state(self, text: str):
        """Handle step-by-step conversation flow"""
        if self.awaiting == 'chart_type':
            chart_type = self.extract_chart_type(text)
            if chart_type:
                self.current_chart_type = chart_type
                self.speak(f"Perfect! A {chart_type} chart. What should the X-axis be? You can say the default or something else.")
                self.awaiting = 'x_axis'
            else:
                self.speak("I didn't catch the chart type. Please say bar, line, pie, donut, scatter, histogram, area, radar, waterfall, or heatmap.")

        elif self.awaiting == 'x_axis':
            x_label = self.extract_x_label(text)
            if not x_label:
                x_label = self.get_default_x_label()
                self.speak("I'll use the default X-axis label.")
            self.custom_x_label = x_label
            self.speak("Great! What should the Y-axis be? You can say the default or something else.")
            self.awaiting = 'y_axis'

        elif self.awaiting == 'y_axis':
            y_label = self.extract_y_label(text)
            if not y_label:
                y_label = self.get_default_y_label()
                self.speak("I'll use the default Y-axis label.")
            self.custom_y_label = y_label
            self.speak("Perfect! What color should I use? Say a color like blue, red, green, or skip for default.")
            self.awaiting = 'color'

        elif self.awaiting == 'color':
            color = self.extract_color(text)
            self.custom_color_hex = color
            self.render_chart()
            self.speak("There you go! Your chart is ready. Want to create another one or modify this one?")
            self.awaiting = None

    def extract_dataset(self, text: str):
        """Extract dataset from natural language"""
        # Check for uploaded data first
        if self.custom_data is not None and any(word in text for word in ['my data', 'uploaded', 'custom', 'my file']):
            return 'custom'
        
        # Check built-in datasets
        for dataset_name, dataset_info in self.SAMPLE_DATASETS.items():
            if any(keyword in text for keyword in dataset_info['keywords']):
                return dataset_name
        return None

    def extract_chart_type(self, text: str):
        """Extract chart type from natural language"""
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
        return 'bar'  # default

    def extract_color(self, text: str):
        """Extract color from natural language"""
        return parse_color(text, "#00d4ff")

    def extract_x_label(self, text: str):
        """Extract X-axis label from natural language"""
        if self.current_dataset and self.current_dataset in self.SAMPLE_DATASETS:
            dataset_info = self.SAMPLE_DATASETS[self.current_dataset]
            x_patterns = {
                'sales': ['month', 'time', 'period'],
                'weather': ['day', 'date', 'time'],
                'students': ['subject', 'course'],
                'population': ['city', 'cities'],
                'stock': ['company', 'companies'],
                'iris': ['species', 'flower'],
                'titanic': ['class', 'passenger']
            }
            
            if self.current_dataset in x_patterns:
                for pattern in x_patterns[self.current_dataset]:
                    if pattern in text:
                        return dataset_info['default_x_label']
        return None

    def extract_y_label(self, text: str):
        """Extract Y-axis label from natural language"""
        if self.current_dataset and self.current_dataset in self.SAMPLE_DATASETS:
            dataset_info = self.SAMPLE_DATASETS[self.current_dataset]
            y_patterns = {
                'sales': ['revenue', 'money', 'amount', 'income'],
                'weather': ['temperature', 'degrees', 'temp'],
                'students': ['score', 'grade', 'marks'],
                'population': ['population', 'people', 'millions'],
                'stock': ['price', 'value', 'cost'],
                'iris': ['length', 'width', 'measurement'],
                'titanic': ['survival', 'rate', 'percentage']
            }
            
            if self.current_dataset in y_patterns:
                for pattern in y_patterns[self.current_dataset]:
                    if pattern in text:
                        return dataset_info['default_y_label']
        return None

    def get_default_x_label(self):
        """Get default X-axis label for current dataset"""
        if self.current_dataset == 'custom' and self.custom_data is not None:
            return self.custom_data.columns[0] if len(self.custom_data.columns) > 0 else 'X'
        elif self.current_dataset in self.SAMPLE_DATASETS:
            return self.SAMPLE_DATASETS[self.current_dataset]['default_x_label']
        return 'Category'

    def get_default_y_label(self):
        """Get default Y-axis label for current dataset"""
        if self.current_dataset == 'custom' and self.custom_data is not None:
            return self.custom_data.columns[1] if len(self.custom_data.columns) > 1 else 'Value'
        elif self.current_dataset in self.SAMPLE_DATASETS:
            return self.SAMPLE_DATASETS[self.current_dataset]['default_y_label']
        return 'Value'

    def create_chart_from_preferences(self, dataset, chart_type, color, x_label, y_label):
        """Create chart with all preferences at once"""
        if dataset == 'custom' and self.custom_data is None:
            self.speak("Please upload your data file first!")
            return
        
        if dataset not in self.SAMPLE_DATASETS and dataset != 'custom':
            self.speak(f"Sorry, I don't have {dataset} data. Try sales, weather, students, population, stock, iris, or titanic!")
            return

        self.current_dataset = dataset
        self.current_chart_type = chart_type
        self.custom_color_hex = color
        self.custom_x_label = x_label or self.get_default_x_label()
        self.custom_y_label = y_label or self.get_default_y_label()

        # Friendly confirmation
        dataset_name = dataset.title()
        chart_name = chart_type.title()
        color_name = "default" if color == "#00d4ff" else "your chosen"
        
        confirmation = f"Perfect! Creating a {chart_name} chart for {dataset_name} data with {color_name} colors!"
        self.speak(confirmation)

        # Create the chart
        self.render_chart()

        # Ask what's next
        next_responses = [
            "There you go! Want to try something else?",
            "Awesome! What should we create next?",
            "Cool chart! Ready for another one?",
            "Nice! Want to make a different chart?",
            "Great! What's next on your mind?"
        ]
        self.speak(random.choice(next_responses))

    def render_chart(self):
        """Render the chart with current preferences"""
        if not self.current_dataset:
            return

        # Get data
        if self.current_dataset == 'custom' and self.custom_data is not None:
            data = self.get_custom_data_summary()
        else:
            data = self.SAMPLE_DATASETS[self.current_dataset]['data']
        
        if not data:
            self.speak("Sorry, I couldn't process the data for this chart.")
            return

        self.clear_chart()

        fig, ax = plt.subplots(figsize=(10,6))
        fig.patch.set_facecolor('#0f3460')
        ax.set_facecolor('#0f3460')

        cats = list(data.keys())
        vals = list(data.values())
        ct = self.current_chart_type
        color_hex = self.custom_color_hex

        try:
            if ct == "bar":
                ax.bar(cats, vals, color=palette_variants(color_hex, len(cats)), edgecolor='white', linewidth=1.5)

            elif ct == "line":
                ax.plot(cats, vals, marker='o', linewidth=3, markersize=9, color=color_hex,
                        markerfacecolor="#00ff88", markeredgecolor='white', markeredgewidth=1.0)
                for x, y in zip(cats, vals):
                    ax.annotate(f'{y}', (x, y), textcoords="offset points", xytext=(0,8),
                                ha='center', fontsize=11, color='white')

            elif ct == "area":
                x = np.arange(len(cats))
                ax.fill_between(x, vals, color=color_hex, alpha=0.35)
                ax.plot(x, vals, color=color_hex, linewidth=2)
                ax.set_xticks(x)
                ax.set_xticklabels(cats, rotation=25, ha='right', color='white')

            elif ct == "pie":
                ax.pie(vals, labels=cats, colors=palette_variants(color_hex, len(cats)),
                       autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor':'white','linewidth':1.5})

            elif ct == "donut":
                ax.pie(vals, labels=cats, colors=palette_variants(color_hex, len(cats)),
                       autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor':'white','linewidth':1.5})
                center = plt.Circle((0,0), 0.55, fc='#0f3460')
                fig.gca().add_artist(center)

            elif ct == "scatter":
                x = np.arange(len(cats))
                ax.scatter(x, vals, s=80, color=color_hex, edgecolor='white', linewidth=0.8)
                ax.set_xticks(x)
                ax.set_xticklabels(cats, rotation=25, ha='right', color='white')

            elif ct == "histogram":
                ax.hist(vals, bins=min(10, max(5, len(vals)//2)), color=color_hex, edgecolor='white')

            elif ct == "radar":
                N = len(vals)
                angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
                angles += angles[:1]
                v = np.array(vals, dtype=float).tolist()
                v += v[:1]
                ax = fig.add_subplot(111, polar=True, facecolor="#0f3460")
                ax.plot(angles, v, color=color_hex, linewidth=2)
                ax.fill(angles, v, color=color_hex, alpha=0.25)
                ax.set_thetagrids(np.degrees(angles[:-1]), cats, color='white')
                ax.tick_params(colors='white')
                ax.grid(color="#1f2a3a")

            elif ct == "waterfall":
                cum = [0]
                for val in vals:
                    cum.append(cum[-1] + val)
                starts = cum[:-1]
                changes = vals
                colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in changes]
                x = np.arange(len(cats))
                for i,(s,chg,col) in enumerate(zip(starts, changes, colors)):
                    ax.bar(i, chg, bottom=s, color=col, edgecolor="white", linewidth=1.0)
                ax.plot(x, cum[1:], color="#00d4ff", linewidth=2, marker="o")
                ax.set_xticks(x)
                ax.set_xticklabels(cats, rotation=25, ha='right', color='white')

            elif ct == "heatmap":
                mat = np.array(vals, dtype=float)[None, :]
                im = ax.imshow(mat, aspect='auto', cmap='coolwarm')
                ax.set_yticks([0])
                ax.set_yticklabels(['Value'], color='white')
                ax.set_xticks(range(len(cats)))
                ax.set_xticklabels(cats, rotation=25, ha='right', color='white')
                plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

            else:
                ax.bar(cats, vals, color=palette_variants(color_hex, len(cats)), edgecolor='white', linewidth=1.5)

            title = f"📊 {self.current_dataset.title()} - {ct.title()} Chart"
            ax.set_title(title, fontsize=18, color="#00d4ff", pad=16)

            if ct not in ["pie","donut","radar","heatmap"]:
                ax.set_xlabel(self.custom_x_label, color='white')
                ax.set_ylabel(self.custom_y_label, color='white')
                ax.tick_params(colors='white')
                for spine in ax.spines.values(): 
                    spine.set_color("#00d4ff")
                ax.grid(True, alpha=0.18, linestyle='--', color='white')

            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

        except Exception as e:
            self.speak("Oops! I had trouble creating that chart. Let me try a simpler version!")
            # Fallback to bar chart
            ax.bar(cats, vals, color=palette_variants(color_hex, len(cats)), edgecolor='white', linewidth=1.5)
            ax.set_title(f"📊 {self.current_dataset.title()} - Bar Chart", fontsize=18, color="#00d4ff", pad=16)
            ax.set_xlabel(self.custom_x_label, color='white')
            ax.set_ylabel(self.custom_y_label, color='white')
            ax.tick_params(colors='white')
            for spine in ax.spines.values(): 
                spine.set_color("#00d4ff")
            ax.grid(True, alpha=0.18, linestyle='--', color='white')
            
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
        finally:
            plt.close(fig)

    def get_custom_data_summary(self):
        """Get summary data from custom uploaded dataset"""
        if self.custom_data is None:
            return {}
        
        # Try to create a meaningful summary
        try:
            # If numeric columns exist, use first numeric column
            numeric_cols = self.custom_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                col = numeric_cols[0]
                if len(self.custom_data[col].unique()) <= 10:  # If few unique values, use as categories
                    return dict(self.custom_data[col].value_counts())
                else:  # If many values, create bins
                    bins = pd.cut(self.custom_data[col], bins=5)
                    return dict(bins.value_counts())
            
            # If no numeric columns, use first categorical column
            categorical_cols = self.custom_data.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                col = categorical_cols[0]
                return dict(self.custom_data[col].value_counts())
            
            # Fallback: use first column
            col = self.custom_data.columns[0]
            return dict(self.custom_data[col].value_counts())
            
        except Exception:
            return {}

    def clear_chart(self):
        """Clear the chart frame"""
        for w in self.chart_frame.winfo_children():
            w.destroy()

    def quick_create(self, dataset):
        """Quick create for button clicks"""
        if not self.conversation_active:
            self.speak("Please click START CHATTING first!")
            return
        self.create_chart_from_preferences(dataset, 'bar', '#00d4ff', None, None)

    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = EnhancedVoiceChartApp()
    app.run()