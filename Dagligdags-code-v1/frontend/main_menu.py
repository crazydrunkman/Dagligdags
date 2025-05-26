# frontend/main_menu.py
from simple_term_menu import TerminalMenu
from backend.processing.match_algorithm import DealMatcher
from backend.scraping.scraping_manager import ScrapingManager
from utilities.logger import setup_logger
import time
import json
from config.paths import USER_PROFILES_DIR, NORMALIZED_DATA_DIR

class MainMenu:
    def __init__(self, user_id, deal_matcher, scraping_manager):
        self.logger = setup_logger("main_menu")
        self.user_id = user_id
        self.deal_matcher = deal_matcher
        self.scraping_manager = scraping_manager
        self.user_profile = self._load_user_profile()
        
        # Norwegian-language menu options
        self.menu_options = [
            "Vis personaliserte tilbud",
            "Kartvisning av butikker",
            "Håndter pantry-liste",
            "Oppskriftsforslag",
            "Innstillinger",
            "Avslutt"
        ]
        
        # Menu styling for Norwegian users
        self.menu_style = {
            "cursor": "➤ ",
            "cursor_style": ("fg_cyan", "bold"),
            "menu_cursor_style": ("fg_yellow", "bg_black", "bold"),
            "menu_highlight_style": ("fg_black", "bg_cyan", "bold")
        }

    def _load_user_profile(self):
        """Load user profile from JSON file"""
        profile_path = USER_PROFILES_DIR / f"user_{self.user_id}.json"
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed loading profile: {str(e)}")
            return {}

    def _display_menu(self):
        """Show interactive terminal menu"""
        terminal_menu = TerminalMenu(
    self.menu_options,
    title=f"\n📋 DAGLIGDAGS HOVEDMENY - {self.user_id}",
    menu_cursor="➤ ",
    menu_cursor_style=("fg_cyan", "bold"),
    menu_highlight_style=("fg_black", "bg_cyan", "bold")
        )

        return terminal_menu.show()

    def run(self):
        """Main menu interaction loop"""
        while True:
            choice_index = self._display_menu()
            
            if choice_index == 0:
                self._show_personalized_deals()
            elif choice_index == 1:
                self._show_map_view()
            elif choice_index == 2:
                self._manage_pantry()
            elif choice_index == 3:
                self._show_recipe_suggestions()
            elif choice_index == 4:
                self._show_settings()
            elif choice_index == 5 or choice_index is None:
                print("\nTakk for at du brukte Dagligdags! 👋")
                break

    def _show_personalized_deals(self):
        """Display deals personalized for Norwegian user"""
        print("\n🔍 Søker etter de beste tilbudene for deg...")
        
        # Load latest deals
        deals_file = max(NORMALIZED_DATA_DIR.glob("deals_*.json"), default=None)
        if not deals_file:
            print("Ingen tilgjengelige tilbud funnet. Prøv igjen senere.")
            return
        
        with open(deals_file, "r", encoding="utf-8") as f:
            all_deals = json.load(f)
        
        # Get personalized deals
        user_location = self.user_profile.get('answers', {}).get('location', "Oslo")
        personalized_deals = self.deal_matcher.find_personalized_deals(
            self.user_id, all_deals, user_location
        )
        
        # Display top 10 deals
        print("\n🎯 Dine beste mattilbud denne uken:")
        for idx, deal in enumerate(personalized_deals[:10], 1):
            print(f"{idx}. {deal['product']} - {deal['price']} kr hos {deal['store'].capitalize()}")
            print(f"   📍 {deal.get('distance', '?')} km | 🕒 {deal.get('valid_until', 'Ukjent')}")
        
        input("\nTrykk Enter for å fortsette...")

    def _show_map_view(self):
        """Show map of stores with Norwegian locations"""
        print("\n🗺️ Nærliggende butikker med gode tilbud:")
        # This would integrate with your map data
        print("Kartfunksjonalitet er under utvikling. Sjekk tilbake senere!")
        time.sleep(2)

    def _manage_pantry(self):
        """Manage Norwegian pantry items"""
        print("\n🥫 Din pantry-liste:")
        # Implement pantry management logic here
        print("Pantry-håndtering kommer snart!")
        time.sleep(2)

    def _show_recipe_suggestions(self):
        """Show recipes based on Norwegian ingredients"""
        print("\n👩🍳 Oppskriftsforslag basert på dine varer:")
        # Implement recipe suggestions
        print("Oppskriftsfunksjonen er under arbeid!")
        time.sleep(2)

    def _show_settings(self):
        """User settings for Norwegian preferences"""
        print("\n⚙️ Dine innstillinger:")
        print(f"Sted: {self.user_profile.get('answers', {}).get('location', 'Ikke satt')}")
        print(f"Prisfølsomhet: {self.user_profile.get('answers', {}).get('price_sensitivity', 3)}/5")
        print(f"Bærekraftsprioritering: {self.user_profile.get('answers', {}).get('sustainability_importance', 3)}/5")
        input("\nTrykk Enter for å fortsette...")

# Example usage (for testing)
if __name__ == "__main__":
    mock_user_id = "test_user_123"
    main_menu = MainMenu(
        user_id=mock_user_id,
        deal_matcher=DealMatcher(),
        scraping_manager=ScrapingManager()
    )
    main_menu.run()
