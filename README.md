# Sentiment API

REST API for sentiment analysis. Send it English text, get back positive/negative with a confidence score. Built with FastAPI and a HuggingFace transformer model.

## What it does

POST a text to `/api/v1/sentiment/analyze` and it returns a sentiment label, a confidence score, and the full score breakdown. There's also a batch endpoint for up to 100 texts in one call, and three health endpoints for basic liveness, detailed component status, and readiness (whether the model finished loading).

## Try it

```bash
curl -X POST "http://localhost:8000/api/v1/sentiment/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product! It is amazing."}'
```

```json
{
  "text": "I love this product! It is amazing.",
  "sentiment": "positive",
  "confidence": 0.9999,
  "scores": [
    {"label": "positive", "score": 0.9999},
    {"label": "negative", "score": 0.0001}
  ],
  "processing_time_ms": 1477.56,
  "model_version": "distilbert-base-uncased-finetuned-sst-2-english",
  "timestamp": "2026-09-23T13:46:55.620091Z"
}
```

That request was the first one after startup, which is why processing took 1.4s. Once the model is warm, the same request runs in 30-50ms on CPU.

Interactive docs (Swagger) are at `/api/v1/docs` once the server is running.

## Model

The model is `distilbert-base-uncased-finetuned-sst-2-english`, pulled from HuggingFace as-is. It's not fine-tuned or trained on anything of mine — it comes pretrained for binary sentiment (positive/negative) on the SST-2 dataset. My part is the API around it: request validation, text preprocessing (stripping URLs, emails, @mentions before the text hits the model), the batch endpoint, health checks, error handling, and the Docker packaging.

Because the model is binary, "neutral" is a label the code can return but the model itself will basically never produce — the schema and the API support three classes, but in practice you'll only see positive or negative.

## Tests

25 tests, 85% coverage, all passing against the pinned dependency versions in `requirements.txt`. Coverage is measured with `pytest --cov=app`, not eyeballed.

What's actually covered: text preprocessing (URL/email/mention stripping, truncation, lowercasing), the prediction pipeline end to end, and the API layer (valid requests, empty text, missing fields, batch counts). The weakest spots are the exception handlers and the model-load failure path — those are written but not exercised by a test that forces a load failure.

## Limits

- **Language**: only tested against English. I ran a Spanish sentence through it during this review and it happened to classify correctly, but that's not something to rely on — the model wasn't trained for Spanish, and there's no language detection or rejection in the code. There's no `language` parameter in the request — I pulled it out rather than keep a field that didn't do anything.
- **Text length**: hard cap at 5000 characters, enforced by Pydantic — anything longer gets a 422 before it reaches the model. Internally there's also a 512-character truncation in the preprocessor, so very long inputs get cut down further before inference; I haven't checked how that interacts with texts that are meaningful past character 512.
- **Weird input**: empty or whitespace-only text returns 422 with a clear message. I haven't tried emoji-only text, non-Latin scripts, or adversarial inputs — no data on how the model handles those.
- **Batch endpoint**: caps at 100 texts per call, and it's a plain loop over the single-text path — no batching at the model level, so 100 texts take roughly 100x as long as one.

## Running it

```bash
docker-compose up --build
```

or without Docker:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Dev setup (linting, tests): `pip install -r requirements-dev.txt`, then `make test` or `make lint`.

## Stack

FastAPI, HuggingFace Transformers (PyTorch backend, CPU inference), Pydantic v2, Docker (multi-stage build), pytest, GitHub Actions for lint/test/build on push.

## License

MIT
