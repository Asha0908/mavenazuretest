# 🗣️ Voice Enabled Chart Creation Tool

Meet **Faboo** - your friendly voice-enabled chart-making assistant! This application allows you to create beautiful charts through natural voice conversation.

## ✨ Features

- **Voice Recognition**: Speak naturally to create charts
- **Multiple Chart Types**: Bar, Line, Pie, Donut, Scatter, Histogram, Waterfall, Area, Radar, and Heatmap charts
- **Smart Data Generation**: Automatically generates relevant data based on your requests
- **Custom Data Upload**: Upload your own CSV/Excel files
- **Context Awareness**: Uses previous conversation context for follow-up requests
- **Text-to-Speech**: Faboo responds with voice feedback
- **Beautiful UI**: Modern, intuitive interface

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Microphone for voice input
- Speakers/headphones for voice output

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python voice_chart_app.py
   ```

## 🎯 How to Use

### Starting a Conversation

1. Click **"🎤 START CHATTING"** to begin
2. Faboo will greet you and start listening
3. Speak naturally about what chart you want to create

### Example Voice Commands

**Basic Chart Creation:**
- "Create a pie chart"
- "Make a bar chart for sales data"
- "Show me a line chart for weather data"

**Using Context:**
- "Use same dataset, create bar chart"
- "Make it blue"
- "Change to pie chart"

**Data Upload:**
- "Upload my data"
- "Use my CSV file"

**Getting Help:**
- "What charts can you create?"
- "What attributes does this dataset have?"
- "Explain the chart"

### Chart Types Available

- **Bar Charts**: For comparing categories
- **Line Charts**: For showing trends over time
- **Pie Charts**: For showing proportions
- **Donut Charts**: Similar to pie charts with hollow center
- **Scatter Plots**: For showing relationships
- **Histograms**: For showing distributions
- **Waterfall Charts**: For showing cumulative changes
- **Area Charts**: For showing trends with filled areas
- **Radar Charts**: For multi-dimensional data
- **Heatmaps**: For showing patterns in data

### Supported Datasets

The app can generate data for various topics:
- **Sales/Revenue**: Monthly sales data
- **Weather**: Temperature and climate data
- **Student Performance**: Grades and scores
- **Iris Dataset**: Classic flower classification data
- **Transportation**: Train and passenger data
- **Custom Data**: Upload your own CSV/Excel files

## 🎨 Features in Detail

### Voice Recognition
- Uses Google Speech Recognition API
- Handles natural language processing
- Supports various accents and speaking styles

### Smart Context Handling
- Remembers previous chart and dataset
- Allows follow-up requests like "use same data"
- Maintains conversation flow

### Data Generation
- Automatically creates relevant sample data
- Supports multiple data types and formats
- Adapts data based on requested chart type

### Custom Data Upload
- Supports CSV and Excel files
- Automatically processes uploaded data
- Provides data summary and attributes

## 🔧 Troubleshooting

### Common Issues

**No Microphone Found:**
- Ensure your microphone is connected and working
- Check system audio settings
- Restart the application

**Speech Recognition Issues:**
- Speak clearly and at moderate pace
- Reduce background noise
- Check internet connection (Google Speech API requires internet)

**Chart Display Issues:**
- Ensure matplotlib is properly installed
- Check that all dependencies are installed correctly

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.7 or higher
- **Memory**: At least 4GB RAM recommended
- **Storage**: 100MB free space

## 🎪 Example Conversation

```
You: "Hi Faboo!"
Faboo: "Hi! I'm Faboo, your friendly chart-making buddy! How are you doing today?"

You: "Create a pie chart for sales data"
Faboo: "Great! I'll use sales data. What type of chart would you like?"

You: "Pie chart"
Faboo: "Perfect! A pie chart for sales data. What should be the X axis?"

You: "Month"
Faboo: "Great! X axis will be Month. What should be the Y axis?"

You: "Revenue"
Faboo: "Perfect! Y axis will be Revenue. What color would you like?"

You: "Blue"
Faboo: "Sure! Here we go! Creating your chart!"

[Chart appears]

You: "Use same dataset, create bar chart"
Faboo: "Done! I'll create a bar chart with the same sales data!"

[New chart appears]
```

## 🤝 Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Improving the voice recognition accuracy
- Adding new chart types
- Enhancing the UI

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with Python, Tkinter, and Matplotlib
- Uses Google Speech Recognition API
- Inspired by the need for accessible data visualization tools

---

**Happy Charting with Faboo! 🎉**