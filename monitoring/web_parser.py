from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
import logging

class WebPageParser:
    def __init__(self, config: dict):
        self.config = config

    def parse_listings(self, page_content: str) -> List[Dict]:
        entries = []
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            job_listings = soup.select('.career-card')

            for job in job_listings:
                title_element = job.select_one('.career-card__title')
                oraganization_element = job.select_one('.career-card__data span')
                url_element = job.get('href')
                deadline_element = job.select_one('.deadline u')

                entry = {
                    'title': title_element.text.strip() if title_element else '',
                    'oraganization': oraganization_element.text.strip() if oraganization_element else '',
                    'url': url_element if url_element else '',
                    'id': f"{title_element.text.strip()}_{oraganization_element.text.strip()}_{deadline_element.text}",
                    'timestamp': datetime.now().isoformat(),
                    'deadline': deadline_element.text,
                    'location': ''
                }
                entries.append(entry)
                
        except Exception as e:
            logging.error(f"Error parsing job listings: {e}")
            
        return entries

    def parse_job_description(self, page_content: str) -> str:
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            description = soup.select_one('.entry-content')
            return description.text.strip() if description else ""
        except Exception as e:
            logging.error(f"Error parsing job description: {e}")
            return ""
