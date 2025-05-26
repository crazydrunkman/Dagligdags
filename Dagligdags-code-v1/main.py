#!/usr/bin/env python3
"""
Dagligdags - Norwegian Grocery Price Comparison App
Main application entry point
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from frontend.onboarding import DagligdagsOnboarding
from frontend.main_menu import MainMenu
from backend.scraping.scraping_manager import ScrapingManager
from backend.processing.match_algorithm import DealMatcher
from utilities.logger import setup_logger

class DagligdagsApp:
    def __init__(self):
        self.logger = setup_logger("main_app")
        self.current_user = None
        self.scraping_manager = ScrapingManager()
        self.deal_matcher = DealMatcher()
    
    def run(self):
        """Main application loop"""
        try:
            self._show_welcome()
            
            # Check if returning user or new user
            choice = self._get_user_choice()
            
            if choice == 1:  # New user
                self.current_user = self._new_user_flow()
            else:  # Returning user
                self.current_user = self._returning_user_flow()
            
            if self.current_user:
                # Run main application
                self._main_app_loop()
            
        except KeyboardInterrupt:
            print("\n\nTakk for at du brukte Dagligdags! 👋")
        except Exception as e:
            self.logger.error(f"Application error: {str(e)}")
            print("En feil oppstod. Sjekk loggene for detaljer.")
    
    def _show_welcome(self):
        """Show welcome screen"""
        print("\n" + "="*60)
        print("🛒 VELKOMMEN TIL DAGLIGDAGS! 🛒")
        print("="*60)
        print("Norges smarteste app for å spare penger på matvarer!")
        print("Vi finner personaliserte tilbud basert på dine preferanser.")
        print("="*60)
    
    def _get_user_choice(self):
        """Get user choice for new vs returning user"""
        print("\nEr du:")
        print("1. Ny bruker (start onboarding)")
        print("2. Eksisterende bruker (logg inn)")
        
        while True:
            try:
                choice = int(input("\nVelg (1 eller 2): "))
                if choice in [1, 2]:
                    return choice
                print("Vennligst velg 1 eller 2")
            except ValueError:
                print("Vennligst skriv inn 1 eller 2")
    
    def _new_user_flow(self):
        """Handle new user onboarding"""
        print("\n🎯 La oss sette opp din profil...")
        onboarding = DagligdagsOnboarding()
        user_id = onboarding.start_onboarding()
        
        # Initial data scraping for new user
        print("\n🔄 Henter ferske tilbud for deg...")
        self.scraping_manager.run_daily_scrape()
        
        return user_id
    
    def _returning_user_flow(self):
        """Handle returning user login"""
        user_id = input("\nSkriv inn din bruker-ID: ").strip()
        
        # Verify user exists
        from config.paths import USER_PROFILES_DIR
        profile_file = USER_PROFILES_DIR / f"user_{user_id}.json"
        
        if profile_file.exists():
            print(f"✅ Velkommen tilbake!")
            return user_id
        else:
            print("❌ Bruker ikke funnet. Oppretter ny profil...")
            return self._new_user_flow()
    
    def _main_app_loop(self):
        """Main application functionality loop"""
        main_menu = MainMenu(self.current_user, self.deal_matcher, self.scraping_manager)
        main_menu.run()

if __name__ == "__main__":
    app = DagligdagsApp()
    app.run()
