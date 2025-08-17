#!/usr/bin/env python3
"""
📞 PHONE CALL STYLE Voice-Enabled Chart Creator
======================================================================
This opens a beautiful interface automatically and works like a phone call!
You speak, it speaks back, and charts appear on screen!
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np
import os
import time
import threading
import speech_recognition as sr
import pyttsx3
from PIL import Image, ImageTk
import io

class PhoneCallChartApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📞 Phone Call Chart Creator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Initialize speech recognition and TTS
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        
        # Sample datasets
        self.SAMPLE_DATASETS = {
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
        
        self.current_dataset = None
        self.current_chart_type = 'bar'
        self.is_listening = False
        
        self.setup_ui()
        self.start_conversation()
        
    def setup_ui(self):
        """Create the beautiful phone call interface"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header - Phone call style
        header_frame = tk.Frame(main_frame, bg='#1a1a2e')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(header_frame, 
                              text="📞 PHONE CALL CHART CREATOR", 
                              font=('Arial', 28, 'bold'), 
                              bg='#1a1a2e', 
                              fg='#00d4ff')
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, 
                                 text="Speak to create charts - just like a phone call!", 
                                 font=('Arial', 14), 
                                 bg='#1a1a2e', 
                                 fg='#ffffff')
        subtitle_label.pack(pady=(5, 0))
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg='#1a1a2e')
        content_frame.pack(fill='both', expand=True)
        
        # Left panel - Conversation area
        left_panel = tk.Frame(content_frame, bg='#16213e', width=400)
        left_panel.pack(side='left', fill='y', padx=(0, 20))
        left_panel.pack_propagate(False)
        
        # Conversation title
        conv_title = tk.Label(left_panel, 
                             text="📞 CONVERSATION", 
                             font=('Arial', 16, 'bold'), 
                             bg='#16213e', 
                             fg='#00d4ff')
        conv_title.pack(pady=(20, 15))
        
        # Conversation display
        self.conversation_text = tk.Text(left_panel, 
                                        height=20, 
                                        width=45, 
                                        bg='#0f3460', 
                                        fg='#ffffff',
                                        font=('Arial', 11),
                                        wrap='word',
                                        state='disabled')
        self.conversation_text.pack(padx=20, pady=(0, 20))
        
        # Scrollbar for conversation
        conv_scrollbar = ttk.Scrollbar(left_panel, orient='vertical', command=self.conversation_text.yview)
        conv_scrollbar.pack(side='right', fill='y')
        self.conversation_text.configure(yscrollcommand=conv_scrollbar.set)
        
        # Voice control buttons
        voice_frame = tk.Frame(left_panel, bg='#16213e')
        voice_frame.pack(pady=(0, 20))
        
        self.mic_button = tk.Button(voice_frame, 
                                   text="🎤 START CONVERSATION", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#00d4ff',
                                   fg='#1a1a2e',
                                   command=self.toggle_listening,
                                   width=25,
                                   height=2)
        self.mic_button.pack()
        
        # Status display
        self.status_label = tk.Label(left_panel, 
                                    text="Ready to start conversation...", 
                                    font=('Arial', 12), 
                                    bg='#16213e', 
                                    fg='#00ff88')
        self.status_label.pack(pady=(10, 0))
        
        # Right panel - Chart display
        right_panel = tk.Frame(content_frame, bg='#16213e')
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Chart title
        chart_title = tk.Label(right_panel, 
                              text="📊 CHART DISPLAY", 
                              font=('Arial', 16, 'bold'), 
                              bg='#16213e', 
                              fg='#00d4ff')
        chart_title.pack(pady=(20, 15))
        
        # Chart area
        self.chart_frame = tk.Frame(right_panel, bg='#0f3460', height=500)
        self.chart_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Chart placeholder
        self.chart_placeholder = tk.Label(self.chart_frame, 
                                         text="🎯 Speak to create your first chart!\n\nSay: 'show me sales data' or 'create weather chart'", 
                                         font=('Arial', 16), 
                                         bg='#0f3460', 
                                         fg='#ffffff',
                                         justify='center')
        self.chart_placeholder.pack(expand=True)
        
        # Quick access buttons
        quick_frame = tk.Frame(right_panel, bg='#16213e')
        quick_frame.pack(pady=(0, 20))
        
        quick_label = tk.Label(quick_frame, 
                              text="Quick Access:", 
                              font=('Arial', 12, 'bold'), 
                              bg='#16213e', 
                              fg='#ffffff')
        quick_label.pack()
        
        buttons_frame = tk.Frame(quick_frame, bg='#16213e')
        buttons_frame.pack(pady=(10, 0))
        
        tk.Button(buttons_frame, text="💰 Sales", command=lambda: self.quick_create('sales'), 
                 bg='#FF6B6B', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="🌤️ Weather", command=lambda: self.quick_create('weather'), 
                 bg='#74B9FF', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="📚 Students", command=lambda: self.quick_create('students'), 
                 bg='#6C5CE7', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
    def add_to_conversation(self, speaker, message):
        """Add message to conversation display"""
        self.conversation_text.config(state='normal')
        timestamp = time.strftime("%H:%M:%S")
        
        if speaker == "System":
            self.conversation_text.insert('end', f"[{timestamp}] 🤖 {speaker}: {message}\n\n", 'system')
        else:
            self.conversation_text.insert('end', f"[{timestamp}] 👤 {speaker}: {message}\n\n", 'user')
        
        self.conversation_text.config(state='disabled')
        self.conversation_text.see('end')
        
        # Configure tags for different colors
        self.conversation_text.tag_config('system', foreground='#00d4ff')
        self.conversation_text.tag_config('user', foreground='#00ff88')
        
    def speak(self, text):
        """Speak the text and add to conversation"""
        self.add_to_conversation("System", text)
        self.engine.say(text)
        self.engine.runAndWait()
        
    def start_conversation(self):
        """Start the phone call conversation"""
        self.speak("Hello! Welcome to your personal chart assistant. I'm here to help you create beautiful charts. Just speak to me and I'll create charts for you!")
        
    def toggle_listening(self):
        """Toggle voice recognition on/off"""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
            
    def start_listening(self):
        """Start listening for voice input"""
        self.is_listening = True
        self.mic_button.config(text="🎤 STOP LISTENING", bg='#ff6b6b')
        self.status_label.config(text="Listening... Speak now!", fg='#00ff88')
        
        # Start listening in a separate thread
        threading.Thread(target=self.listen_loop, daemon=True).start()
        
    def stop_listening(self):
        """Stop listening for voice input"""
        self.is_listening = False
        self.mic_button.config(text="🎤 START CONVERSATION", bg='#00d4ff')
        self.status_label.config(text="Conversation stopped", fg='#ff6b6b')
        
    def listen_loop(self):
        """Main listening loop"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                    
                text = self.recognizer.recognize_google(audio)
                self.add_to_conversation("You", text)
                self.process_voice_command(text)
                
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                continue
            except Exception as e:
                print(f"Error: {e}")
                continue
                
    def process_voice_command(self, command):
        """Process voice commands"""
        command_lower = command.lower()
        
        # Check for dataset requests
        if any(word in command_lower for word in ['sales', 'revenue', 'money']):
            self.speak("Great! I found the sales dataset. I'll create a beautiful chart for you now.")
            self.create_chart('sales')
            
        elif any(word in command_lower for word in ['weather', 'temperature', 'climate']):
            self.speak("Perfect! I found the weather dataset. I'll create a beautiful chart for you now.")
            self.create_chart('weather')
            
        elif any(word in command_lower for word in ['student', 'performance', 'score', 'grade']):
            self.speak("Excellent! I found the student performance dataset. I'll create a beautiful chart for you now.")
            self.create_chart('students')
            
        # Check for chart type changes
        elif 'bar' in command_lower:
            self.speak("I'll change the chart to a beautiful bar chart.")
            self.current_chart_type = 'bar'
            if self.current_dataset:
                self.create_chart(self.current_dataset)
                
        elif 'line' in command_lower:
            self.speak("I'll change the chart to a beautiful line chart.")
            self.current_chart_type = 'line'
            if self.current_dataset:
                self.create_chart(self.current_dataset)
                
        elif 'pie' in command_lower:
            self.speak("I'll change the chart to a beautiful pie chart.")
            self.current_chart_type = 'pie'
            if self.current_dataset:
                self.create_chart(self.current_dataset)
                
        else:
            self.speak("I'm not sure what you want. Please say 'sales', 'weather', or 'students' to create a chart.")
            
    def quick_create(self, dataset):
        """Quick create chart from button click"""
        self.speak(f"I'll create a beautiful chart for the {dataset} dataset.")
        self.create_chart(dataset)
        
    def create_chart(self, dataset_name):
        """Create and display a beautiful chart"""
        if dataset_name not in self.SAMPLE_DATASETS:
            self.speak(f"Sorry, I couldn't find the {dataset_name} dataset.")
            return
            
        self.current_dataset = dataset_name
        dataset = self.SAMPLE_DATASETS[dataset_name]
        data = dataset['data']
        colors = dataset['colors']
        
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#0f3460')
        ax.set_facecolor('#0f3460')
        
        categories = list(data.keys())
        values = list(data.values())
        
        if self.current_chart_type == "bar":
            bars = ax.bar(categories, values, color=colors, edgecolor='white', linewidth=2)
            
            # Add value labels
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                       f'{value}', ha='center', va='bottom', fontsize=12, fontweight='bold', color='white')
                       
        elif self.current_chart_type == "line":
            ax.plot(categories, values, marker='o', linewidth=4, markersize=10, 
                   color='#00d4ff', markerfacecolor='#00ff88', markeredgecolor='white', markeredgewidth=2)
            
            # Add value labels
            for x, y in zip(categories, values):
                ax.annotate(f'{y}', (x, y), textcoords="offset points", xytext=(0,10), 
                           ha='center', fontsize=12, fontweight='bold', color='white')
                           
        elif self.current_chart_type == "pie":
            wedges, texts, autotexts = ax.pie(values, labels=categories, colors=colors, 
                                              autopct='%1.1f%%', startangle=90,
                                              wedgeprops={'edgecolor': 'white', 'linewidth': 2})
            
            # Make percentage text white and bold
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                
        # Styling
        ax.set_title(f'📊 {dataset_name.title()} Data Chart', fontsize=20, fontweight='bold', 
                     color='#00d4ff', pad=20)
        
        if self.current_chart_type != "pie":
            ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5, color='white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#00d4ff')
            ax.spines['bottom'].set_color('#00d4ff')
            
            # Set colors for labels
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            
            # Rotate x-axis labels
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
        # Add dataset description
        fig.text(0.5, 0.02, dataset['description'], ha='center', fontsize=12, 
                 style='italic', color='#00ff88')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Success message
        self.speak(f"I've successfully created a {self.current_chart_type} chart showing {dataset['description']}. The chart is now displayed on your screen!")
        
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main function"""
    try:
        app = PhoneCallChartApp()
        app.run()
    except Exception as e:
        print(f"Error starting app: {e}")
        print("Please make sure you have the required packages installed:")
        print("pip install tkinter matplotlib speech_recognition pyttsx3 pyaudio pillow")

if __name__ == "__main__":
    main()