from docx import Document
from utils import handle_error

class OutputFormatter:
    def __init__(self):
        self.output_doc = "output.docx"

    def format_and_save_output(self, scraped_data):
        """Formats the scraped data and saves it to a Word document."""
        if not scraped_data:
            handle_error("No scraped data to format.")
            return False

        try:
            doc = Document()
            doc.add_paragraph(scraped_data)
            doc.save(self.output_doc)
            return True
        except Exception as e:
            handle_error(f"Failed to format and save output: {e}")
            return False