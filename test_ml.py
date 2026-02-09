
from app.core import setup_logging
from app.ml import sentiment_model, sentiment_pipeline
from app.schemas import SentimentRequest

# Setup
setup_logging()
print("Cargando modelo (puede tardar la primera vez)...")
sentiment_model.load()
print(f"✅ Modelo cargado: {sentiment_model.model_name}")

# Probar predicción directa
print("\n--- Test predicción directa ---")
result = sentiment_model.predict("I love this product!")
print(f"Sentiment: {result['sentiment']}")
print(f"Confidence: {result['confidence']:.2f}")

# Probar pipeline completo
print("\n--- Test pipeline completo ---")
request = SentimentRequest(text="This movie was terrible and boring.")
response = sentiment_pipeline.analyze(request)
print(f"Text: {response.text}")
print(f"Sentiment: {response.sentiment}")
print(f"Confidence: {response.confidence:.2f}")
print(f"Processing time: {response.processing_time_ms:.1f}ms")
print("\n✅ Pipeline funcionando correctamente!")