# Intelligent Data Visualization

An intelligent web application that generates automated data visualizations based on user problems and datasets using Groq AI.

## 🌟 Features

- 📤 Upload CSV files (up to 10MB)
- 💭 Input textual problems/questions about your data
- 🤖 AI-powered generation of 3 visualization proposals
- 📊 Interactive visualizations with Plotly (6 types: scatter, bar, line, histogram, box, heatmap)
- 💾 Export to PNG in high quality
- 🎨 Professional styling with best practices
- ⚡ Caching for faster responses

## 🚀 Quick Start

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Rblaze23/intelligent-data-viz.git
   cd intelligent-data-viz
   ```

2. Create virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Create .env file and add your Groq API key
   echo "GROQ_API_KEY=your_api_key_here" > .env
   ```

### Usage

Run the application locally:
```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

### Example Datasets

Try the app with our sample datasets in `examples/`:
- `housing_prices.csv` - Real estate price analysis
- `sales_data.csv` - Product sales trends
- `student_performance.csv` - Educational performance analysis

## 📖 How It Works

1. **Upload Data**: Upload your CSV file containing the data you want to analyze
2. **Describe Problem**: Enter your question or analysis goal in natural language
3. **Get Recommendations**: The AI analyzes your data and suggests 3 optimal visualizations
4. **View Results**: Explore interactive charts with justifications and best practices
5. **Export**: Download your chosen visualization as a high-quality PNG

## 🏗️ Architecture

```
intelligent-data-viz/
├── src/
│   ├── llm/              # LLM integration (Groq API)
│   ├── data/             # Data processing and validation
│   ├── visualization/    # Chart generation with Plotly
│   ├── ui/               # Streamlit UI components
│   ├── config/           # Configuration management
│   └── utils/            # Utilities (logging, exceptions)
├── tests/
│   ├── unit/             # Unit tests (49 tests)
│   └── integration/      # Integration tests
├── examples/             # Sample datasets
└── docs/                 # Documentation

```

## 🧪 Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

Run integration tests (requires GROQ_API_KEY):
```bash
pytest tests/integration/
```

## 🛠️ Development

### Pre-commit Hooks

We use pre-commit hooks for code quality:
```bash
pip install pre-commit
pre-commit install
```

### Code Quality

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing (96% pass rate)

## 📊 Supported Visualizations

1. **Scatter Plot** - Relationships between two variables
2. **Bar Chart** - Categorical comparisons
3. **Line Chart** - Trends over time
4. **Histogram** - Distribution analysis
5. **Box Plot** - Statistical summaries and outliers
6. **Heatmap** - Correlation matrices

## 🌐 Deployment

**Live Demo**: [Coming Soon - Hugging Face Spaces]

The app is deployed on Hugging Face Spaces with automatic deployment from the main branch.

## 👥 Team

- **Ramy Lazgheb**: LLM & Data Processing Lead
- **Chiheb Guesmi**: Visualization & Frontend Lead
- **Mohamed Yassine Madhi**: Infrastructure & Quality Lead

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [Prompt Engineering Guide](docs/prompt_engineering_guide.md)
- [LLM Integration](src/llm/ReadmeLLM.md)
- [Data Processing](src/data/Readmedata.md)

## 🙏 Acknowledgments

- Groq for lightning-fast LLM inference
- Streamlit for the web framework
- Plotly for interactive visualizations
- OpenSource community

---

**Master 2 BDIA - Data Visualization Project**  
**Deadline**: February 7, 2026
