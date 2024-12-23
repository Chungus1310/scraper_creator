import customtkinter as ctk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import logging
from datetime import datetime
from api_handler import APIHandler
from url_handler import URLHandler
from target_parser import TargetParser
from html_fetcher import HTMLFetcher
from gemini_api_handler import GeminiAPIHandler
from code_executor import CodeExecutor
from output_formatter import OutputFormatter
from utils import handle_error
from save_to_word import save_response_to_word
import platform
import subprocess
import os
import threading
import queue

class GUILogHandler(logging.Handler):
    """Custom logging handler that updates both GUI and file."""
    def __init__(self, text_widget, queue):
        super().__init__()
        self.text_widget = text_widget
        self.queue = queue
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Create file handler
        log_filename = f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.file_handler = logging.FileHandler(log_filename, mode='a')
        self.file_handler.setFormatter(self.formatter)

    def emit(self, record):
        """Emit a log record to both GUI and file."""
        msg = self.format(record)
        self.file_handler.emit(record)
        self.queue.put((self._update_log, (msg,)))

    def _update_log(self, msg):
        """Update the text widget with the log message."""
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", msg + "\n")
        self.text_widget.see("end")  # Auto-scroll to the bottom
        self.text_widget.configure(state="disabled")

class ModernWebScraperApp:
    def __init__(self):
        self.window = ttk.Window(themename="darkly")
        self.window.title("Kitten Scraper")
        self.window.geometry("1000x800")
        
        # Initialize handlers (keeping existing functionality)
        self.api_handler = APIHandler()
        self.url_handler = URLHandler()
        self.target_parser = TargetParser()
        self.html_fetcher = HTMLFetcher(self.url_handler)
        self.gemini_api_handler = GeminiAPIHandler(self.api_handler)
        self.code_executor = CodeExecutor()
        self.output_formatter = OutputFormatter()

        # Initialize queue for thread-safe GUI updates
        self.update_queue = queue.Queue()
        
        self.create_gui()
        self.setup_logging()
        self.create_bindings()
        
        # Start the GUI update checker
        self.check_queue()

    def setup_logging(self):
        """Set up logging configuration."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        root_logger.handlers = []
        
        # Add our custom handler
        gui_handler = GUILogHandler(self.log_text, self.update_queue)
        root_logger.addHandler(gui_handler)
        
        # Log initial message
        logging.info("Web Scraper initialized and ready")

    def create_gui(self):
        # Main container with padding
        self.main_frame = ttk.Frame(self.window, padding="20")
        self.main_frame.pack(fill=BOTH, expand=YES)

        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            header_frame,
            text="Web Scraper",
            font=("Helvetica", 24, "bold"),
            bootstyle="inverse-primary"
        ).pack(side=LEFT)

        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=BOTH, expand=YES)

        # Configuration Tab
        config_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(config_frame, text="Configuration")

        # API Key Section
        api_frame = ttk.LabelFrame(config_frame, text="API Configuration", padding=10)
        api_frame.pack(fill=X, pady=(0, 10))

        self.api_key_entry = ttk.Entry(api_frame, show="•")
        self.api_key_entry.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        
        self.validate_api_button = ttk.Button(
            api_frame,
            text="Validate API Key",
            command=self.validate_api_key,
            bootstyle="outline-primary"
        )
        self.validate_api_button.pack(side=LEFT)
        
        self.api_status_label = ttk.Label(api_frame, text="")
        self.api_status_label.pack(side=LEFT, padx=(10, 0))

        # URLs Section
        url_frame = ttk.LabelFrame(config_frame, text="URLs Configuration", padding=10)
        url_frame.pack(fill=X, pady=(0, 10))

        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        
        self.validate_url_button = ttk.Button(
            url_frame,
            text="Validate URLs",
            command=self.validate_urls,
            bootstyle="outline-primary"
        )
        self.validate_url_button.pack(side=LEFT)
        
        self.url_status_label = ttk.Label(url_frame, text="")
        self.url_status_label.pack(side=LEFT, padx=(10, 0))

        # Target Description Section
        target_frame = ttk.LabelFrame(config_frame, text="Target Description", padding=10)
        target_frame.pack(fill=BOTH, expand=YES)

        self.target_entry = ttk.Text(target_frame, height=6)
        self.target_entry.pack(fill=BOTH, expand=YES)

        # Action Buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=X, pady=(20, 0))

        self.start_button = ttk.Button(
            button_frame,
            text="Start Scraping",
            command=self.start_scraping,
            bootstyle="success",
            state="disabled"
        )
        self.start_button.pack(side=RIGHT)

        # Output Tab
        output_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(output_frame, text="Output")

        # Create a paned window to separate logs and results
        paned = ttk.PanedWindow(output_frame, orient="vertical")
        paned.pack(fill=BOTH, expand=YES)

        # Progress Section
        progress_frame = ttk.Frame(paned)
        progress_frame.pack(fill=X)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            bootstyle="success-striped"
        )
        self.progress_bar.pack(fill=X)

        self.status_label = ttk.Label(
            progress_frame,
            text="Ready to start",
            font=("Helvetica", 10)
        )
        self.status_label.pack(pady=(5, 0))

        # Log Section
        log_frame = ttk.LabelFrame(paned, text="Process Log", padding=10)
        paned.add(log_frame, weight=1)

        self.log_text = ttk.Text(
            log_frame,
            wrap=WORD,
            height=8,
            state="disabled"
        )
        self.log_text.pack(fill=BOTH, expand=YES, side=LEFT)

        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scrollbar.pack(side=RIGHT, fill=Y)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        # Results Section
        results_frame = ttk.LabelFrame(paned, text="Scraping Results", padding=10)
        paned.add(results_frame, weight=2)

        self.output_text = ttk.Text(
            results_frame,
            wrap=WORD,
            state="disabled",
            height=15
        )
        self.output_text.pack(fill=BOTH, expand=YES, side=LEFT)

        output_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.output_text.yview)
        output_scrollbar.pack(side=RIGHT, fill=Y)
        self.output_text.configure(yscrollcommand=output_scrollbar.set)

        # Output Actions
        self.open_output_button = ttk.Button(
            output_frame,
            text="Open Output File",
            command=self.open_output_file,
            bootstyle="outline-primary",
            state="disabled"
        )
        self.open_output_button.pack(pady=(10, 0))

    def create_bindings(self):
        """Set up all event bindings."""
        # Validate on key release for text inputs
        self.api_key_entry.bind('<KeyRelease>', lambda e: self.check_start_button_state())
        self.url_entry.bind('<KeyRelease>', lambda e: self.check_start_button_state())
        self.target_entry.bind('<KeyRelease>', lambda e: self.check_start_button_state())
        
        # Bind Return/Enter key to validation buttons
        self.api_key_entry.bind('<Return>', lambda e: self.validate_api_key())
        self.url_entry.bind('<Return>', lambda e: self.validate_urls())
        
        # Bind validate buttons to their respective functions
        self.validate_api_button.configure(command=self.validate_api_key)
        self.validate_url_button.configure(command=self.validate_urls)

    def validate_api_key(self):
        """Validates the entered API key."""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            self.api_status_label.configure(text="API key required", bootstyle="danger")
            return
            
        self.api_handler.set_api_key(api_key)
        self.api_status_label.configure(text="Validating...")
        
        try:
            if self.api_handler.validate_api_key():
                self.api_status_label.configure(text="Valid ✓", bootstyle="success")
            else:
                self.api_status_label.configure(text="Invalid ✗", bootstyle="danger")
        except Exception as e:
            self.api_status_label.configure(text=f"Error: {str(e)}", bootstyle="danger")
        
        self.check_start_button_state()

    def validate_urls(self):
        """Validates the entered URLs."""
        urls_text = self.url_entry.get().strip()
        if not urls_text:
            self.url_status_label.configure(text="URL required", bootstyle="danger")
            self.check_start_button_state()
            return
            
        urls = [url.strip() for url in urls_text.split(',') if url.strip()]
        if not urls:
            self.url_status_label.configure(text="No valid URLs found", bootstyle="danger")
            self.check_start_button_state()
            return
            
        self.url_handler.urls = []  # Reset URLs
        self.url_status_label.configure(text="Validating...", bootstyle="warning")
        self.window.update()  # Update UI immediately
        
        try:
            for url in urls:
                self.url_handler.add_url(url)

            if self.url_handler.validate_urls():
                self.url_status_label.configure(text="Valid ✓", bootstyle="success")
            else:
                self.url_status_label.configure(text="Invalid URLs", bootstyle="danger")
        except Exception as e:
            self.url_status_label.configure(text=f"Error: {str(e)}", bootstyle="danger")
        
        self.check_start_button_state()
    def check_start_button_state(self):
        """Enables the Start button if all required fields are valid."""
        api_key = self.api_key_entry.get().strip()
        urls = self.url_entry.get().strip()
        target_description = self.target_entry.get("1.0", "end-1c").strip()
        
        # Get current validation states
        api_valid = self.api_status_label.cget("text") == "Valid ✓"
        url_valid = self.url_status_label.cget("text") == "Valid ✓"
        
        # Check all conditions
        if all([
            api_key,
            urls,
            target_description,
            api_valid,
            url_valid
        ]):
            self.start_button.configure(state="normal")
        else:
            self.start_button.configure(state="disabled")


    def check_queue(self):
        """Check for GUI updates from the worker thread."""
        try:
            while True:
                update = self.update_queue.get_nowait()
                if update:
                    func, args = update
                    func(*args)
        except queue.Empty:
            pass
        finally:
            self.window.after(100, self.check_queue)

    def safe_update_progress(self, value, status_text):
        """Thread-safe method to update progress."""
        self.update_queue.put((self._update_progress, (value, status_text)))

    def _update_progress(self, value, status_text):
        """Internal method to actually update the GUI."""
        self.progress_bar["value"] = value
        self.status_label.configure(text=status_text)
    def safe_update_output(self, text, state="disabled"):
        """Thread-safe method to update output text."""
        self.update_queue.put((self._update_output, (text, state)))

    def _update_output(self, text, state):
        """Internal method to update output text."""
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.configure(state=state)

    def safe_update_button_state(self, button, state):
        """Thread-safe method to update button state."""
        self.update_queue.put((button.configure, {"state": state}))

    def scraping_worker(self):
        """Worker function to run the scraping process in a separate thread."""
        try:
            logging.info("Starting scraping process")
            
            # Get and set target description
            target_description = self.target_entry.get("1.0", "end-1c").strip()
            self.target_parser.set_target_description(target_description)
            logging.info(f"Target description set: {target_description[:50]}...")

            # Step 1: Fetch HTML
            self.safe_update_progress(10, "Fetching HTML...")
            logging.info("Fetching HTML content...")
            html_content = self.html_fetcher.fetch_html()
            logging.info("HTML content fetched successfully")
            self.safe_update_progress(20, "HTML fetched successfully")

            # Step 2: Analyze HTML
            self.safe_update_progress(30, "Analyzing HTML with Gemini API...")
            logging.info("Starting HTML analysis with Gemini API...")
            try:
                analysis_results = self.gemini_api_handler.analyze_html(html_content, target_description)
                logging.info("HTML analysis completed successfully")
                self.safe_update_progress(40, "HTML analysis complete")
            except TimeoutError:
                logging.error("HTML analysis timed out")
                raise Exception("HTML analysis took too long to complete. Please try again or simplify your target description.")
            except Exception as e:
                logging.error(f"HTML analysis failed: {str(e)}")
                raise Exception(f"HTML analysis failed: {str(e)}")
            
            # Step 3: Generate code
            self.safe_update_progress(50, "Generating code with Gemini API...")
            logging.info("Generating code with Gemini API...")
            try:
                generated_code = self.gemini_api_handler.generate_code(analysis_results)
                logging.info("Code generation completed successfully")
                self.safe_update_progress(60, "Code generation complete")
            except TimeoutError:
                logging.error("Code generation timed out")
                raise Exception("Code generation took too long to complete. Please try again.")
            except Exception as e:
                logging.error(f"Code generation failed: {str(e)}")
                raise Exception(f"Code generation failed: {str(e)}")
            
            if generated_code:
                # Step 4: Save and execute code
                self.safe_update_progress(70, "Executing generated code...")
                logging.info("Saving and executing generated code...")
                
                if self.code_executor.save_code(generated_code):
                    scraped_data = self.code_executor.execute_code()
                    logging.info("Code executed successfully")

                    if scraped_data:
                        self.safe_update_progress(80, "Formatting output...")
                        logging.info("Formatting and saving output...")
                        
                        if self.output_formatter.format_and_save_output(scraped_data):
                            # Step 5: Save final output to Word document
                            self.safe_update_progress(90, "Saving output to Word document...")
                            logging.info("Saving response to Word document...")
                            output_file = save_response_to_word(scraped_data)
                            logging.info("Response saved to Word document")
                            
                            self.safe_update_progress(100, "Scraping complete! ✓")
                            self.safe_update_output(scraped_data)
                            self.safe_update_button_state(self.open_output_button, "normal")
                            logging.info("Scraping process completed successfully")
                        else:
                            raise Exception("Error formatting output")
                    else:
                        raise Exception("Error executing code")
                else:
                    raise Exception("Error saving code")
            else:
                raise Exception("Error generating code")
                
        except Exception as e:
            logging.error(f"Scraping process failed: {str(e)}")
            self.safe_update_progress(0, f"Error: {str(e)}")

    def start_scraping(self):
        """Starts the web scraping process in a separate thread."""
        # Switch to output tab
        self.notebook.select(1)
        
        # Reset progress
        self.safe_update_progress(0, "Starting scraping process...")
        
        # Start the scraping process in a separate thread
        threading_thread = threading.Thread(target=self.scraping_worker)
        threading_thread.daemon = True
        threading_thread.start()

    def open_output_file(self):
        """Opens the output Word document."""
        try:
            if platform.system() == "Windows":
                os.startfile(self.output_formatter.output_doc)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", self.output_formatter.output_doc])
            else:  # Linux
                subprocess.Popen(["xdg-open", self.output_formatter.output_doc])
        except Exception as e:
            handle_error(f"Failed to open output file: {e}")
            self.status_label.configure(
                text=f"Failed to open output file: {e}",
                bootstyle="danger"
            )

if __name__ == "__main__":
    app = ModernWebScraperApp()
    app.window.mainloop()