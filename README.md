# Sephira Orion - Sentiment Analysis RAG System

Sephira Orion is an advanced RAG (Retrieval-Augmented Generation) system that provides intelligent analysis of sentiment data across 32 countries from 1970 to 2025. It combines historical sentiment analysis with predictive capabilities and integrates multiple external data sources.

## Features

- **Intelligent Q&A**: Ask questions about historical sentiment data with natural language
- **Predictive Analytics**: 
  - Time series forecasting (30/60/90 day predictions)
  - Trend analysis and pattern detection
  - Cross-country correlation analysis
  - Anomaly detection
- **Multi-Source Integration**: 
  - Financial market data
  - News sentiment
  - Economic indicators
- **Security-First Design**:
  - Prompt injection protection
  - Bulk data extraction prevention
  - Rate limiting and audit logging
- **Interactive Dashboard**: Beautiful Streamlit interface with visualizations

## Architecture

```
Backend (FastAPI) → RAG Engine (ChromaDB + GPT-4o) → Predictions (Prophet/ML)
                  ↓
Frontend (Streamlit) + REST API
```

## Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key
- (Optional) API keys for NewsAPI, Alpha Vantage, FRED

### Installation

1. Clone the repository:
```bash
cd sephira4
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Place your sentiment data:
```bash
cp /path/to/all_indexes_beta.csv data/raw/
```

5. Initialize the system (load data and create embeddings):
```bash
python -m backend.services.data_loader
```

### Running the Application

#### Start the FastAPI backend:
```bash
uvicorn backend.api.main:app --reload --port 8000
```

#### Start the Streamlit frontend:
```bash
streamlit run frontend/app.py
```

Access the application at `http://localhost:8501`

API documentation available at `http://localhost:8000/docs`

## API Endpoints

- `POST /api/chat` - Chat with Sephira
- `POST /api/predict/forecast` - Get sentiment forecasts
- `POST /api/predict/trends` - Analyze trends
- `POST /api/predict/correlations` - Cross-country correlations
- `POST /api/predict/anomalies` - Detect anomalies
- `GET /api/data/countries` - List available countries
- `GET /api/data/date-range` - Get data coverage

## Project Structure

```
sephira4/
├── backend/
│   ├── api/          # FastAPI routes
│   ├── core/         # Core functionality (RAG, security)
│   ├── models/       # Data models and predictors
│   ├── services/     # Business logic
│   └── utils/        # Utilities
├── frontend/
│   └── app.py        # Streamlit dashboard
├── data/
│   ├── raw/          # Original CSV data
│   └── processed/    # Processed data
└── tests/            # Test suite
```

## Security Features

- **Prompt Injection Detection**: Pattern matching and semantic analysis
- **Rate Limiting**: Configurable per-user/per-IP limits
- **Audit Logging**: All queries logged for security review
- **Response Filtering**: Prevents system prompt exposure
- **Bulk Extraction Prevention**: Detects and blocks systematic data extraction

## Development

### Running Tests
```bash
pytest tests/
```

### Linting
```bash
black backend/ frontend/ tests/
flake8 backend/ frontend/ tests/
```

## Technologies Used

- **Backend**: FastAPI, Python 3.10+
- **LLM**: OpenAI GPT-4o
- **Vector DB**: ChromaDB
- **ML/Forecasting**: Prophet, scikit-learn, statsmodels
- **Frontend**: Streamlit
- **Visualization**: Plotly, Matplotlib, Seaborn

## Configuration

Key configuration options in `.env`:

- `MAX_QUERIES_PER_MINUTE`: Rate limit for queries
- `MAX_RESPONSE_TOKENS`: Maximum tokens in LLM responses
- `CHROMADB_PATH`: Vector database storage location

## License

MIT License

## Support

For issues and questions, please open a GitHub issue.
