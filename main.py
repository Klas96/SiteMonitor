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

def create_directory_structure():
    directories = [
        'logs',
        'data',
        'cover_letters',
        'templates',
    ]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def init_application():
    """Initialize the application and its components."""
    try:

        create_directory_structure()

        # Set up logging
        setup_logger()
        logging.info("Starting job monitor application")

        config_manager = ConfigManager()
        config = config_manager.config

        content_generator = ContentGenerator(config)
        latex_generator = PDFGenerator(config)
        job_parser = WebPageParser(config)
        email_sender = EmailSender(config)

        return SiteMonitor(
            config=config,
            parser=job_parser,
            content_generator=content_generator,
            pdf_generator=latex_generator,
            email_sender=email_sender
        )

    except Exception as e:
        logging.error(f"Error initializing application: {e}")
        raise

def main():
    try:
        logging.info("Initializing job monitor application")
        monitor = init_application()
        logging.info("Application initialized, starting monitor")
        monitor.run()
    except KeyboardInterrupt:
        logging.info("Application stopped by user")
        sys.exit(0)
    except Exception as e:   
        logging.error(f"Application crashed: {e}")
        sys.exit(1)

app = Flask(__name__)

@app.route('/')
def hello():
    return "Web Agent is running!"

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))
    main() 
    app.run(host='0.0.0.0', port=port)
