from utils import handle_error, extract_python_code
from config import PROMPTS
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import threading
import time
import google.generativeai as genai

class GeminiAPIHandler:
    def __init__(self, api_handler, timeout=60):
        self.api_handler = api_handler
        self.timeout = timeout
        self.current_task = None
        self._stop_event = threading.Event()

    def _execute_with_timeout(self, func, *args):
        """Execute a function with timeout."""
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args)
            try:
                return future.result(timeout=self.timeout)
            except TimeoutError:
                self._stop_event.set()
                handle_error(f"Operation timed out after {self.timeout} seconds")
                return None
            finally:
                self._stop_event.clear()

    def analyze_html(self, html_content, target_description):
        """Sends HTML and target description to Gemini API for analysis with timeout."""
        if not self.api_handler.chat_session:
            handle_error("Chat session not initialized.")
            return None

        analysis_results = {}
        for url, html in html_content.items():
            try:
                def _analyze():
                    if self._stop_event.is_set():
                        raise InterruptedError("Analysis was interrupted")
                    
                    prompt = PROMPTS['html_analysis'].format(
                        url=url,
                        target_description=target_description,
                        html=html[:5000]  # Limiting content size for better performance
                    )
                    
                    response = self.api_handler.send_message(prompt)
                    if response:
                        return extract_python_code(response)
                    return None

                result = self._execute_with_timeout(_analyze)
                if result:
                    analysis_results[url] = result
                else:
                    handle_error(f"Gemini API analysis failed for {url}.")
                    analysis_results[url] = None

            except TimeoutError:
                handle_error(f"HTML analysis timed out for {url}")
                analysis_results[url] = None
            except Exception as e:
                handle_error(f"An error occurred during Gemini API analysis for {url}: {e}")
                analysis_results[url] = None

        return analysis_results

    def generate_code(self, analysis_results):
        """Sends HTML analysis to Gemini API for code generation with timeout."""
        if not self.api_handler.chat_session:
            handle_error("Chat session not initialized.")
            return None

        try:
            def _generate():
                if self._stop_event.is_set():
                    raise InterruptedError("Code generation was interrupted")
                
                prompt = PROMPTS['code_generation'].format(
                    analysis_results=analysis_results
                )
                
                response = self.api_handler.send_message(prompt)
                if response:
                    return extract_python_code(response)
                return None

            generated_code = self._execute_with_timeout(_generate)
            if not generated_code:
                handle_error("Gemini API code generation failed.")
                return None

            return generated_code

        except TimeoutError:
            handle_error(f"Code generation timed out after {self.timeout} seconds")
            return None
        except Exception as e:
            handle_error(f"An error occurred during Gemini API code generation: {e}")
            return None