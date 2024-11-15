import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Tuple, Dict
import logging
import os
import ssl

class EmailSender:
    def __init__(self, config: dict):
        self.sender = config['sender']
        self.recipient = config['recipient']
        self.smtp_url = config['smtp_url']
        self.app_password = config['app_password']

    def send_emails(self, email_entries: List[Tuple[Dict, str]], send_props: List[str]):
        logging.info(f"Sending {len(email_entries)} notifications")
        
        for entry, file_paths in email_entries:
            email_body = "New entry:\n\n"
            logging.info(f"Sending props: {send_props} for entry {entry['id']}")
            for key in send_props:
                email_body += f"{key.capitalize()}: {entry[key]}\n"
            email_body += "-" * 50 + "\n"

            message = MIMEMultipart()
            message['From'] = self.sender
            message['To'] = self.recipient
            message['Subject'] = f"New entry: {entry['id']}"
            message.attach(MIMEText(email_body, 'plain'))

            for file_path in file_paths:
                if file_path and os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                        attachment = MIMEApplication(file_data, _subtype='pdf')
                        attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
                        message.attach(attachment)

            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_url, 465, context=context) as server:
                    server.login(self.sender, self.app_password)
                    server.sendmail(self.sender, self.recipient, message.as_string())
                logging.info(f"Email sent successfully for new entry id {entry['id']}")
                
                for file_path in file_paths:
                    try:
                        directory = os.path.dirname(file_path)
                        base_name = os.path.splitext(os.path.basename(file_path))[0]
                        for file in os.listdir(directory):
                            if file.startswith(base_name):
                                os.remove(os.path.join(directory, file))
                        logging.info(f"Deleted file: {file_path}")
                    except Exception as e:
                        logging.error(f"Error deleting file {file_path}: {e}")
                
            except Exception as e:
                logging.error(f"Error sending email for job: {entry['title']}: {e}")
                raise
