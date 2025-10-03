#!/usr/bin/env python3
"""
🗣️ OPTIMIZED VOICE CHART CREATOR
- Dynamic dataset generation
- Context-aware conversation
- Smaller, cleaner code
- Smart understanding of follow-up requests
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
import re
import random
import os
from sklearn.datasets import load_iris, load_wine, load_breast_cancer
from sklearn.preprocessing import LabelEncoder

# ---------------- Helpers ----------------
def parse_color(text: str, fallback: str = "#00d4ff"):
    colors = {
        "blue":"#3498db","red":"#e74c3c","green":"#2ecc71","orange":"#f39c12",
        "purple":"#9b59b6","teal":"#1abc9c","gray":"#7f8c8d","grey":"#7f8c8d",
        "yellow":"#f1c40f","pink":"#ff6bb5","cyan":"#00d4ff","lime":"#b6ff00",
        "white":"#ffffff","black":"#000000","navy":"#2c3e50","maroon":"#8b0000"
    }
    if not text: return fallback
    s = text.strip().lower().replace("colour","color")
    if "skip" in s: return fallback
    for name, hexv in colors.items():
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
class OptimizedVoiceChartApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🗣️ Optimized Voice Chart Creator")
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

        # Context tracking
        self.current_dataset = None
        self.current_chart_type = 'bar'
        self.custom_color_hex = "#00d4ff"
        self.custom_x_label = None
        self.custom_y_label = None
        self.custom_data = None
        self.last_data = None  # Store last used data for context

        # Conversation state
        self.is_listening = False
        self.conversation_active = False
        self.awaiting = None
        self.first_interaction = True
        self.conversation_history = []

        self.setup_ui()
        self.speak("Hello! I'm your smart chart-making buddy! Click START CHATTING to begin!")

    def generate_dataset(self, dataset_name):
        """Generate datasets dynamically"""
        dataset_name = dataset_name.lower()
        
        if dataset_name in ['sales', 'revenue', 'money', 'business']:
            return {
                'data': {'Jan': 2000, 'Feb': 2300, 'Mar': 2100, 'Apr': 1800, 'May': 2500, 'Jun': 2700},
                'x_label': 'Month', 'y_label': 'Revenue'
            }
        elif dataset_name in ['weather', 'temperature', 'climate']:
            return {
                'data': {'Monday': 25, 'Tuesday': 28, 'Wednesday': 22, 'Thursday': 30, 'Friday': 27},
                'x_label': 'Day', 'y_label': 'Temperature'
            }
        elif dataset_name in ['student', 'performance', 'score', 'grade']:
            return {
                'data': {'Math': 85, 'Science': 92, 'English': 78, 'History': 88, 'Art': 95},
                'x_label': 'Subject', 'y_label': 'Score'
            }
        elif dataset_name in ['population', 'cities', 'people']:
            return {
                'data': {'Tokyo': 37, 'Delhi': 32, 'Shanghai': 28, 'São Paulo': 22, 'Mexico City': 21},
                'x_label': 'City', 'y_label': 'Population (Millions)'
            }
        elif dataset_name in ['stock', 'stocks', 'shares', 'companies']:
            return {
                'data': {'Apple': 150, 'Google': 2800, 'Microsoft': 300, 'Amazon': 3200, 'Tesla': 800},
                'x_label': 'Company', 'y_label': 'Price ($)'
            }
        elif dataset_name in ['iris', 'flower', 'flowers']:
            iris = load_iris()
            df = pd.DataFrame(iris.data, columns=iris.feature_names)
            df['species'] = iris.target_names[iris.target]
            species_counts = df['species'].value_counts()
            return {
                'data': dict(species_counts),
                'x_label': 'Species', 'y_label': 'Count'
            }
        elif dataset_name in ['titanic', 'passengers', 'survival']:
            return {
                'data': {'First Class': 0.63, 'Second Class': 0.47, 'Third Class': 0.24},
                'x_label': 'Class', 'y_label': 'Survival Rate'
            }
        else:
            # Generate random data for unknown datasets
            categories = [f'Category {i+1}' for i in range(5)]
            values = [random.randint(10, 100) for _ in range(5)]
            return {
                'data': dict(zip(categories, values)),
                'x_label': 'Category', 'y_label': 'Value'
            }

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        header_frame = tk.Frame(main_frame, bg='#1a1a2e')
        header_frame.pack(fill='x', pady=(0, 20))
        tk.Label(header_frame, text="🗣️ OPTIMIZED VOICE CHART CREATOR", font=('Arial', 24, 'bold'), bg='#1a1a2e', fg='#00d4ff').pack()
        tk.Label(header_frame, text="Smart context-aware chart creation!", font=('Arial', 14), bg='#1a1a2e', fg='#ffffff').pack(pady=(5,0))

        content_frame = tk.Frame(main_frame, bg='#1a1a2e')
        content_frame.pack(fill='both', expand=True)

        left_panel = tk.Frame(content_frame, bg='#16213e', width=450)
        left_panel.pack(side='left', fill='y', padx=(0, 20))
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text="🗣️ CONVERSATION", font=('Arial', 16, 'bold'), bg='#16213e', fg='#00d4ff').pack(pady=(20,15))

        self.conversation_text = tk.Text(left_panel, height=18, width=50, bg='#0f3460', fg='#ffffff', font=('Arial', 11), wrap='word', state='disabled')
        self.conversation_text.pack(padx=20, pady=(0,20))
        scr = ttk.Scrollbar(left_panel, orient='vertical', command=self.conversation_text.yview)
        scr.pack(side='right', fill='y')
        self.conversation_text.configure(yscrollcommand=scr.set)

        # Upload section
        upload_frame = tk.Frame(left_panel, bg='#16213e')
        upload_frame.pack(pady=(0, 15))
        tk.Label(upload_frame, text="📁 UPLOAD DATA", font=('Arial', 12, 'bold'), bg='#16213e', fg='#00d4ff').pack()
        upload_btn = tk.Button(upload_frame, text="📤 Upload CSV/Excel", command=self.upload_dataset, bg='#6C5CE7', fg='white', font=('Arial', 10, 'bold'))
        upload_btn.pack(pady=(5,0))

        voice_frame = tk.Frame(left_panel, bg='#16213e')
        voice_frame.pack(pady=(0, 20))
        self.mic_button = tk.Button(voice_frame, text="🎤 START CHATTING", font=('Arial', 14, 'bold'), bg='#00d4ff', fg='#1a1a2e', command=self.start_session, width=25, height=2)
        self.mic_button.pack()
        self.end_call_button = tk.Button(voice_frame, text="👋 END CHAT", font=('Arial', 12, 'bold'), bg='#ff6b6b', fg='white', command=self.end_session, width=20, height=1)

        self.status_label = tk.Label(left_panel, text="Click START CHATTING to begin...", font=('Arial', 12), bg='#16213e', fg='#00ff88')
        self.status_label.pack(pady=(10, 0))

        right_panel = tk.Frame(content_frame, bg='#16213e')
        right_panel.pack(side='right', fill='both', expand=True)
        tk.Label(right_panel, text="📊 YOUR CHARTS", font=('Arial', 16, 'bold'), bg='#16213e', fg='#00d4ff').pack(pady=(20,15))

        self.chart_frame = tk.Frame(right_panel, bg='#0f3460', height=500)
        self.chart_frame.pack(fill='both', expand=True, padx=20, pady=(0,20))

        self.chart_placeholder = tk.Label(self.chart_frame, text="🎯 Just say what you want!\n\nExamples:\n• 'Show me sales data as a pie chart'\n• 'Make it blue'\n• 'Change to line chart'\n• 'Use weather data'\n• 'Upload my data'", font=('Arial', 12), bg='#0f3460', fg='#ffffff', justify='center')
        self.chart_placeholder.pack(expand=True)

        # Quick test button
        test_btn = tk.Button(right_panel, text="🧪 Test Chart", command=self.test_chart, bg='#FF6B6B', fg='white', font=('Arial', 12, 'bold'))
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
                preview_text = f"📁 Uploaded: {os.path.basename(file_path)}\n📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns"
                messagebox.showinfo("Dataset Uploaded", preview_text)
                
                if self.conversation_active:
                    self.speak(f"Great! I've uploaded your dataset with {df.shape[0]} rows and {df.shape[1]} columns. What kind of chart would you like?")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def add_to_conversation(self, speaker, message):
        self.conversation_text.config(state='normal')
        ts = time.strftime("%H:%M:%S")
        icon = "🤖" if speaker == "Chart Buddy" else "👤"
        self.conversation_text.insert('end', f"[{ts}] {icon} {speaker}: {message}\n\n")
        self.conversation_text.tag_config('system', foreground='#00d4ff')
        self.conversation_text.tag_config('user', foreground='#00ff88')
        self.conversation_text.config(state='disabled')
        self.conversation_text.see('end')
        
        # Store in history
        self.conversation_history.append((speaker, message))

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
        
        if self.first_interaction:
            self.speak("Hello! Welcome! I'm your smart chart-making buddy. What kind of chart would you like to create? You can say everything at once or I can guide you step by step!")
            self.first_interaction = False
        else:
            greetings = ["Hey! What should we create?", "Hi! Ready to make charts?", "Hello! What interests you?"]
            self.speak(random.choice(greetings))
        
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def end_session(self):
        self.conversation_active = False
        self.is_listening = False
        self.awaiting = None
        self.end_call_button.pack_forget()
        self.mic_button.pack()
        self.status_label.config(text="Chat ended. Click START CHATTING to begin again...", fg='#ff6b6b')
        self.speak("Thanks for chatting! Hope you enjoyed creating charts!")

    def listen_loop(self):
        while self.conversation_active and self.is_listening:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                self.add_to_conversation("You", text)
                self.process_smart_request(text)
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

    def process_smart_request(self, text: str):
        t = (text or "").lower().strip()

        # End conversation
        if any(w in t for w in ["goodbye", "bye", "end chat", "stop", "exit", "quit"]):
            self.speak("Goodbye! It was fun creating charts with you!")
            self.end_session()
            return

        # Handle awaiting states
        if self.awaiting:
            self.handle_awaiting_state(t)
            return

        # Smart context understanding
        dataset = self.extract_dataset_smart(t)
        chart_type = self.extract_chart_type(t)
        color = self.extract_color(t)
        
        # Check for context-based requests
        if self.is_context_request(t):
            self.handle_context_request(t, dataset, chart_type, color)
        elif dataset:
            # New dataset request
            self.handle_new_dataset_request(dataset, chart_type, color)
        else:
            # Help or unclear request
            self.handle_help_request(t)

    def is_context_request(self, text):
        """Check if this is a follow-up request using context"""
        context_words = ['change', 'make it', 'use', 'switch', 'different', 'another', 'same', 'this', 'that']
        return any(word in text for word in context_words) and self.current_dataset

    def handle_context_request(self, text, dataset, chart_type, color):
        """Handle requests that use previous context"""
        if 'color' in text or 'blue' in text or 'red' in text or 'green' in text:
            # Color change request
            new_color = self.extract_color(text)
            self.custom_color_hex = new_color
            self.speak(f"Changing color to {new_color}! Creating your chart...")
            self.render_chart()
        elif 'chart' in text or any(ct in text for ct in ['bar', 'line', 'pie', 'donut', 'scatter']):
            # Chart type change
            new_type = self.extract_chart_type(text)
            self.current_chart_type = new_type
            self.speak(f"Changing to {new_type} chart! Creating your chart...")
            self.render_chart()
        elif dataset:
            # New dataset with same context
            self.current_dataset = dataset
            self.speak(f"Switching to {dataset} data! Creating your chart...")
            self.render_chart()
        else:
            # Generic change request
            self.speak("What would you like to change? Chart type, color, or dataset?")

    def handle_new_dataset_request(self, dataset, chart_type, color):
        """Handle new dataset requests"""
        self.current_dataset = dataset
        self.current_chart_type = chart_type
        self.custom_color_hex = color
        
        if chart_type != 'bar':  # User specified chart type
            self.speak(f"Perfect! Creating a {chart_type} chart for {dataset} data!")
            self.render_chart()
        else:
            # Ask for chart type
            self.speak(f"Great! I'll use {dataset} data. What type of chart would you like?")
            self.awaiting = 'chart_type'

    def handle_help_request(self, text):
        """Handle help or unclear requests"""
        if any(w in text for w in ["help", "what can you do", "how", "what"]):
            self.speak("I can create charts from sales, weather, student, population, stock, iris, or titanic data! You can also upload your own CSV or Excel file. Just tell me what you want!")
        elif any(w in text for w in ["hello", "hi", "hey"]):
            responses = ["Hey! What kind of chart should we make?", "Hi! Ready to create something?", "Hello! What interests you?"]
            self.speak(random.choice(responses))
        else:
            self.speak("I'm not sure what you want to create. Try saying something like 'show me sales data' or 'make a weather chart'!")

    def handle_awaiting_state(self, text):
        """Handle step-by-step conversation"""
        if self.awaiting == 'chart_type':
            chart_type = self.extract_chart_type(text)
            if chart_type:
                self.current_chart_type = chart_type
                self.speak(f"Perfect! A {chart_type} chart. What color would you like?")
                self.awaiting = 'color'
            else:
                self.speak("I didn't catch the chart type. Please say bar, line, pie, donut, scatter, histogram, area, radar, waterfall, or heatmap.")
        elif self.awaiting == 'color':
            color = self.extract_color(text)
            self.custom_color_hex = color
            self.render_chart()
            self.speak("There you go! Your chart is ready. Want to create another one?")
            self.awaiting = None

    def extract_dataset_smart(self, text):
        """Smart dataset extraction with context"""
        # Check for uploaded data first
        if self.custom_data is not None and any(word in text for word in ['my data', 'uploaded', 'custom', 'my file']):
            return 'custom'
        
        # Check for dataset keywords
        dataset_keywords = {
            'sales': ['sales', 'revenue', 'money', 'business', 'income'],
            'weather': ['weather', 'temperature', 'climate', 'hot', 'cold'],
            'students': ['student', 'performance', 'score', 'grade', 'subject'],
            'population': ['population', 'cities', 'people', 'demographics'],
            'stock': ['stock', 'stocks', 'shares', 'companies', 'market'],
            'iris': ['iris', 'flower', 'flowers', 'petal', 'sepal'],
            'titanic': ['titanic', 'passengers', 'survival', 'ship']
        }
        
        for dataset_name, keywords in dataset_keywords.items():
            if any(keyword in text for keyword in keywords):
                return dataset_name
        return None

    def extract_chart_type(self, text):
        """Extract chart type from text"""
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
        else:
            dataset_info = self.generate_dataset(self.current_dataset)
            data = dataset_info['data']
            x_label = dataset_info['x_label']
            y_label = dataset_info['y_label']

        if not data:
            self.speak("Sorry, I couldn't process the data for this chart.")
            return

        self.clear_chart()
        self.last_data = data  # Store for context

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
            else:
                ax.bar(cats, vals, color=palette_variants(color_hex, len(cats)), edgecolor='white', linewidth=1.5)

            title = f"📊 {self.current_dataset.title()} - {ct.title()} Chart"
            ax.set_title(title, fontsize=18, color="#00d4ff", pad=16)

            if ct not in ["pie", "donut"]:
                ax.set_xlabel(x_label, color='white')
                ax.set_ylabel(y_label, color='white')
                ax.tick_params(colors='white')
                for spine in ax.spines.values(): 
                    spine.set_color("#00d4ff")
                ax.grid(True, alpha=0.18, linestyle='--', color='white')

            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            plt.tight_layout()

        except Exception as e:
            self.speak("Oops! I had trouble creating that chart. Let me try a simpler version!")
            ax.bar(cats, vals, color=palette_variants(color_hex, len(cats)), edgecolor='white', linewidth=1.5)
            ax.set_title(f"📊 {self.current_dataset.title()} - Bar Chart", fontsize=18, color="#00d4ff", pad=16)
            ax.set_xlabel(x_label, color='white')
            ax.set_ylabel(y_label, color='white')
            ax.tick_params(colors='white')
            for spine in ax.spines.values(): 
                spine.set_color("#00d4ff")
            ax.grid(True, alpha=0.18, linestyle='--', color='white')
            
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
        fig.patch.set_facecolor('#0f3460')
        ax.set_facecolor('#0f3460')
        
        categories = ['A', 'B', 'C', 'D']
        values = [10, 20, 15, 25]
        
        ax.bar(categories, values, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'], edgecolor='white', linewidth=1.5)
        ax.set_title("📊 Test Chart", fontsize=18, color="#00d4ff", pad=16)
        ax.set_xlabel("Category", color='white')
        ax.set_ylabel("Value", color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values(): 
            spine.set_color("#00d4ff")
        ax.grid(True, alpha=0.18, linestyle='--', color='white')
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        plt.tight_layout()
        plt.close(fig)

    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = OptimizedVoiceChartApp()
    app.run()