import json
import logging
from pathlib import Path
from typing import Dict

class ConfigManager:
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> dict:
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Config file not found: {self.config_path}")
            config = self.create_default_config()
            self.save_config(config)
            return config

    def create_default_config(self) -> dict:
        return {
            'career_site_url': 'defaultsite url',
            'check_interval': 3000000,
            'latex_template_path': 'templates/cover_letter_template.tex',
            'user_profile': {
                'name': 'Your Name',
                'address': 'Your Address',
                'city': 'City, State ZIP',
                'email': 'your.email@example.com',
                'skills': ['Python', 'Data Analysis', 'Project Management'],
                'background': ['software development', 'data science'],
                'experience': 'Previous oraganization Name',
                'achievement': 'Describe a key achievement here.',
                'value_proposition': 'Describe your unique value proposition here.'
            }
        }

    def save_config(self, config: Dict):
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)
