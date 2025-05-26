import json
from datetime import datetime
from pathlib import Path
from config.paths import USER_PROFILES_DIR
from utilities.logger import setup_logger

MVP_QUESTIONS = [
    {
        "id": "prisfokus",
        "text": "Hvor viktig er lave priser for deg? (1=ikke viktig, 5=veldig viktig)",
        "type": "scale",
        "range": (1, 5),
        "mandatory": True
    },
    {
        "id": "butikker",
        "text": "Hvilke butikker handler du oftest i? (skriv tall, flere mulig, f.eks. 1,3)",
        "type": "multiplechoice",
        "options": ["Coop", "Rema 1000", "Kiwi", "Oda"],
        "mandatory": True
    },
    {
        "id": "matrestriksjoner",
        "text": "Har du noen matrestriksjoner? (skriv tall, flere mulig, eller 0 for ingen)",
        "type": "multiplechoice",
        "options": ["Vegetar", "Vegan", "Glutenfri", "Laktosefri"],
        "mandatory": False
    },
    {
        "id": "postnummer",
        "text": "Hva er postnummeret ditt?",
        "type": "text",
        "mandatory": True
    },
    {
        "id": "transport",
        "text": "Hvordan handler du oftest?",
        "type": "choice",
        "options": ["Går", "Bil", "Sykkel", "Levering"],
        "mandatory": True
    }
]

class DagligdagsOnboarding:
    def __init__(self):
        self.logger = setup_logger("onboarding")
        self.answers = {}
        self.userid = None

    def start_onboarding(self):
        print("\nVelkommen til Dagligdags onboarding!\n")
        self.userid = self.generate_userid()
        total = len(MVP_QUESTIONS)
        for i, q in enumerate(MVP_QUESTIONS, start=1):
            answer = self.ask_question(q, i, total)
            self.answers[q["id"]] = answer
        self.save_user_profile()
        self.show_profile_summary()
        return self.userid

    def ask_question(self, q, current, total):
        print(f"\n[{current}/{total}] {q['text']}")
        if q["type"] == "text":
            while True:
                answer = input("Svar: ").strip()
                if not answer and q["mandatory"]:
                    print("Dette feltet er påkrevd.")
                else:
                    return answer or None
        elif q["type"] == "choice":
            for idx, opt in enumerate(q["options"], 1):
                print(f"{idx}. {opt}")
            while True:
                answer = input("Velg ett tall: ").strip()
                if not answer and q["mandatory"]:
                    print("Dette feltet er påkrevd.")
                elif not answer:
                    return None
                else:
                    try:
                        idx = int(answer)
                        if 1 <= idx <= len(q["options"]):
                            return q["options"][idx-1]
                        else:
                            print("Ugyldig valg.")
                    except ValueError:
                        print("Skriv et tall.")
        elif q["type"] == "multiplechoice":
            for idx, opt in enumerate(q["options"], 1):
                print(f"{idx}. {opt}")
            print("Flere mulig, separer med komma. 0 for ingen.")
            while True:
                answer = input("Dine valg: ").strip()
                if not answer and q["mandatory"]:
                    print("Dette feltet er påkrevd.")
                elif not answer:
                    return []
                else:
                    try:
                        if answer == "0":
                            return []
                        indices = [int(x) for x in answer.split(",")]
                        valid = [q["options"][i-1] for i in indices if 1 <= i <= len(q["options"])]
                        if valid:
                            return valid
                        else:
                            print("Ugyldige valg.")
                    except ValueError:
                        print("Skriv tall separert med komma.")
        elif q["type"] == "scale":
            minv, maxv = q["range"]
            while True:
                answer = input(f"Velg et tall mellom {minv} og {maxv}: ").strip()
                if not answer and q["mandatory"]:
                    print("Dette feltet er påkrevd.")
                elif not answer:
                    return None
                else:
                    try:
                        val = int(answer)
                        if minv <= val <= maxv:
                            return val
                        else:
                            print(f"Velg mellom {minv}-{maxv}.")
                    except ValueError:
                        print("Skriv et tall.")
        else:
            return None

    def generate_userid(self):
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def save_user_profile(self):
        profile = {
            "userid": self.userid,
            "createdat": datetime.now().isoformat(),
            "answers": self.answers,
        }
        profile_path = Path(USER_PROFILES_DIR) / f"{self.userid}.json"
        try:
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(profile, f, indent=4)
            self.logger.info(f"User profile saved for {self.userid}")
        except Exception as e:
            self.logger.error(f"Failed to save profile: {str(e)}")
            print("En feil oppstod under lagring av profilen.")

    def show_profile_summary(self):
        print("\n--- Oppsummering ---")
        print(f"Postnummer: {self.answers.get('postnummer', 'Ikke oppgitt')}")
        print(f"Butikker: {', '.join(self.answers.get('butikker', []))}")
        print(f"Prisfokus: {self.answers.get('prisfokus', 'Ikke oppgitt')}/5")
        print("--------------------")

if __name__ == "__main__":
    onboarding = DagligdagsOnboarding()
    userid = onboarding.start_onboarding()
    print(f"\nOnboarding fullført. Din bruker-ID er: {userid}")
