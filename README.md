# 🎤 Voice-Enabled Chart Creator

A real-time, interactive chart creation application that responds to voice commands! Create beautiful charts using just your voice or traditional controls.

## ✨ Features

- **🎤 Voice Recognition**: Speak to create charts naturally
- **📊 Real-time Chart Generation**: Instant chart creation with Plotly
- **📁 Dataset Management**: Pre-loaded sample datasets + upload your own
- **🎨 Multiple Chart Types**: Bar, Line, Scatter, Pie, Histogram
- **🎯 Interactive UI**: Beautiful, responsive design with smooth animations
- **🔧 Customization**: Colors, titles, and chart options
- **📱 Mobile Friendly**: Works on all devices

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open Your Browser
Navigate to `http://localhost:5000`

## 🎯 How to Use

### Voice Commands
- **"Show me the sales dataset"** - Load sales data
- **"Create a bar chart"** - Set chart type to bar
- **"Use temperature and humidity"** - Set X and Y axes
- **"Add colors by region"** - Add color coding
- **"Title it Monthly Sales"** - Set chart title

### Manual Controls
1. **Select Dataset**: Choose from available datasets or upload your own
2. **Choose Chart Type**: Pick from 5 chart types
3. **Configure Axes**: Select X and Y axis columns
4. **Customize**: Add colors, titles, and styling
5. **Generate**: Click to create your chart!

## 📊 Sample Datasets

### Sales Data
- Monthly sales for different products across regions
- Columns: Month, Product, Sales, Region

### Weather Data
- Daily temperature and humidity by city
- Columns: Date, Temperature, Humidity, City

### Student Performance
- Student scores in different subjects
- Columns: Student, Math, Science, English, Grade

## 🔧 Technical Details

### Backend
- **Flask**: Web framework for API endpoints
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive chart generation
- **Speech Recognition**: Voice command processing

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients and animations
- **JavaScript**: Voice recognition and chart interaction
- **Plotly.js**: Chart rendering and interaction

### API Endpoints
- `GET /api/datasets` - List available datasets
- `GET /api/dataset/<id>` - Get specific dataset
- `POST /api/upload` - Upload new dataset
- `POST /api/chart` - Generate chart
- `POST /api/voice-command` - Process voice commands

## 🎨 Chart Types Supported

1. **Bar Charts**: Perfect for comparing categories
2. **Line Charts**: Great for trends over time
3. **Scatter Plots**: Show relationships between variables
4. **Pie Charts**: Display proportions and percentages
5. **Histograms**: Show data distribution

## 📁 File Structure
```
voice-chart-creator/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   └── index.html     # Main interface
├── uploads/           # User uploaded datasets
├── datasets/          # Sample datasets
└── README.md          # This file
```

## 🌟 Voice Command Examples

### Dataset Selection
- "Show me the weather data"
- "Load student performance dataset"
- "Use sales information"

### Chart Creation
- "Create a bar chart"
- "Make a line graph"
- "Show me a pie chart"
- "Generate scatter plot"

### Customization
- "Use month for X axis"
- "Set sales as Y axis"
- "Color by region"
- "Title it Sales Overview"

## 🔒 Browser Compatibility

- **Chrome**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support

## 🚨 Troubleshooting

### Voice Recognition Issues
- Ensure microphone permissions are granted
- Use Chrome for best compatibility
- Check if microphone is working in other apps

### Chart Generation Errors
- Verify dataset columns exist
- Check data types (numeric for Y-axis)
- Ensure required fields are filled

### Upload Issues
- Supported formats: CSV, Excel (.xlsx, .xls)
- Check file size (max 10MB recommended)
- Verify file format and structure

## 🎉 Project Highlights

This project demonstrates:
- **Real-time voice interaction** with web applications
- **Modern web development** with Flask and JavaScript
- **Data visualization** using Plotly
- **Responsive design** principles
- **API-first architecture**
- **User experience** optimization

## 🤝 Contributing

Feel free to enhance this project with:
- Additional chart types
- More voice commands
- Enhanced data processing
- Better UI/UX
- Performance optimizations

## 📄 License

This project is open source and available under the MIT License.

---

**Happy Charting! 🎤📊✨**