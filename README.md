# Project Name

## Purpose
This project automates the generation of personalized cover letters for job applications. It scrapes job listings from a specified career site, generates cover letters using a template, and sends notifications with the generated cover letters attached.

## Tech Stack
- **Backend**: Python
- **Web Scraping**: BeautifulSoup
- **PDF Generation**: PyLaTeX
- **Email Sending**: SMTP
- **API Integration**: Anthropic API for generating cover letter content
- **Deployment**: Heroku

## Deployment
The application is deployed on **Heroku**, which provides a platform-as-a-service (PaaS) that enables developers to build, run, and operate applications entirely in the cloud. The `Procfile` specifies the command to run the application.

## Code Architecture
The project follows a modular architecture with the following components:
- **Content Generation**: Uses the `ContentGenerator` class to create cover letter content based on job descriptions and user profiles.
- **LaTeX Generation**: Uses the `LaTeXGenerator` class to format the cover letter content into a PDF.
- **Site Monitor**: The `SiteMonitor` class periodically checks for new job listings and processes them.
- **Email Notification**: The `EmailSender` class sends emails with the generated cover letters attached.

## Getting Started
To get a local copy up and running, follow these steps:
1. Clone the repository.
2. Install dependencies using `pip install -r requirements.txt`.
3. Set up environment variables for email and API keys.
4. Run the application using `heroku local` or `python main.py`.

## Configuration
- Update the `config.json` file with your personal and API details.
- Ensure the `latex_template_path` and other paths are correctly set.

## Usage
- The application will automatically monitor job listings and generate cover letters.
- Check the logs for any issues or notifications.

