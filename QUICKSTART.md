# Sephira Orion - Quick Start Guide

## Prerequisites

- Python 3.10 or higher
- OpenAI API key (required)
- API keys for NewsAPI, Alpha Vantage, FRED (optional)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configuration

Copy the sentiment data CSV:
```bash
cp /path/to/all_indexes_beta.csv data/raw/
```

Create and configure `.env` file:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run Setup

```bash
python setup.py
```

This will:
- Create necessary directories
- Process the sentiment data
- Generate embeddings (requires OpenAI API key)
- Set up the vector database

**Note**: Embedding generation may take 10-15 minutes and will make API calls to OpenAI.

## Running the Application

### Option 1: Automated Setup (Recommended)

Run the setup script which will guide you through all steps:
```bash
python setup.py
```

### Option 2: Manual Setup

1. **Process Data**:
```bash
python -m backend.services.data_loader
```

2. **Generate Embeddings**:
```bash
python -m backend.services.embeddings
```

3. **Start Backend** (Terminal 1):
```bash
uvicorn backend.api.main:app --reload --port 8000
```

4. **Start Frontend** (Terminal 2):
```bash
streamlit run frontend/app.py
```

## Access Points

- **Frontend Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/api/health

## Features

### 1. Chat Interface
Ask questions about sentiment data:
- "What was the sentiment in the United States in 2020?"
- "Compare sentiment trends between Germany and France"
- "When did UK sentiment peak?"

### 2. Forecasting
Generate future sentiment predictions:
- Select a country
- Choose forecast horizon (7-90 days)
- View predictions with confidence intervals

### 3. Trend Analysis
Analyze sentiment patterns:
- Moving averages
- Momentum indicators
- Trend strength and direction
- Turning points

### 4. Correlation Analysis
Discover relationships between countries:
- Pearson or Spearman correlation
- Heatmap visualization
- Significant correlation pairs

### 5. Anomaly Detection
Identify unusual patterns:
- Statistical outliers
- ML-based anomaly detection
- Severity classification

## API Usage

### Chat Endpoint
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What was the sentiment in 2020?",
    "countries": ["United States"],
    "start_date": "2020-01-01",
    "end_date": "2020-12-31"
  }'
```

### Forecast Endpoint
```bash
curl -X POST "http://localhost:8000/api/predict/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "country": "United States",
    "days": 30,
    "confidence_level": 0.95
  }'
```

### List Countries
```bash
curl "http://localhost:8000/api/data/countries"
```

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run specific test modules:
```bash
pytest tests/test_security.py -v
pytest tests/test_rag.py -v
pytest tests/test_predictions.py -v
```

## Troubleshooting

### Backend won't start
- Check that port 8000 is not in use
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check logs in `logs/` directory

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check `API_BASE_URL` in `frontend/app.py`

### Embeddings generation fails
- Verify `OPENAI_API_KEY` in `.env` is correct
- Check OpenAI API rate limits
- Ensure you have sufficient API credits

### "Collection not found" error
- Run embeddings generation: `python -m backend.services.embeddings`
- Check ChromaDB path in `.env`

### Out of memory during embedding generation
- Reduce batch size in `backend/services/embeddings.py`
- Process data in smaller chunks

## Security Features

Sephira includes built-in security:

✅ **Prompt Injection Protection**
- Pattern matching for common injection attempts
- Semantic analysis of queries

✅ **Bulk Extraction Prevention**
- Rate limiting (configurable)
- Query pattern analysis
- Response size limits

✅ **Audit Logging**
- All queries logged
- Security violations tracked

## Performance Tips

1. **Caching**: Enable Redis for query caching (optional)
2. **Batch Processing**: Process multiple predictions in parallel
3. **Index Optimization**: ChromaDB automatically optimizes indices
4. **API Keys**: Use separate API keys for development and production

## Next Steps

- Explore the Streamlit interface
- Try different types of queries
- Experiment with forecasting parameters
- Review API documentation at `/docs`
- Integrate external APIs (News, Financial data)

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review API documentation at http://localhost:8000/docs
3. See README.md for detailed information

---

**Happy Analyzing! 📊**
