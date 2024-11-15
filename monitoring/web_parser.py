from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
import logging
from copy import deepcopy
import requests

class WebPageParser:
    def __init__(self, config: dict):
        self.links = config['entry_site']['links']
        self.entry_selector = config['entry_site']['entry_selector']
        self.selectors = config['entry_site']['selectors']

    def parse_listings_old(self, page_content: str) -> List[Dict]:
        entries = []
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            job_listings = soup.select('.career-card')

            for job in job_listings:
                title_element = job.select_one('.career-card__title')
                organization_element = job.select_one('.career-card__data span')
                url_element = job.get('href')
                deadline_element = job.select_one('.deadline u')

                entry = {
                    'title': title_element.text.strip() if title_element else '',
                    'organization': organization_element.text.strip() if organization_element else '',
                    'url': url_element if url_element else '',
                    'id': f"{title_element.text.strip()}_{organization_element.text.strip()}_{deadline_element.text}",
                    'timestamp': datetime.now().isoformat(),
                    'deadline': deadline_element.text,
                    'location': ''
                }
                entries.append(entry)
                
        except Exception as e:
            logging.error(f"Error parsing listings: {e}")
            
        return entries

    def parse_job_description(self, page_content: str) -> str:
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            description = soup.select_one('.entry-content')
            return description.text.strip() if description else ""
        except Exception as e:
            logging.error(f"Error parsing job description: {e}")
            return ""

    def parse_job_listings_from_config(self, page_content: str) -> List[Dict]:
        entries = []
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            job_listings = soup.select(self.entry_selector)

            for job in job_listings:
                title_element = job.select_one(self.selectors['title'])
                location_element = job.select_one(self.selectors['location'])
                age_element = job.select_one(self.selectors['age'])
                url_element = job.get('href')

                entry = {
                    'title': title_element.text.strip() if title_element else '',
                    'location': location_element.text.strip() if location_element else '',
                    'url': url_element if url_element else '',
                    'id': f"{title_element.text.strip()}_{location_element.text.strip()}_{age_element.text}",
                    'timestamp': datetime.now().isoformat(),
                    'age': age_element.text if age_element else ''
                }
                entries.append(entry)
                
        except Exception as e:
            logging.error(f"Error parsing listings: {e}")
            
        return entries

    def fetch_page(self, url: str) -> str:
        try:
            logging.info(f"Fetching page {url}")
            response = requests.get(
                url,
                headers={'User-Agent': 'Career Monitor Bot 1.0'}
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"Error fetching page {url}: {e}")
            return ""

    def parse_listings(self, page_content: str) -> List[Dict]:
        entries = []
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            entry_listings = soup.select(self.entry_selector)

            for entry in entry_listings:
                entry_values = {}
                for key, selector in self.selectors.items():
                    if isinstance(selector, dict):
                        element = entry
                        if element and element.has_attr('href'):
                            sub_page_content = self.fetch_page(element['href'])
                            sub_soup = BeautifulSoup(sub_page_content, 'html.parser')
                            element = sub_soup.select_one(selector['selector'])

                        else:
                            logging.warning(f"No <a> tag with href found for selector: {selector['url']}")
                    else:
                        element = entry.select_one(selector)
                        
                    entry_values[key] = element.get_text(strip=True) if element else ''

                # Get links
                key, selector = next(iter(self.links.items()))
                link_element = entry.select_one(selector) if selector != self.entry_selector else entry
                entry_values[key] = link_element.get('href') if link_element and link_element.get('href') else ''
                # Construct the id as a number using a hash of available keys
                id_components = []
                for key, element in entry_values.items():
                    if element:
                        id_components.append(element)
                        
                entry_values['id'] = str(abs(hash("_".join(id_components))) % (10 ** 8))  # Limiting the hash to 8 digits

                #title_element = entry.select_one(self.selectors['title'])
                #deadline_element = entry.select_one(self.selectors['deadline'])
                #url_element = entry.select_one(self.selectors['description']['url']).get('href')
                #location_element = entry.select_one(self.selectors['location'])
                #
                #entry = {
                #    'title': title_element.text.strip() if title_element else '',
                #    'location': location_element.text.strip() if location_element else '',
                #    'deadline': deadline_element.text.strip() if deadline_element else '',
                #    'url': url_element if url_element else '',
                #    'id': f"{title_element.text.strip()}_{location_element.text.strip()}_{deadline_element.text.strip()}",
                #    'timestamp': datetime.now().isoformat()
                #}
                entries.append(entry_values)

        except Exception as e:
            logging.error(f"Error parsing listings: {e}", exc_info=True)

        return entries