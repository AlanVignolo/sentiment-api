"""
Preprocesamiento de texto para el modelo.
Limpia el texto antes de mandarlo al modelo de ML (quita URLs, emails, etc).
"""

import re  # modulo de Python para expresiones regulares (patrones de texto)
from typing import List, Optional

from app.core import get_logger

logger = get_logger(__name__)


class TextPreprocessor:
    """Preprocesador de texto para analisis de sentimientos."""

    # Patrones de regex compilados (se compilan una sola vez, no en cada llamada)
    # Cada uno detecta un tipo de "basura" que no aporta al analisis de sentimiento
    URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")  # detecta URLs
    EMAIL_PATTERN = re.compile(r"\S+@\S+")  # detecta emails
    MENTION_PATTERN = re.compile(r"@\w+")  # detecta @usuario
    HASHTAG_PATTERN = re.compile(r"#\w+")  # detecta #hashtag
    MULTIPLE_SPACES = re.compile(r"\s+")  # detecta espacios repetidos

    def __init__(
        self,
        lowercase: bool = False,
        remove_urls: bool = True,
        remove_emails: bool = True,
        remove_mentions: bool = True,
        remove_hashtags: bool = False,  # False por defecto porque el hashtag puede tener sentimiento
        max_length: Optional[int] = 512,  # 512 = limite tipico de tokens para modelos BERT
    ):
        # Guarda las opciones como atributos para usarlas en preprocess()
        self.lowercase = lowercase
        self.remove_urls = remove_urls
        self.remove_emails = remove_emails
        self.remove_mentions = remove_mentions
        self.remove_hashtags = remove_hashtags
        self.max_length = max_length

        logger.info(
            f"TextPreprocessor inicializado: " f"lowercase={lowercase}, max_length={max_length}"
        )

    def preprocess(self, text: str) -> str:
        """Limpia un texto aplicando las transformaciones configuradas."""

        if not text:
            return ""

        original_length = len(text)

        # Cada .sub() busca el patron y lo reemplaza por un espacio
        if self.remove_urls:
            text = self.URL_PATTERN.sub(" ", text)  # "mira https://x.com genial" → "mira  genial"

        if self.remove_emails:
            text = self.EMAIL_PATTERN.sub(" ", text)

        if self.remove_mentions:
            text = self.MENTION_PATTERN.sub(" ", text)  # "hola @juan que tal" → "hola  que tal"

        if self.remove_hashtags:
            text = self.HASHTAG_PATTERN.sub(" ", text)

        if self.lowercase:
            text = text.lower()  # "GENIAL" → "genial"

        # Limpia los espacios dobles que quedaron de las sustituciones
        text = self.MULTIPLE_SPACES.sub(" ", text)  # "hola   que  tal" → "hola que tal"
        text = text.strip()

        # Si el texto es mas largo que el limite, lo corta
        if self.max_length and len(text) > self.max_length:
            text = text[: self.max_length]
            logger.debug(f"Texto truncado de {original_length} a {self.max_length}")

        return text

    def preprocess_batch(self, texts: List[str]) -> List[str]:
        """Preprocesa multiples textos de una vez."""
        # List comprehension: aplica preprocess() a cada texto de la lista
        return [self.preprocess(text) for text in texts]
