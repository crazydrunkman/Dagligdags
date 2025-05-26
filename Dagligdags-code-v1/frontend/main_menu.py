import json
from pathlib import Path
from simple_term_menu import TerminalMenu
from config.paths import USER_PROFILES_DIR
from frontend.onboarding import DagligdagsOnboarding

class MainMenu:
    def __init__(self, userid):
        self.userid = userid
        self.profile = self.load_profile()
        self.menu_options = [
            "Se personlige tilbud",
            "Kartvisning av butikker",
            "Fullfør onboarding/profil",
            "Innstillinger",
            "Avslutt"
        ]

    def load_profile(self):
        profile_path = Path(USER_PROFILES_DIR) / f"{self.userid}.json"
        if profile_path.exists():
            with open(profile_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            print("Fant ikke brukerprofil.")
            return {}

    def show(self):
        print(f"\nHei, {self.userid}! Hva vil du gjøre?")
        menu = TerminalMenu(self.menu_options, title="Dagligdags Hovedmeny", menu_cursor="➤ ")
        while True:
            idx = menu.show()
            if idx == 0:
                self.show_deals()
            elif idx == 1:
                self.show_map()
            elif idx == 2:
                self.complete_profile()
            elif idx == 3:
                self.show_settings()
            elif idx == 4 or idx is None:
                print("Ha en fin dag! 👋")
                break

    def show_deals(self):
        print("\n[DEMO] Personlige tilbud vises her basert på din profil.\n")
        input("Trykk Enter for å gå tilbake til menyen.")

    def show_map(self):
        print("\n[DEMO] Kart over butikker vises her.\n")
        input("Trykk Enter for å gå tilbake til menyen.")

    def complete_profile(self):
        print("\nDu kan nå fylle ut flere profilspørsmål for bedre tilpassede tilbud!")
        onboarding = DagligdagsOnboarding()
        onboarding.start_onboarding()
        input("Trykk Enter for å gå tilbake til menyen.")

    def show_settings(self):
        print("\n[DEMO] Innstillinger vises her.\n")
        input("Trykk Enter for å gå tilbake til menyen.")

if __name__ == "__main__":
    userid = input("Skriv inn bruker-ID: ").strip()
    menu = MainMenu(userid)
    menu.show()
