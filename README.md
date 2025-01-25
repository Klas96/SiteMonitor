# Site Monitor

## Purpose
This project automates the generation of personalized cover letters for job applications. It scans for new job listings from a specified career site, generates cover letters using a template, and sends notifications with the generated cover letters attached.

## Tech Stack
- **Backend**: Python
- **Web Scraping**: BeautifulSoup
- **PDF Generation**: PyLaTeX
- **Email Sending**: SMTP
- **API Integration**: Anthropic API for generating content
- **Deployment**: Google Cloud Platform (GCP)
- **Containerization**: Docker

## Deployment
The application is deployed using Docker on **Google Cloud Platform (GCP)**.

## Code Architecture
The project follows a modular architecture with the following components:
- **Content Generation**: Uses the `ContentGenerator` class to create cover letter content based on job descriptions and user profiles.
- **LaTeX PDF Generation**: Uses the `LaTeXGenerator` class to format the cover letter content into a PDF.
- **Site Monitor**: The `SiteMonitor` class, hosted on GCP, scans for new job listings and processes them.
- **Email Notification**: The `EmailSender` class sends emails with the generated cover letters attached.

## Getting Started
To get a local copy up and running, follow these steps:
1. Clone the repository.
2. Rename `config.example.json` to `config.json` and update it with your personal and API details.
3. Install dependencies using `pip install -r requirements.txt`.
4. Set up environment variables for email and API keys.
5. Build and run the Docker container using:
   ```bash
   docker build -t cover-letter-generator .
   docker run -d cover-letter-generator
   ```

## Configuration
- Ensure the `latex_template_path` and other paths are correctly set in the `config.json` file.

## Usage
- The application will automatically monitor job listings and generate cover letters.
- Check the logs for any issues or notifications.
## Running the Application

To run the application, follow these steps:

1. **Initialize the Application**:
   - Ensure you have set up your `config.json` file with the necessary configurations.
   - Make sure all dependencies are installed using `pip install -r requirements.txt`.

2. **Run the Application**:
   - You can run the application using the following command:
     ```bash
     python main.py
     ```

3. **Command Line Arguments**:
   - You can list available sites to monitor using:
     ```bash
     python main.py --list
     ```
   - To monitor specific sites, use:
     ```bash
     python main.py --site <site_url_1> <site_url_2> ...
     ```