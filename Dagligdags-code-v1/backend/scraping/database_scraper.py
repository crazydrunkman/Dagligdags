import requests
import json
from datetime import datetime
from config.constants import API_ENDPOINTS, NORWEGIAN_FOOD_CATEGORIES
from config.paths import NORMALIZED_DATA_DIR
from utilities.logger import setup_logger

class DatabaseScraper:
    def __init__(self):
        self.logger = setup_logger("database_scraper")
        self.session = requests.Session()
    
    def scrape_all_databases(self):
        """Scrape all available food databases"""
        all_data = {}
        
        # Norwegian food database
        all_data['norwegian_foods'] = self._scrape_norwegian_food_db()
        
        # Nutrition data
        all_data['nutrition_data'] = self._scrape_nutrition_database()
        
        # Store locations (mock data for now)
        all_data['store_locations'] = self._get_store_locations()
        
        self._save_database_data(all_data)
        return all_data
    
    def _scrape_norwegian_food_db(self):
        """Scrape Norwegian food database"""
        try:
            # This would connect to actual Norwegian food APIs
            # For now, we'll create comprehensive mock data
            norwegian_foods = []
            
            for category, foods in NORWEGIAN_FOOD_CATEGORIES.items():
                for food in foods:
                    norwegian_foods.append({
                        'name': food,
                        'category': category,
                        'norwegian_name': food,
                        'protein_per_100g': self._get_mock_nutrition(food, 'protein'),
                        'calories_per_100g': self._get_mock_nutrition(food, 'calories'),
                        'typical_price_range': self._get_mock_price_range(food),
                        'sustainability_score': self._get_sustainability_score(food),
                        'local_availability': True
                    })
            
            self.logger.info(f"Processed {len(norwegian_foods)} Norwegian food items")
            return norwegian_foods
            
        except Exception as e:
            self.logger.error(f"Error scraping Norwegian food DB: {str(e)}")
            return []
    
    def _scrape_nutrition_database(self):
        """Get nutrition data for foods"""
        nutrition_data = {}
        
        # Mock comprehensive nutrition database
        common_foods = [
            'melk', 'egg', 'brød', 'kylling', 'laks', 'poteter', 
            'ris', 'pasta', 'ost', 'yoghurt', 'kjøtt', 'fisk'
        ]
        
        for food in common_foods:
            nutrition_data[food] = {
                'protein_g': self._get_mock_nutrition(food, 'protein'),
                'carbs_g': self._get_mock_nutrition(food, 'carbs'),
                'fat_g': self._get_mock_nutrition(food, 'fat'),
                'fiber_g': self._get_mock_nutrition(food, 'fiber'),
                'calories': self._get_mock_nutrition(food, 'calories'),
                'vitamins': self._get_mock_vitamins(food),
                'allergens': self._get_allergens(food)
            }
        
        return nutrition_data
    
    def _get_store_locations(self):
        """Get store location data for Norway"""
        # Mock store location data for Oslo area
        store_locations = {
            'oslo': {
                'coop': [
                    {'name': 'Coop Mega Storo', 'lat': 59.9407, 'lng': 10.6720, 'address': 'Stasjonsveien 25'},
                    {'name': 'Coop Prix Grünerløkka', 'lat': 59.9227, 'lng': 10.7594, 'address': 'Thorvald Meyers gate 68'},
                    {'name': 'Coop Obs Aker Brygge', 'lat': 59.9081, 'lng': 10.7297, 'address': 'Brynjulf Bulls plass 1'}
                ],
                'rema1000': [
                    {'name': 'Rema 1000 Majorstuen', 'lat': 59.9289, 'lng': 10.7166, 'address': 'Bogstadveien 44'},
                    {'name': 'Rema 1000 Grønland', 'lat': 59.9127, 'lng': 10.7618, 'address': 'Grønlandsleiret 15'},
                    {'name': 'Rema 1000 Bislett', 'lat': 59.9234, 'lng': 10.7348, 'address': 'Pilestredet 35'}
                ],
                'kiwi': [
                    {'name': 'Kiwi Frogner', 'lat': 59.9185, 'lng': 10.7097, 'address': 'Huitfeldts gate 19'},
                    {'name': 'Kiwi Sagene', 'lat': 59.9345, 'lng': 10.7512, 'address': 'Bentsebrugata 30'},
                    {'name': 'Kiwi Tøyen', 'lat': 59.9175, 'lng': 10.7698, 'address': 'Jørgensens gate 2'}
                ]
            }
        }
        
        return store_locations
    
    def _get_mock_nutrition(self, food, nutrient_type):
        """Generate realistic nutrition data"""
        nutrition_db = {
            'melk': {'protein': 3.4, 'carbs': 5.0, 'fat': 3.5, 'fiber': 0, 'calories': 64},
            'egg': {'protein': 13.0, 'carbs': 1.0, 'fat': 11.0, 'fiber': 0, 'calories': 155},
            'kylling': {'protein': 31.0, 'carbs': 0, 'fat': 3.6, 'fiber': 0, 'calories': 165},
            'laks': {'protein': 25.0, 'carbs': 0, 'fat': 14.0, 'fiber': 0, 'calories': 208},
            'brød': {'protein': 9.0, 'carbs': 49.0, 'fat': 3.2, 'fiber': 7.0, 'calories': 265}
        }
        
        return nutrition_db.get(food, {}).get(nutrient_type, 0)
    
    def _get_mock_price_range(self, food):
        """Get typical price ranges in NOK"""
        price_ranges = {
            'melk': {'min': 18, 'max': 25, 'unit': 'liter'},
            'egg': {'min': 35, 'max': 45, 'unit': '12 stk'},
            'kylling': {'min': 89, 'max': 120, 'unit': 'kg'},
            'laks': {'min': 180, 'max': 250, 'unit': 'kg'},
            'brød': {'min': 25, 'max': 40, 'unit': 'stk'}
        }
        
        return price_ranges.get(food, {'min': 10, 'max': 50, 'unit': 'kg'})
    
    def _get_sustainability_score(self, food):
        """Calculate sustainability score (1-10)"""
        sustainability_scores = {
            'laks': 4,  # Farmed salmon has environmental concerns
            'kylling': 6,  # Better than red meat
            'kjøtt': 3,  # High environmental impact
            'melk': 5,  # Moderate impact
            'poteter': 9,  # Very sustainable
            'gulrøtter': 9,  # Local vegetables
            'brød': 7  # Depends on grain source
        }
        
        return sustainability_scores.get(food, 5)
    
    def _get_mock_vitamins(self, food):
        """Get vitamin content"""
        return {
            'vitamin_d': True if food in ['laks', 'melk', 'egg'] else False,
            'vitamin_c': True if food in ['poteter', 'gulrøtter'] else False,
            'b_vitamins': True if food in ['kjøtt', 'egg', 'laks'] else False
        }
    
    def _get_allergens(self, food):
        """Get allergen information"""
        allergen_map = {
            'melk': ['lactose'],
            'egg': ['egg'],
            'brød': ['gluten'],
            'laks': ['fish'],
            'ost': ['lactose']
        }
        
        return allergen_map.get(food, [])
    
    def _save_database_data(self, data):
        """Save database data to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = NORMALIZED_DATA_DIR / f"database_data_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Saved database data to {output_file}")

# Test the database scraper
if __name__ == "__main__":
    scraper = DatabaseScraper()
    data = scraper.scrape_all_databases()
    print(f"Scraped data from {len(data)} databases")
