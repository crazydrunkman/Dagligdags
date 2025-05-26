import os
from pathlib import Path
from typing import Literal

class Config:
    """Centralized configuration with environment-aware settings."""
    
    # Environment (dev/staging/prod)
    ENV: Literal['dev', 'staging', 'prod'] = os.getenv('DAGLIGDAGS_ENV', 'dev')
    
    # Security & SSL
    VERIFY_SSL: bool = os.getenv('VERIFY_SSL', str(ENV == 'prod')).lower() == 'true'
    SSL_CERT_PATH: Path = Path(os.getenv('SSL_CERT_PATH', '/etc/ssl/certs/ca-certificates.crt'))
    
    # Norwegian localization
    DEFAULT_LOCALE: str = 'nb-NO'
    CURRENCY: str = 'NOK'
    DECIMAL_SEPARATOR: str = ','  # Norwegian number format
    
    # API Limits (aligned with Norwegian store policies)
    REQUESTS_PER_MINUTE: int = 60
    MAX_RETRIES: int = 3

    @classmethod
    def get_store_url(cls, store_name: str) -> str:
        """Get configured URL for Norwegian grocery chains."""
        return cls.STORE_URLS.get(store_name.lower(), '')
    
    # Norwegian grocery store URLs
    STORE_URLS: dict = {
        'coop': 'https://coop.no/uke-tilbud/',
        'rema': 'https://www.rema.no/aktuelt/aktuelle-tilbud/',
        'kiwi': 'https://kiwi.no/webutils/tilbudsavis/',
        'meny': 'https://meny.no/tilbud/',
        'oda': 'https://oda.com/api/v1/products'
    }
    
    # Food databases
    FOOD_DATABASES: dict = {
        'matvaretabellen': 'https://www.matvaretabellen.no/api/v2/foods',
        'usda': 'https://api.nal.usda.gov/fdc/v1/foods/list'
    }
