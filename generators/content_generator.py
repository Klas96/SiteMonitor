from anthropic import Anthropic
from typing import Dict
import logging
from datetime import datetime
import os

class ContentGenerator:
    def __init__(self, api_key: str, user_profile: dict, default_cover_letter_path: str, cover_letter_mode: str = 'default'):
        self.api_key = api_key
        self.user_profile = user_profile
        self.default_cover_letter_path = default_cover_letter_path
        self.cover_letter_mode = cover_letter_mode
        self.client = Anthropic(api_key=self.api_key)

    def generate_cover_letter(self, job_info: Dict, job_description: str) -> str:
        with open('templates/prompt_cover_letter_latex.txt', 'r') as file:
            prompt_template = file.read()

        prompt = prompt_template.replace('{{JOB_DESCRIPTION}}', job_description)
        prompt = prompt.replace('{{APPLICANT_INFO}}', f"""
        - Name: {self.user_profile['name']}
        - Skills: {', '.join(self.user_profile['skills'])}
        - Background: {', '.join(self.user_profile['background'])}
        - Experience: {self.user_profile['experience']}
        - Key Achievements: {self.user_profile['achievements']}
        - Personal Traits: {', '.join(self.user_profile['personal_traits'])}
        - Interests: {', '.join(self.user_profile['interests'])}
        """)
        try:
            # todo fail?
            # Check the cover letter mode
            cover_letter_mode = self.cover_letter_mode
            if cover_letter_mode == 'default':
                # Default behavior
                with open(self.default_cover_letter_path, 'r') as file:
                    default_cover_letter = file.read()
                return default_cover_letter
            elif cover_letter_mode == 'AI':
                response = self.client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1500,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                letter_text = response.content[0].text
                current_date = datetime.now().strftime("%Y-%m-%d")
                letter_text = letter_text.replace('<DateInsertLater>', current_date)
                return letter_text
            elif cover_letter_mode == 'none':
                pass
            else:
                raise ValueError(f"Invalid cover letter mode: {cover_letter_mode}")
        except Exception as e:
            logging.error(f"Error generating cover letter content: {e}")
            raise
