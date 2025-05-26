import json
import math
from datetime import datetime
from typing import Dict, List, Tuple
from config.constants import PREFERENCE_WEIGHTS, DISTANCE_PENALTIES
from config.paths import USER_PROFILES_DIR
from utilities.logger import setup_logger, log_deal_match

class DealMatcher:
    def __init__(self):
        self.logger = setup_logger("deal_matcher")
    
    def find_personalized_deals(self, user_id: str, available_deals: List[Dict], user_location: Tuple[float, float] = None) -> List[Dict]:
        """Find deals personalized for specific user"""
        
        # Load user profile
        user_profile = self._load_user_profile(user_id)
        if not user_profile:
            self.logger.warning(f"No profile found for user {user_id}")
            return []
        
        # Score all deals
        scored_deals = []
        for deal in available_deals:
            score = self._calculate_match_score(deal, user_profile, user_location)
            if score > 0:  # Only include deals with positive scores
                deal_copy = deal.copy()
                deal_copy['match_score'] = score
                deal_copy['recommendation_reason'] = self._get_recommendation_reason(deal, user_profile)
                scored_deals.append(deal_copy)
        
        # Sort by score (highest first)
        scored_deals.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Log matching results
        avg_score = sum(d['match_score'] for d in scored_deals) / len(scored_deals) if scored_deals else 0
        log_deal_match(user_id, len(scored_deals), avg_score)
        
        return scored_deals[:50]  # Return top 50 deals
    
    def _calculate_match_score(self, deal: Dict, user_profile: Dict, user_location: Tuple[float, float] = None) -> float:
        """Calculate how well a deal matches user preferences"""
        
        score = 0.0
        
        # Base price score (higher discount = higher score)
        if 'discount_percentage' in deal:
            score += deal['discount_percentage'] * 0.1
        elif 'price' in deal:
            # Lower price gets higher score
            price_score = max(0, 100 - deal['price']) * 0.01
            score += price_score
        
        # Organic preference
        if user_profile.get('organic_preference', 3) >= 4 and deal.get('organic', False):
            score += PREFERENCE_WEIGHTS['organic']
        
        # Local preference
        if user_profile.get('local_preference', 3) >= 4 and deal.get('local', False):
            score += PREFERENCE_WEIGHTS['local']
        
        # Price sensitivity
        if user_profile.get('price_sensitivity', 3) >= 4:
            score += PREFERENCE_WEIGHTS['price_sensitive']
        
        # Dietary restrictions
        user_allergies = user_profile.get('allergies', [])
        deal_allergens = deal.get('allergens', [])
        if any(allergen in deal_allergens for allergen in user_allergies):
            score -= 5.0  # Heavy penalty for allergens
        
        # Diet compatibility
        user_diet = user_profile.get('diet', [])
        if 'vegetarian' in user_diet and deal.get('product_category') == 'meat':
            score -= 3.0
        if 'vegan' in user_diet and deal.get('product_category') in ['meat', 'dairy']:
            score -= 3.0
        
        # Cuisine preferences
        user_cuisines = user_profile.get('cuisine_preferences', [])
        deal_cuisine = deal.get('cuisine_type', '')
        if deal_cuisine and deal_cuisine.lower() in [c.lower() for c in user_cuisines]:
            score += 1.5
        
        # Pantry type matching
        user_pantry = user_profile.get('pantry_type', '')
        if user_pantry == 'high_protein' and deal.get('protein_content', 0) > 20:
            score += 2.0
        
        # Package size preference
        user_package_pref = user_profile.get('package_preference', 'regular')
        deal_package = deal.get('package_size', 'regular')
        if user_package_pref == deal_package:
            score += 1.0
        
        # Store preference
        user_stores = user_profile.get('preferred_stores', [])
        if deal.get('store') in user_stores:
            score += 1.5
        
        # Membership discount
        user_memberships = user_profile.get('loyalty_memberships', [])
        deal_store = deal.get('store', '')
        if self._has_membership_discount(deal_store, user_memberships):
            score += 2.0
        
        # Distance penalty
        if user_location and 'store_location' in deal:
            distance = self._calculate_distance(user_location, deal['store_location'])
            transport_mode = user_profile.get('transport_mode', 'walking')
            distance_penalty = distance * DISTANCE_PENALTIES.get(transport_mode, 0.5)
            score -= distance_penalty
        
        # Sustainability score
        if user_profile.get('sustainability_importance', 3) >= 4:
            sustainability_score = deal.get('sustainability_score', 5)
            score += (sustainability_score - 5) * 0.3  # Bonus/penalty based on sustainability
        
        return max(0, score)  # Never negative
    
    def _get_recommendation_reason(self, deal: Dict, user_profile: Dict) -> str:
        """Generate human-readable reason for recommendation"""
        reasons = []
        
        if deal.get('organic') and user_profile.get('organic_preference', 3) >= 4:
            reasons.append("matches your organic preference")
        
        if deal.get('local') and user_profile.get('local_preference', 3) >= 4:
            reasons.append("is locally produced")
        
        if user_profile.get('price_sensitivity', 3) >= 4 and deal.get('discount_percentage', 0) > 20:
            reasons.append(f"{deal.get('discount_percentage', 0):.0f}% discount")
        
        user_cuisines = user_profile.get('cuisine_preferences', [])
        deal_cuisine = deal.get('cuisine_type', '')
        if deal_cuisine and deal_cuisine.lower() in [c.lower() for c in user_cuisines]:
            reasons.append(f"perfect for {deal_cuisine} cooking")
        
        if user_profile.get('pantry_type') == 'high_protein' and deal.get('protein_content', 0) > 20:
            reasons.append("high in protein")
        
        if not reasons:
            reasons.append("good value")
        
        return ", ".join(reasons)
    
    def _has_membership_discount(self, store: str, memberships: List[str]) -> bool:
        """Check if user has membership for store discount"""
        membership_map = {
            'coop': 'coop_medlem',
            'rema': 'ae_rema',
            'ica': 'ica_kort'
        }
        
        required_membership = membership_map.get(store.lower())
        return required_membership in [m.lower() for m in memberships]
    
    def _calculate_distance(self, user_location: Tuple[float, float], store_location: Tuple[float, float]) -> float:
        """Calculate distance between user and store in km"""
        lat1, lon1 = user_location
        lat2, lon2 = store_location
        
        # Haversine formula
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _load_user_profile(self, user_id: str) -> Dict:
        """Load user profile from file"""
        profile_file = USER_PROFILES_DIR / f"user_{user_id}.json"
        
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            self.logger.error(f"Error loading profile for user {user_id}: {str(e)}")
            return {}
    
    def optimize_shopping_basket(self, user_id: str, shopping_list: List[str], available_deals: List[Dict]) -> Dict:
        """Optimize shopping across multiple stores"""
        
        user_profile = self._load_user_profile(user_id)
        max_distance = user_profile.get('max_distance', 5.0)  # km
        
        # Group deals by store
        stores_with_items = {}
        for deal in available_deals:
            store = deal.get('store')
            product = deal.get('product', '').lower()
            
            # Check if deal matches shopping list
            for list_item in shopping_list:
                if list_item.lower() in product:
                    if store not in stores_with_items:
                        stores_with_items[store] = []
                    stores_with_items[store].append({
                        'item': list_item,
                        'deal': deal,
                        'price': deal.get('price', 0)
                    })
        
        # Calculate optimal combination
        combinations = self._generate_store_combinations(stores_with_items, shopping_list)
        best_combination = self._evaluate_combinations(combinations, user_profile)
        
        return best_combination
    
    def _generate_store_combinations(self, stores_with_items: Dict, shopping_list: List[str]) -> List[Dict]:
        """Generate possible store combinations for shopping list"""
        # Simplified: just return single-store and two-store combinations
        combinations = []
        
        # Single store combinations
        for store, items in stores_with_items.items():
            found_items = [item['item'] for item in items]
            coverage = len(set(found_items) & set(shopping_list)) / len(shopping_list)
            
            combinations.append({
                'stores': [store],
                'items': items,
                'coverage': coverage,
                'total_price': sum(item['price'] for item in items)
            })
        
        # Two store combinations (for demonstration)
        store_names = list(stores_with_items.keys())
        for i, store1 in enumerate(store_names):
            for store2 in store_names[i+1:]:
                combined_items = stores_with_items[store1] + stores_with_items[store2]
                found_items = [item['item'] for item in combined_items]
                coverage = len(set(found_items) & set(shopping_list)) / len(shopping_list)
                
                combinations.append({
                    'stores': [store1, store2],
                    'items': combined_items,
                    'coverage': coverage,
                    'total_price': sum(item['price'] for item in combined_items)
                })
        
        return combinations
    
    def _evaluate_combinations(self, combinations: List[Dict], user_profile: Dict) -> Dict:
        """Evaluate and return best store combination"""
        best_score = -1
        best_combination = None
        
        for combo in combinations:
            score = combo['coverage'] * 10  # Favor high coverage
            score -= len(combo['stores']) * 2  # Penalty for multiple stores
            score -= combo['total_price'] * 0.01  # Penalty for high price
            
            if score > best_score:
                best_score = score
                best_combination = combo
        
        return best_combination or {'stores': [], 'items': [], 'coverage': 0, 'total_price': 0}

# Test the matcher
if __name__ == "__main__":
    matcher = DealMatcher()
    
    # Mock deals for testing
    test_deals = [
        {
            'product': 'Organic Milk',
            'price': 22.90,
            'store': 'coop',
            'organic': True,
            'allergens': ['lactose']
        },
        {
            'product': 'Chicken Breast',
            'price': 89.90,
            'store': 'rema',
            'protein_content': 31,
            'allergens': []
        }
    ]
    
    # This would work with real user profile
    personalized_deals = matcher.find_personalized_deals("test_user", test_deals)
    print(f"Found {len(personalized_deals)} personalized deals")
