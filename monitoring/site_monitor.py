import requests
import time
import logging
from typing import List, Dict
from pathlib import Path
import json
import os
import shutil

class SiteMonitor:
    def __init__(self, config: dict, parser, email_sender, content_generator=None, pdf_generator=None, send_starting_entries: bool = False):
        self.config = config
        self.parser = parser
        self.content_generator = content_generator
        self.pdf_generator = pdf_generator
        self.email_sender = email_sender
        self.known_entries = self.load_known_entries()
        self.send_props = config.get('send_props', list(self.parser.selectors.keys()))
        logging.info(f"Loaded {len(self.known_entries)} known entries")

        self.send_starting_entries = config['send_starting_entries']
        if not self.send_starting_entries:
            # add current entries to known entries
            self.known_entries = self.parser.parse_listings(self.fetch_page(self.config['entry_site']['url']))
            self.known_entries.extend(self.known_entries)
            self.save_known_entries()

    def load_known_entries(self) -> List[Dict]:
        try:
            with open('data/known_entries.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            Path('data').mkdir(exist_ok=True)
            return []

    def save_known_entries(self):
        with open('data/known_entries.json', 'w') as f:
            json.dump([entry['id'] for entry in self.known_entries], f)

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
        include_filters = self.config.get('include_filters', {})
        if include_filters:
            filtered_entries = [
                entry for entry in new_entries
                if all(filter_value in entry.get(key, '') for key, filter_value in include_filters.items())
            ]
        else:
            filtered_entries = new_entries

        exclude_filters = self.config.get('exclude_filters', {})
        if exclude_filters:
            filtered_entries = [
                entry for entry in filtered_entries
                if not any(filter_value in entry.get(key, '') for key, filter_value in exclude_filters.items())
            ]

        return filtered_entries

    def process_new_entries(self, new_entries: List[Dict]):
        generated_entries = []
        for entry in new_entries:
            try:
                # Fetch full job description
                job_description = self.parser.parse_job_description(
                    self.fetch_page(entry['url'])
                )

                # Generate cover letter content
                latex_content = self.content_generator.generate_cover_letter(entry, job_description)

                # Create PDF
                latex_content = self.pdf_generator.make_latex_compilable(latex_content)
                pdf_path, latex_output_path = self.pdf_generator.compile_pdf(latex_content, entry)
                generated_entries.append((entry, [pdf_path, latex_output_path]))

            except Exception as e:
                logging.error(f"Error processing entry {entry['title']}: {e}")

        return generated_entries

    def run(self):
        logging.info(f"Starting site monitor for {self.config['entry_site']['url']}")

        try:
            logging.info(f"Fetching page {self.config['entry_site']['url']}")
            page_content = self.fetch_page(self.config['entry_site']['url'])
            if page_content:
                current_entries = self.parser.parse_listings(page_content)
                logging.info(f"Found {len(current_entries)} entries on {self.config['entry_site']['url']}")

                selected_entries = self.select_entries(current_entries)
                logging.info(f"Found {len(selected_entries)} relevant entries")

                if self.config['debug']['stop_after_one'] and selected_entries:
                    logging.info(f"Debug mode: stopping after one entry")
                    selected_entries = selected_entries[:1]

                generated_entries = []
                # Process entries config loop todo
                if 'pdf' in self.config['process_entries'] or 'tex' in self.config['process_entries']:
                    generated_entries = self.process_new_entries(selected_entries)

                if generated_entries:
                    self.email_sender.send_emails(generated_entries, send_props=self.send_props)
                    if self.config['to_disk'] and generated_entries:
                        for entry, file_paths in generated_entries:
                            entry_dir = os.path.join('data', entry['id'])
                            os.makedirs(entry_dir, exist_ok=True)
                            entry_file_path = os.path.join(entry_dir, 'entry.json')
                            with open(entry_file_path, 'w') as entry_file:
                                json.dump(entry, entry_file, indent=4)
                            for file_path in file_paths:
                                if file_path and os.path.exists(file_path):
                                    shutil.copy(file_path, entry_dir)
                else:
                    generated_entries = [(entry, []) for entry in selected_entries]
                    self.email_sender.send_emails(generated_entries, send_props=self.send_props)

                self.known_entries.extend(selected_entries)
                self.save_known_entries()

        except Exception as e:
            logging.error(f"Error in site monitor: {e}")
            time.sleep(60)
