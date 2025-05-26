import json
from datetime import datetime
from pathlib import Path
from ..config.paths import USER_PROFILES_DIR
from ..utilities.logger import setup_logger


# Define all questions in a structured list
QUESTIONS = [
    # Dietary Preferences
    {
        "category": "dietary",
        "question_id": "allergies",
        "text": "Do you have any allergies?",
        "type": "text",
        "mandatory": False
    },
    {
    "category": "dietary",
    "question_id": "organic_importance",
    "text": "Hvor viktig er det for deg å kjøpe økologiske produkter? (1-5)",
    "type": "scale",
    "range": (1, 5),
    "mandatory": True
    },
    {
        "category": "dietary",
        "question_id": "organic_importance",
        "text": "How important is it for you to buy organic products? (1-5)",
        "type": "scale",
        "range": (1, 5),
        "mandatory": True
    },
    {
        "category": "dietary",
        "question_id": "local_importance",
        "text": "How important is it for you to buy local products? (1-5)",
        "type": "scale",
        "range": (1, 5),
        "mandatory": True
    },
    {
        "category": "dietary",
        "question_id": "avoid_ingredients",
        "text": "Are there any ingredients you want to avoid?",
        "type": "text",
        "mandatory": False
    },
    # Shopping Habits
    {
        "category": "shopping",
        "question_id": "shopping_mode",
        "text": "What is your preferred shopping mode?",
        "type": "choice",
        "options": ["In-store", "Delivery", "Both"],
        "mandatory": True
    },
    {
        "category": "shopping",
        "question_id": "preferred_stores",
        "text": "Which stores do you usually shop at? (select all that apply)",
        "type": "multiple_choice",
        "options": ["Kiwi", "Coop", "Oda", "Rema 1000", "Other"],
        "mandatory": True
    },
    {
        "category": "shopping",
        "question_id": "loyalty_memberships",
        "text": "Do you have any loyalty memberships? (select all that apply)",
        "type": "multiple_choice",
        "options": ["Kiwi", "Coop", "Oda", "Rema 1000", "None"],
        "mandatory": False
    },
    {
        "category": "shopping",
        "question_id": "location",
        "text": "What is your location? (city or postal code)",
        "type": "text",
        "mandatory": True
    },
    {
        "category": "shopping",
        "question_id": "transportation",
        "text": "What is your preferred mode of transportation?",
        "type": "choice",
        "options": ["Car", "Bike", "Walk", "Public Transport"],
        "mandatory": True
    },
    {
        "category": "shopping",
        "question_id": "max_distance",
        "text": "What is the maximum distance you are willing to travel for shopping? (in km)",
        "type": "number",
        "mandatory": True
    },
    # Food Preferences
    {
        "category": "food",
        "question_id": "favorite_cuisines",
        "text": "What are your favorite cuisines? (select all that apply)",
        "type": "multiple_choice",
        "options": ["Italian", "Mexican", "Asian", "Other"],
        "mandatory": False
    },
    {
        "category": "food",
        "question_id": "cooking_style",
        "text": "Do you prefer to cook from scratch or use ready-made meals?",
        "type": "choice",
        "options": ["From scratch", "Ready-made", "Both"],
        "mandatory": True
    },
    {
        "category": "food",
        "question_id": "staple_foods",
        "text": "What are your staple foods?",
        "type": "text",
        "mandatory": False
    },
    {
        "category": "food",
        "question_id": "package_size",
        "text": "Do you prefer buying in bulk or smaller packages?",
        "type": "choice",
        "options": ["Bulk", "Smaller packages"],
        "mandatory": True
    },
    {
        "category": "food",
        "question_id": "price_sensitivity",
        "text": "How price-sensitive are you? (1-5, where 1 is not price-sensitive and 5 is very price-sensitive)",
        "type": "scale",
        "range": (1, 5),
        "mandatory": True
    },
    # Sustainability Values
    {
        "category": "sustainability",
        "question_id": "carbon_footprint",
        "text": "How important is it for you to reduce your carbon footprint? (1-5)",
        "type": "scale",
        "range": (1, 5),
        "mandatory": True
    },
    {
        "category": "sustainability",
        "question_id": "food_waste_tracking",
        "text": "Are you interested in tracking your food waste?",
        "type": "yes_no",
        "mandatory": False
    },
    # Notification Preferences
    {
        "category": "notifications",
        "question_id": "deal_notifications",
        "text": "Would you like to receive notifications about deals?",
        "type": "yes_no",
        "mandatory": True
    },
    {
        "category": "notifications",
        "question_id": "expiry_reminders",
        "text": "Would you like reminders about expiring products?",
        "type": "yes_no",
        "mandatory": True
    },
    {
        "category": "notifications",
        "question_id": "recipe_suggestions",
        "text": "Would you like recipe suggestions based on your pantry?",
        "type": "yes_no",
        "mandatory": True
    },
    # Demographic Info
    {
        "category": "demographic",
        "question_id": "household_size",
        "text": "What is your household size?",
        "type": "number",
        "mandatory": True
    },
    {
        "category": "demographic",
        "question_id": "has_children",
        "text": "Do you have children?",
        "type": "yes_no",
        "mandatory": True
    },
    {
        "category": "demographic",
        "question_id": "age_group",
        "text": "What is your age group?",
        "type": "choice",
        "options": ["Under 18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
        "mandatory": True
    }
]

# Helper function to ask questions with validation and progress indicators
def ask_question(question, current, total):
    print(f"Question {current}/{total}: {question['text']}")
    while True:
        if question['type'] == 'text':
            answer = input("Your answer (leave blank to skip): ").strip()
            if not answer and not question['mandatory']:
                return None
            elif not answer and question['mandatory']:
                print("This field is mandatory. Please provide an answer.")
            else:
                return answer
        elif question['type'] == 'choice':
            print("Options:", ", ".join(question['options']))
            answer = input("Select one (enter number or leave blank to skip): ").strip()
            if not answer and not question['mandatory']:
                return None
            elif not answer and question['mandatory']:
                print("This field is mandatory. Please select an option.")
                continue
            try:
                index = int(answer) - 1
                if 0 <= index < len(question['options']):
                    return question['options'][index]
                else:
                    print("Invalid choice. Please select a valid number.")
            except ValueError:
                print("Please enter a number.")
        elif question['type'] == 'multiple_choice':
            print("Options:", ", ".join([f"{i+1}. {opt}" for i, opt in enumerate(question['options'])]))
            answer = input("Select all that apply (enter numbers separated by commas, or leave blank to skip): ").strip()
            if not answer and not question['mandatory']:
                return []
            elif not answer and question['mandatory']:
                print("This field is mandatory. Please select at least one option.")
                continue
            try:
                selections = [int(x.strip()) for x in answer.split(',')]
                valid_selections = [question['options'][i-1] for i in selections if 1 <= i <= len(question['options'])]
                if valid_selections:
                    return valid_selections
                else:
                    print("Invalid selections. Please enter valid numbers.")
            except ValueError:
                print("Please enter valid numbers separated by commas.")
        elif question['type'] == 'scale':
            min_val, max_val = question['range']
            answer = input(f"Enter a number between {min_val} and {max_val} (or leave blank to skip): ").strip()
            if not answer and not question['mandatory']:
                return None
            elif not answer and question['mandatory']:
                print("This field is mandatory. Please provide an answer.")
                continue
            try:
                num = int(answer)
                if min_val <= num <= max_val:
                    return num
                else:
                    print(f"Please enter a number between {min_val} and {max_val}.")
            except ValueError:
                print("Please enter a valid number.")
        elif question['type'] == 'yes_no':
            answer = input("Yes or No (or leave blank to skip): ").strip().lower()
            if not answer and not question['mandatory']:
                return None
            elif not answer and question['mandatory']:
                print("This field is mandatory. Please answer yes or no.")
                continue
            if answer in ['yes', 'y']:
                return True
            elif answer in ['no', 'n']:
                return False
            else:
                print("Please enter 'yes' or 'no'.")
        elif question['type'] == 'number':
            answer = input("Enter a number (or leave blank to skip): ").strip()
            if not answer and not question['mandatory']:
                return None
            elif not answer and question['mandatory']:
                print("This field is mandatory. Please provide an answer.")
                continue
            try:
                return float(answer)
            except ValueError:
                print("Please enter a valid number.")

class DagligdagsOnboarding:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.answers = {}
        self.user_id = None

    def start_onboarding(self):
        print("Welcome to Dagligdags Onboarding!")
        self.user_id = self._generate_user_id()
        total_questions = len(QUESTIONS)
        for i, question in enumerate(QUESTIONS, start=1):
            answer = ask_question(question, i, total_questions)
            self.answers[question['question_id']] = answer
        self._save_user_profile()
        self._show_profile_summary()
        return self.user_id

    def _generate_user_id(self):
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
        print("En feil oppstod under lagring av profilen. Prøv igjen.")
        raise

    def _show_profile_summary(self):
        location = self.answers.get('location', 'Not provided')
        stores = self.answers.get('preferred_stores', [])
        print(f"\nProfile Summary:")
        print(f"Location: {location}")
        print(f"Preferred Stores: {', '.join(stores) if stores else 'None selected'}")

if __name__ == "__main__":
    onboarding = DagligdagsOnboarding()
    user_id = onboarding.start_onboarding()
    print(f"Onboarding complete. Your user ID is: {user_id}")