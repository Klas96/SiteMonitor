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
        self.config = config

    def send_notification(self, generated_files: List[Tuple[Dict, str]]):
        logging.info(f"Sending {len(generated_files)} notifications")
        for job_info, pdf_path in generated_files:
            email_body = "Position available:\n\n"
            email_body += f"Title: {job_info['title']}\n"
            email_body += f"oraganization: {job_info['oraganization']}\n"
            email_body += f"Location: {job_info['location']}\n"
            email_body += f"Deadline: {job_info['deadline']}\n"
            email_body += f"URL: {job_info['url']}\n"
            email_body += "-" * 50 + "\n"

            message = MIMEMultipart()
            message['From'] = self.config['email']['sender']
            message['To'] = self.config['email']['recipient']
            message['Subject'] = f"Job Notification: {job_info['title']}"
            message.attach(MIMEText(email_body, 'plain'))

            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    file_data = f.read()
                    attachment = MIMEApplication(file_data, _subtype='pdf')
                    attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
                    message.attach(attachment)

            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.config['email']['smtp_url'], 465, context=context) as server:
                    server.login(self.config['email']['sender'], self.config['email']['app_password'])
                    server.sendmail(self.config['email']['sender'], self.config['email']['recipient'], message.as_string())
                logging.info(f"Email sent successfully for job: {job_info['title']}")
                try:
                    # TODO: remove using *
                    directory = os.path.dirname(pdf_path)
                    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                    for file in os.listdir(directory):
                        if file.startswith(base_name):
                            os.remove(os.path.join(directory, file))
                    logging.info(f"Deleted file: {pdf_path}")
                except Exception as e:
                    logging.error(f"Error deleting file {pdf_path}: {e}")
                
            except Exception as e:
                logging.error(f"Error sending email for job: {job_info['title']}: {e}")
                raise
