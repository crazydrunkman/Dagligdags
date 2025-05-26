from pathlib import Path
import json
from config.paths import USER_PROFILES_DIR
from utilities.logger import setup_logger

class OnboardingFlow:
    """
    Norwegian-focused onboarding with 6 essential questions
    Uses emoji scales and quick-tap inputs for low friction
    """
    
    def __init__(self):
        self.logger = setup_logger("onboarding")
        self.essential_questions = [
            {
                "id": "price_sensitivity",
                "text": "Hvor viktig er lav pris for deg?",
                "type": "scale",
                "labels": ["Ikke viktig 😞", "Veldig viktig 😊"]
            },
            {
                "id": "preferred_stores",
                "text": "Hvor handler du vanligvis?",
                "type": "multi_select",
                "options": ["Coop", "Rema 1000", "Kiwi", "Oda"]
            },
            {
                "id": "dietary_restrictions", 
                "text": "Har du noen matrestriksjoner?",
                "type": "checkboxes",
                "options": ["Vegetar", "Vegan", "Glutenfri", "Laktosefri"]
            },
            {
                "id": "location",
                "text": "Hvor bor du (postnummer)?",
                "type": "text"
            },
            {
                "id": "transport_mode",
                "text": "Hvordan handler du?",
                "type": "single_choice",
                "options": ["Går", "Bil", "Sykkel", "Levering"]
            },
            {
                "id": "sustainability",
                "text": "Hvor viktig er bærekraft?",
                "type": "scale",
                "labels": ["Ikke viktig 😞", "Veldig viktig 😊"]
            }
        ]
        self.optional_questions = [...]  # For later expansion

    def start_flow(self) -> dict:
        """Guided onboarding with progress visualization"""
        print("\nVelkommen til Dagligdags! La oss komme i gang:\n")
        responses = {}
        
        for idx, q in enumerate(self.essential_questions, 1):
            print(f"Spørsmål {idx}/{len(self.essential_questions)}")
            responses[q['id']] = self._ask_question(q)
            print("---")
            
        self._save_profile(responses)
        return responses

    def _ask_question(self, question: dict):
        """Unified question handler with input validation"""
        print(f"\n{question['text']}")
        
        if question['type'] == 'scale':
            return self._handle_scale(question['labels'])
        elif question['type'] == 'multi_select':
            return self._handle_multi_select(question['options'])
        # ... other input types

    def _handle_scale(self, labels: list) -> int:
        """Emoji-based 1-5 scale input"""
        print(f"  {labels[0]} 1 2 3 4 5 {labels[1]}")
        while True:
            try:
                val = int(input("Velg (1-5): "))
                if 1 <= val <= 5:
                    return val
                raise ValueError
            except:
                print("Vennligst skriv et tall mellom 1-5")

    # ... other input handlers

    def _save_profile(self, data: dict):
        """Save with Norwegian timestamp format"""
        profile_path = USER_PROFILES_DIR / f"user_{data.get('location', 'unknown')}.json"
        try:
            with profile_path.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"Profil lagret: {profile_path}")
        except Exception as e:
            self.logger.error(f"Lagring feilet: {str(e)}")
            raise
