# Architecture Overview

## Project Structure

```
intelligent-data-viz/
├── src/
│   ├── config/          # Configuration management
│   ├── utils/           # Utilities (logging, exceptions)
│   ├── llm/             # LLM integration 
│   ├── data/            # Data processing 
│   ├── visualization/   # Visualization generation 
│   └── ui/              # User interface 
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── docs/                # Documentation
├── examples/            # Example datasets
└── .github/workflows/   # CI/CD pipelines
```

## Components

### LLM Module
- `client.py`: API client for Groq
- `prompts.py`: Prompt templates
- `analyzer.py`: Main analysis logic

### Data Module
- `processor.py`: CSV processing
- `profiler.py`: Data profiling
- `validator.py`: Data validation

### Visualization Module
- `generator.py`: Chart generation
- `styler.py`: Styling
- `exporter.py`: Export to PNG/HTML

### UI Module
- `components.py`: Reusable UI components

### Config Module
- `settings.py`: Environment and constants

### Utils Module
- `logger.py`: Logging setup
- `exceptions.py`: Custom exceptions

## Data Flow

1. User uploads CSV
2. Data processor validates and profiles
3. LLM analyzer generates 3 visualization proposals
4. User selects one
5. Visualization generator creates chart
6. Exporter saves to PNG

## Dependencies

- Streamlit: Web framework
- Plotly: Visualization
- Groq: LLM API
- Pandas: Data manipulation
- Pytest: Testing
