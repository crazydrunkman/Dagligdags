from pathlib import Path
import os

class Paths:
    """Norwegian-centric path configuration with automatic directory creation."""
    
    # Base directories
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = PROJECT_ROOT / 'data'
    
    # Scraping artifacts
    SCRAPER_STORAGE: Path = DATA_DIR / 'scraped_data'
    PDF_STORAGE: Path = SCRAPER_STORAGE / 'pdfs'
    HTML_CACHE: Path = SCRAPER_STORAGE / 'html'
    
    # Processed data
    NORMALIZED_DATA: Path = DATA_DIR / 'normalized'
    USER_PROFILES: Path = DATA_DIR / 'users'
    
    # System paths
    LOG_DIR: Path = PROJECT_ROOT / 'logs'
    TEMP_DIR: Path = Path(os.getenv('TMPDIR', '/tmp')) / 'dagligdags'
    
    # Create directories on import
    for dir in [SCRAPER_STORAGE, PDF_STORAGE, HTML_CACHE, 
                NORMALIZED_DATA, USER_PROFILES, LOG_DIR, TEMP_DIR]:
        dir.mkdir(parents=True, exist_ok=True)


# File paths
USER_PROFILE_TEMPLATE = USER_PROFILES_DIR / "user_{user_id}.json"
DEALS_DATABASE = NORMALIZED_DATA_DIR / "deals.json"
STORE_LOCATIONS = NORMALIZED_DATA_DIR / "store_locations.json"
