import sys
import logging
from pathlib import Path
from config.config_manager import ConfigManager
from generators.content_generator import ContentGenerator
from generators.pdf_generator import PDFGenerator
from monitoring.web_parser import WebPageParser
from monitoring.site_monitor import SiteMonitor
from utils.email_sender import EmailSender
from utils.logger import setup_logger
import os
from flask import Flask
import schedule
import time
from datetime import datetime
from threading import Thread
import json
from datetime import timedelta
def create_directory_structure():
    directories = [
        'logs',
        'data',
        'cover_letters',
        'templates',
    ]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def init_site_monitor(site_config, config):
    """Initialize the application and its components."""
    try:
        create_directory_structure()

        # Set up logging
        setup_logger()

        # Provide a default user profile if 'user_profile' key is not present
        user_profile = site_config.get('user_profile', {
            'name': 'Default Name',
            'address': 'Default Address',
            'city': 'Default City, State ZIP',
            'email': 'default.email@example.com'
        })
        # Provide a default latex template path if 'latex_template_path' key is not present
        latex_template_path = site_config.get('latex_template_path', 'templates/default_template.tex')

        # Initialize content generator
        content_generator = ContentGenerator(
            api_key=site_config['anthropic_api_key'],
            user_profile=user_profile,
            default_cover_letter_path=latex_template_path,
            cover_letter_mode=site_config.get('cover_letter_mode', 'default')
        )

        # Initialize PDF generator
        latex_generator = PDFGenerator(
            latex_template_path=latex_template_path,
            user_profile=user_profile
        )

        # Initialize site parser
        site_parser = WebPageParser(site_config)

        # Initialize email sender
        email_config = config['email']
        email_sender = EmailSender(email_config)

        return SiteMonitor(
            config=site_config,
            parser=site_parser,
            email_sender=email_sender,
            content_generator=content_generator,
            pdf_generator=latex_generator
        )

    except Exception as e:
        logging.error(f"Error initializing application: {e}")
        raise

def run_monitor_instance(site_config, config):
    print(f"Running monitor instance for {site_config['entry_site']['url']}")
    monitor = init_site_monitor(site_config, config)
    monitor.run()

def schedule_monitors():
    config_manager = ConfigManager()
    config = config_manager.load_config()
    site_configs = config_manager.load_site_configs()
    print(f"Scheduling {len(site_configs)} site monitors")
    for site_config in site_configs:
        #TODO shedule time and interval confiurable via config
        schedule.every().day.at((datetime.now() + timedelta(minutes=1)).strftime("%H:%M")) \
            .do(run_monitor_instance, site_config=site_config, config=config)
        
        logging.info(f"Scheduled monitor for {site_config['entry_site']['url']} at {datetime.now() + timedelta(minutes=1)}")

def main():
    try:
        print("Initializing site monitor application")
        schedule_monitors()
        while True:
            logging.info(f"Checking for new entries at {datetime.now()}")
            schedule.run_pending()
            time.sleep(10*60)

    except KeyboardInterrupt:
        print("Application stopped by user")
        sys.exit(0)
    except Exception as e:   
        print(f"Application crashed: {e}")
        sys.exit(1)

app = Flask(__name__)

@app.route('/add_monitor')
def add_monitor():
    return "TODO Implement!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    main() 
    app.run(host='0.0.0.0', port=port)
