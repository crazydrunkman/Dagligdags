from .environment import Config
from .paths import Paths
from datetime import timedelta

class Constants:
    """Norwegian-market constants and thresholds."""
    
    # Price comparison
    PRICE_THRESHOLDS_NOK: dict = {
        'cheap': 25.0,
        'moderate': 50.0,
        'expensive': 100.0
    }
    
    # Travel cost calculations (NOK per km)
    TRANSPORT_COSTS: dict = {
        'walking': 0.0,
        'cycling': 0.15,
        'driving': 0.82,  # Based on Norwegian fuel prices
        'public_transport': 12.50  # Average Oslo metro fare
    }
    
    # Food categories (Norwegian taxonomy)
    FOOD_CATEGORIES: list = [
        "meieri",
        "kjøtt",
        "fisk",
        "grønnsaker",
        "kornvarer",
        "tørrvarer"
    ]
    
    # Sustainability metrics (CO₂ equivalents)
    CARBON_INTENSITY: dict = {
        'local': 0.5,  # kg CO₂/kg for Norwegian-produced
        'imported': 2.3  # EU average
    }
    
    # Data retention
    DATA_RETENTION: dict = {
        'user_profiles': timedelta(days=730),  # 2 years (GDPR compliance)
        'scraped_data': timedelta(days=7),
        'logs': timedelta(days=30)
    }
    
    # API configuration
    API_TIMEOUT: int = 15  # seconds
    RATE_LIMITS: dict = {
        'coop': 60,  # requests/minute
        'rema': 30
    }
