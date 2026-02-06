# Sentiment API

REST API for sentiment analysis using Machine Learning.

## Tech Stack

- **FastAPI** - Web framework
- **Transformers** - ML models (HuggingFace)
- **Docker** - Containerization
- **pytest** - Testing

## Status

🚧 Under development

## Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/sentiment-api.git
cd sentiment-api

# Setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/sentiment/analyze` | Analyze text sentiment |

## License

MIT
