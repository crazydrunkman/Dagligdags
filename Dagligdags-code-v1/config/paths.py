import os
from pathlib import Path

# Base project directory
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "backend" / "data"
LOG_DIR = PROJECT_ROOT / "logs"

# Data directories
GROCERY_DATA_DIR = DATA_DIR / "grocery_data"
USER_PROFILES_DIR = DATA_DIR / "user_profiles"
NORMALIZED_DATA_DIR = DATA_DIR / "normalized_data"

# Scraping directories
NEWSLETTER_DIR = GROCERY_DATA_DIR / "newsletters"
PDF_STORAGE_DIR = NEWSLETTER_DIR / "pdfs"
PARSED_DATA_DIR = NEWSLETTER_DIR / "parsed"

# Create directories if they don't exist
for directory in [DATA_DIR, GROCERY_DATA_DIR, USER_PROFILES_DIR, 
                  NORMALIZED_DATA_DIR, NEWSLETTER_DIR, PDF_STORAGE_DIR, 
                  PARSED_DATA_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File paths
USER_PROFILE_TEMPLATE = USER_PROFILES_DIR / "user_{user_id}.json"
DEALS_DATABASE = NORMALIZED_DATA_DIR / "deals.json"
STORE_LOCATIONS = NORMALIZED_DATA_DIR / "store_locations.json"
