import json
import logging
from pathlib import Path
from typing import Dict

class ConfigManager:
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.config = self.load_config()
        # load site configs
        self.site_configs = self.load_site_configs()

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
            'check_interval': 3600,
            'latex_template_path': 'templates/cover_letter_template.tex',
            'user_profile': {
                'name': 'Your Name',
                'address': 'Your Address',
                'city': 'City, State ZIP',
                'email': 'your.email@example.com',
                'skills': ['Python', 'Data Analysis', 'Project Management'],
                'background': ['software development', 'data science'],
                'experience': 'Previous organization Name',
                'achievement': 'Describe a key achievement here.',
                'value_proposition': 'Describe your unique value proposition here.'
            }
        }

    def save_config(self, config: Dict):
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)

    def load_site_configs(self) -> list:
        site_configs = []
        for site_config_path in Path('config/site_configs').glob('*.json'):
            with open(site_config_path, 'r') as f:
                # Add Anthropic API key to the config
                site_configs.append(json.load(f))
                # TODO: use environment variable?
                site_configs[-1]['anthropic_api_key'] = self.config['anthropic_api_key']
        return site_configs
