import requests
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from config.constants import API_ENDPOINTS, REQUEST_TIMEOUT
from config.paths import NORMALIZED_DATA_DIR
from utilities.logger import setup_logger

class DatabaseScraper:
    """Scrapes and normalizes food databases for Norwegian market."""
    
    def __init__(self):
        self.logger = setup_logger("database_scraper")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Dagligdags/1.0 (+https://github.com/crazydrunkman/Dagligdags)'
        })
        self.timeout = REQUEST_TIMEOUT
        self.verify_ssl = False  # Managed via environment variables

    def scrape_all_sources(self) -> Dict[str, Any]:
        """Coordinate scraping across all configured data sources."""
        results = {}
        
        # Norwegian Food Database
        results['matvaretabellen'] = self._scrape_endpoint(
            'matvaretabellen',
            validator=lambda data: isinstance(data, list) and len(data) > 0
        )
        
        # USDA National Nutrient Database
        results['usda'] = self._scrape_endpoint(
            'usda',
            validator=lambda data: 'items' in data
        )
        
        return self._normalize_data(results)

    def _scrape_endpoint(self, endpoint_key: str, validator: callable) -> List[Dict]:
        """Generic API scraper with validation."""
        url = API_ENDPOINTS.get(endpoint_key)
        if not url:
            self.logger.error(f"⚠️ Missing endpoint config for {endpoint_key}")
            return []
        
        try:
            response = self.session.get(url, timeout=self.timeout, verify=self.verify_ssl)
            response.raise_for_status()
            data = response.json()
            
            if not validator(data):
                raise ValueError(f"Invalid data structure from {endpoint_key}")
                
            self.logger.info(f"✅ Successfully scraped {endpoint_key}: {len(data)} items")
            return data
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"🚨 HTTP error {e.response.status_code} for {endpoint_key}")
        except json.JSONDecodeError:
            self.logger.error(f"🔴 Invalid JSON response from {endpoint_key}")
        except Exception as e:
            self.logger.error(f"⚠️ Unexpected error scraping {endpoint_key}: {str(e)}")
        return []

    def _normalize_data(self, raw_data: Dict) -> Dict:
        """Normalize data to Norwegian standards."""
        normalized = {}
        
        # Normalize matvaretabellen data
        if 'matvaretabellen' in raw_data:
            normalized['norwegian_foods'] = [
                self._normalize_matvare(item)
                for item in raw_data['matvaretabellen']
                if 'Navn' in item and 'Energi' in item
            ]
        
        # Normalize USDA data
        if 'usda' in raw_data:
            normalized['international_foods'] = [
                self._normalize_usda(item)
                for item in raw_data['usda'].get('items', [])
            ]
        
        return normalized

    def _normalize_matvare(self, item: Dict) -> Dict:
        """Normalize Norwegian food database entries."""
        return {
            'norwegian_name': item.get('Navn', ''),
            'scientific_name': item.get('Varegruppe', ''),
            'nutrients': {
                'energy_kj': item.get('Energi', 0),
                'protein_g': item.get('Protein', 0),
            },
            'source': 'matvaretabellen'
        }

    def _normalize_usda(self, item: Dict) -> Dict:
        """Normalize USDA entries for Norwegian context."""
        return {
            'english_name': item.get('name', ''),
            'nutrients': {
                'energy_kcal': item.get('calories', 0),
                'protein_g': item.get('protein', 0),
            },
            'source': 'usda'
        }

    def save_results(self, data: Dict) -> Path:
        """Save normalized data with versioning."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = NORMALIZED_DATA_DIR / f"food_db_{timestamp}.json"
            
            with output_path.open('w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"💾 Saved normalized database to {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"💥 Failed to save database: {str(e)}")
            raise

if __name__ == "__main__":
    scraper = DatabaseScraper()
    data = scraper.scrape_all_sources()
    scraper.save_results(data)
