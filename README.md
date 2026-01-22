# Intelligent Data Visualization

An intelligent web application that generates automated data visualizations based on user problems and datasets using Groq AI.

## Features

- Upload CSV files
- Input textual problems
- AI-powered generation of 3 visualization proposals
- Interactive visualizations with Plotly
- Export to PNG

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-team/intelligent-data-viz.git
   cd intelligent-data-viz
   ```

2. Create virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Usage

Run the application:
```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

## Architecture

- `src/llm/`: LLM integration and prompt engineering
- `src/data/`: Data processing and profiling
- `src/visualization/`: Visualization generation
- `src/ui/`: User interface components
- `src/config/`: Configuration management
- `src/utils/`: Utilities (logging, exceptions)

## Testing

Run tests:
```bash
pytest
```

## Deployment

Deployed on Hugging Face Spaces: [Link here]

## Team

- Person 1: LLM & Data Processing
- Person 2: Visualization & Frontend
- Person 3: Infrastructure & Quality

## License

MIT