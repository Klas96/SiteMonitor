from datetime import datetime
from pathlib import Path
import subprocess
from typing import Dict
import logging
from pylatex import Document
from pylatex.utils import NoEscape
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import re

class PDFGenerator:
    def __init__(self, latex_template_path: str, user_profile: Dict):
        self.latex_template_path = latex_template_path
        self.user_profile = user_profile

    def substitute_template(self, content: str, job_info: Dict) -> str:
        # TODO Use for Default Template
        # Move to content generator
        # latex
        with open(self.latex_template_path, 'r', encoding='utf-8') as file:
            template = file.read()

        # Determine the language
        language = job_info.get('language', 'eng')

        if language == 'eng':
            title = 'Cover Letter'
            closing_salutation = 'Sincerely,'
            # Thank you for considering my application.
        elif language == 'sve':
            title = 'Personligt Brev'
            closing_salutation = 'Med vänliga hälsningar,'
        else:
            title = 'Cover Letter'

        
        replacements = {
            '{{DATE}}': datetime.now().strftime('%B %d, %Y'),
            '{{organization_NAME}}': job_info['organization'],
            '{{JOB_TITLE}}': job_info['title'],
            '{{RECIPIENT_NAME}}': 'Hiring Manager',
            '{{SENDER_NAME}}': self.user_profile['name'],
            '{{SENDER_ADDRESS}}': self.user_profile['address'],
            '{{SENDER_CITY}}': self.user_profile['city'],
            '{{SENDER_EMAIL}}': self.user_profile['email'],
            '{{LETTER_CONTENT}}': content,
            '{{TITLE}}': title,
            '{{LANGUAGE}}': language,
            '{{CLOSING_SALUTATION}}': closing_salutation
        }
        
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, value)
        
        return template

    def _escape_latex(self, text: str) -> str:
        # TODO let claude handle this
        special_chars = ['\\', '&', '%', '$', '#', '_', '{', '}', '~', '^']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        
        # Replace line breaks with \bigskip and \noindent
        text = re.sub(r'\n+', '\n\n\\bigskip\n\\noindent\n', text)
        
        return text
    
    def make_latex_compilable(self, latex_content: str) -> str:
        try:
            # Extract content inside <latex_cover_letter> tags
            start_tag = '<latex_cover_letter>'
            end_tag = '</latex_cover_letter>'
            start_index = latex_content.find(start_tag)
            end_index = latex_content.find(end_tag)

            if start_index != -1 and end_index != -1:
                latex_content = latex_content[start_index + len(start_tag):end_index].strip()
            return latex_content
        except Exception as e:
            logging.error(f"Error during LaTeX compilation check: {e}")
            return self._escape_latex(latex_content)

    def compile_pdf(self, latex_content: str, job_info: Dict, method: str = 'latex') -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        organization_name = ''.join(c for c in job_info['organization'] if c.isalnum())
        pdf_output_path = Path('cover_letters') / f"Cover_Letter_{organization_name}_{timestamp}.pdf"
        tex_output_path = pdf_output_path.with_suffix('.tex')

        pdf_output_path.parent.mkdir(exist_ok=True)

        if method == 'latex':
            try:
                logging.info(f"Writing latex content to {tex_output_path}")
                tex_output_path.write_text(latex_content, encoding='utf-8')                
                try:
                    subprocess.run(
                        ['pdflatex', '-output-directory', str(pdf_output_path.parent), str(tex_output_path)],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=60
                    )
                except subprocess.CalledProcessError as e:
                    logging.error(f"Failed to compile LaTeX to PDF: {e.stderr.decode()}")
                    return str(tex_output_path)
            except Exception as e:
                logging.error(f"Failed to compile LaTeX to PDF: {e}")
                return str(tex_output_path)
        elif method == 'reportlab':
            # Generate a PDF using reportlab with A4 page size
            c = canvas.Canvas(str(pdf_output_path), pagesize=A4)
            width, height = A4

            # Add content to the PDF
            c.drawString(100, height - 100, latex_content.split('\n')[0])

            # Save the PDF
            c.save()

        return str(pdf_output_path), str(tex_output_path)