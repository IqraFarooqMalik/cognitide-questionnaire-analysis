import os
import json
import pickle
import re

class QuestionnairePreprocessor:
    def __init__(self, config_path='./config.json'):
        self.config = self.load_config(config_path)
        self.ROOT_DIR = self.config['root_dir']
        self.PICKLE_FILE = self.config['pickle_file']

            # Debugging check
        print(f"Checking directory: {self.ROOT_DIR}")
        print(f"Exists: {os.path.exists(self.ROOT_DIR)}")

    QUESTIONNAIRE_MAPPING = {
        "pre": "pre_study_questionnaire",
        "post": "post_study_questionnaire",
        "mid_study_coding": "mid_study_coding_questionnaire",
        "mid_study_debugging": "mid_study_debugging_questionnaire",
        "mid_study_email": "mid_study_email_questionnaire",
        "mid_study_documentation": "mid_study_documentation_questionnaire"
    }

    @staticmethod
    def load_config(config_path):
        """Loads the configuration file."""
        with open(config_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def clean_filename(filename):
        """Extracts questionnaire type from filename by removing timestamp and prefix."""
        match = re.search(r"questionnaire_([a-zA-Z0-9_-]+)\.json", filename)
        if match:
            key = match.group(1)
            return QuestionnairePreprocessor.QUESTIONNAIRE_MAPPING.get(key, key + "_questionnaire")
        return filename.replace(".json", "_questionnaire")

    def load_questionnaire_data(self):
        participants = []
        for participant_id in os.listdir(self.ROOT_DIR):
            participant_path = os.path.join(self.ROOT_DIR, participant_id)
            if not os.path.isdir(participant_path):
                continue

            participant_key = participant_id.replace("Participant_", "")
            participant_data = {"id": participant_key, "questionnaires": []}

            for file_name in sorted(os.listdir(participant_path)):
                if file_name.endswith(".json"):
                    file_path = os.path.join(participant_path, file_name)
                    with open(file_path, "r", encoding="utf-8") as f:
                        questionnaire_data = json.load(f)
                    questionnaire_key = self.clean_filename(file_name)
                    participant_data["questionnaires"].append({
                        "name": questionnaire_key,
                        "responses": questionnaire_data
                    })
            participants.append(participant_data)
        return participants

    def preprocess(self):
        data = self.load_questionnaire_data()
        with open(self.PICKLE_FILE, "wb") as f:
            pickle.dump(data, f)
        print(f"Questionnaire data saved to {self.PICKLE_FILE}")

    def print_formatted_data(self):
        with open(self.PICKLE_FILE, "rb") as file:
            data = pickle.load(file)
        formatted_data = json.dumps(data, indent=4)
        print(formatted_data)

if __name__ == "__main__":
    processor = QuestionnairePreprocessor()
    processor.preprocess()
    processor.print_formatted_data()
