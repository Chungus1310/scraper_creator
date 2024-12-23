import subprocess
import os
from utils import handle_error

class CodeExecutor:
    def __init__(self):
        self.output_file = "scraped_data.txt"

    def save_code(self, code):
        """Saves the generated code to a file."""
        try:
            with open("scraper.py", "w") as f:
                f.write(code)
            return True
        except Exception as e:
            handle_error(f"Failed to save code: {e}")
            return False

    def execute_code(self):
        """Executes the generated code and captures output."""
        try:
            # Make the scraper file executable
            os.chmod("scraper.py", 0o755)

            # Run the scraper and capture output
            process = subprocess.Popen(["python", "scraper.py"],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       text=True)
            stdout, stderr = process.communicate()

            if stderr:
                handle_error(f"Error during code execution:\n{stderr}")
                return None

            # Save the output to a file
            with open(self.output_file, "w") as f:
                f.write(stdout)

            return stdout

        except Exception as e:
            handle_error(f"Failed to execute code: {e}")
            return None