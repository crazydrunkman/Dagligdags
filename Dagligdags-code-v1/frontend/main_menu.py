from typing import Dict
from simple_term_menu import TerminalMenu
from config.paths import USER_PROFILES_DIR

class MainMenu:
    """
    Norwegian UI with 'Fullfør onboarding' section
    Uses clear visual hierarchy for deal browsing
    """
    
    def __init__(self, user_profile: Dict):
        self.profile = user_profile
        self.menu_title = f"🌟 Hovedmeny | {self.profile.get('location', 'Norge')}"
        self.options = [
            "Se tilbud",
            "Kartvisning", 
            "[!] Fullfør profil",
            "Innstillinger",
            "Avslutt"
        ]
        
    def show(self):
        """Interactive terminal menu"""
        menu = TerminalMenu(
            menu_entries=self.options,
            title=self.menu_title,
            menu_cursor="➤ ",
            menu_highlight_style=("fg_black", "bg_cyan")
        )
        
        while True:
            choice = menu.show()
            if choice == 0:
                self._show_deals()
            elif choice == 2:
                self._complete_profile()
            # ... other handlers

    def _complete_profile(self):
        """Trigger optional onboarding steps"""
        from .onboarding import OnboardingFlow  # Lazy import
        print("\n💡 Ta 2 minutter for bedre tilpassede tilbud:")
        OnboardingFlow().start_flow(optional_only=True)
