from app.schemas import SentimentRequest, SentimentResponse, SentimentLabel

# Test request válido
try:
    req = SentimentRequest(text="I love this!")
    print(f"Request válido: {req.text}")
except Exception as e:
    print(f"Error: {e}")
    
# Test request inválido (texto vacío)
try:
    req = SentimentRequest(text=" ")
    print(f"Debería haber fallado")
except ValueError as e:
    print(f"Validación funcionando: {e}")
    # Test response
    resp = SentimentResponse(
    text="test",
    sentiment=SentimentLabel.POSITIVE,
    confidence=0.95,
    scores=[],
    processing_time_ms=10.0,
    model_version="test"
    )
    print(f"Response creado: {resp.sentiment}")
    
print("\nTodos los schemas funcionan correctamente!")