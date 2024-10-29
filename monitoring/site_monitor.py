import requests
import time
import logging
from typing import List, Dict
from pathlib import Path
import json

class SiteMonitor:
    def __init__(self, config: dict, parser, content_generator, pdf_generator, email_sender, send_starting_entries: bool = False):
        self.config = config
        self.parser = parser
        self.content_generator = content_generator
        self.pdf_generator = pdf_generator
        self.email_sender = email_sender
        self.known_entries = self.load_known_entries()
        logging.info(f"Loaded {len(self.known_entries)} known entries")

        self.send_starting_entries = config['send_starting_entries']
        if not self.send_starting_entries:
            pass
            # add current entries to known entries
            #self.known_entries.extend(self.known_entries)
            #self.save_known_entries()

    def load_known_entries(self) -> List[Dict]:
        try:
            with open('data/known_entries.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            Path('data').mkdir(exist_ok=True)
            return []

    def save_known_entries(self):
        with open('data/known_entries.json', 'w') as f:
            json.dump(self.known_entries, f)

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

    def select_entries(self, current_entries: List[Dict]) -> List[Dict]:

        skip_known = False
        if skip_known:
            new_entries = [
            entry for entry in current_entries
                if not any(known['id'] == entry['id'] for known in self.known_entries)
            ]
        else:
            new_entries = current_entries

        # Additional filters
        filters = self.config.get('filters')
        filtered_entries = [
            entry for entry in new_entries
            if not any(title_filter in entry['title'] for title_filter in filters['title_filter'])
        ]

        return filtered_entries

    def process_new_jobs(self, new_entries: List[Dict]):
        generated_files = []
        for entry in new_entries:
            if any(known['id'] == entry['id'] for known in self.known_entries):
                logging.info(f"Skipping known entry {entry['title']}")
                continue
            try:
                # Fetch full job description
                job_description = self.parser.parse_job_description(
                    self.fetch_page(entry['url'])
                )

                # Generate cover letter content
                latex_content = self.content_generator.generate_cover_letter(entry, job_description)

                # Create PDF
                latex_content = self.pdf_generator.make_latex_compilable(latex_content)
                pdf_path = self.pdf_generator.compile_pdf(latex_content, entry)
                generated_files.append((entry, pdf_path))

            except Exception as e:
                logging.error(f"Error processing job {entry['title']}: {e}")

        if generated_files:
            logging.info(f"Sending {len(generated_files)} new notifications")
            self.email_sender.send_notification(generated_files)
            self.known_entries.extend(new_entries)
            self.save_known_entries()

    def run(self):
        logging.info("Starting career site monitor")
        while True:
            try:
                logging.info(f"Fetching page {self.config['career_site_url']}")
                page_content = self.fetch_page(self.config['career_site_url'])
                if page_content:
                    current_entries = self.parser.parse_listings(page_content)
                    logging.info(f"Found {len(current_entries)} entries on {self.config['career_site_url']}")
                    selected_entries = self.select_entries(current_entries)
                    logging.info(f"Found relevant {len(selected_entries)} new entries")
                    if self.config['debug']['stop_after_one'] and selected_entries:
                        logging.info(f"Debug mode: stopping after one entry")
                        selected_entries = selected_entries[:1]
                    if selected_entries:
                        self.process_new_jobs(selected_entries)
                
                time.sleep(self.config['check_interval'])
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(60)
