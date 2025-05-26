# Norwegian-specific constants and settings
import os

# Store URLs for scraping
STORE_URLS = {
    'coop': 'https://coop.no/uke-tilbud/',
    'rema': 'https://rema.no/aktuelt/aktuelle-tilbud/',
    'kiwi': 'https://kiwi.no/tilbud/',
    'bunnpris': 'https://www.bunnpris.no/tilbud/',
    'meny': 'https://meny.no/tilbud/',
    'oda': 'https://oda.com/no/products/',
    'wolt': 'https://wolt.com/nb/nor/oslo/grocery',
    'foodora': 'https://www.foodora.no/'
}

# Price thresholds (NOK)
PRICE_CATEGORIES = {
    'cheap': 25.0,
    'mid_range': 50.0,
    'expensive': 100.0,
    'premium': 200.0
}

# Distance calculations (km)
DISTANCE_PENALTIES = {
    'walking': 0.5,      # Heavy penalty for walking far
    'biking': 0.3,       # Moderate penalty for biking
    'driving': 0.15,     # Light penalty for driving
    'public_transport': 0.25
}

# User preference weights
PREFERENCE_WEIGHTS = {
    'organic': 1.5,
    'local': 1.3,
    'price_sensitive': 2.0,
    'sustainability': 1.4,
    'convenience': 1.2
}

# Scraping schedule (cron format)
SCRAPE_SCHEDULE = {
    'newsletters': '0 4 * * 1',  # Every Monday 4 AM
    'databases': '0 2 * * *',    # Daily 2 AM
    'price_check': '0 */6 * * *' # Every 6 hours
}

# Norwegian food categories
NORWEGIAN_FOOD_CATEGORIES = {
    'dairy': ['melk', 'ost', 'yoghurt', 'smør', 'fløte'],
    'meat': ['kjøtt', 'kylling', 'svinekjøtt', 'lam', 'fisk', 'laks'],
    'vegetables': ['poteter', 'gulrøtter', 'løk', 'brokkoli', 'salat'],
    'grains': ['brød', 'pasta', 'ris', 'havre', 'mel'],
    'nordic_staples': ['lefse', 'knekkebrød', 'kaviar', 'leverpostei']
}

# API endpoints
API_ENDPOINTS = {
    'matvaretabellen': 'https://www.matvaretabellen.no/api/foods',
    'norwegian_food_db': 'https://ndb.nal.usda.gov/ndb/api/v2'
}
