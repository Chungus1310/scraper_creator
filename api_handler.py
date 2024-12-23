import os
import google.generativeai as genai
from utils import handle_error, make_request
from config import AI_CONFIG

class APIHandler:
    def __init__(self):
        self.api_key = None
        self.model = None
        self.chat_session = None
        self.config = AI_CONFIG['html_analyzer']
        self._configure_genai_proxy()

    def _configure_genai_proxy(self):
        """Configures proxy settings for the Gemini API client."""
        try:
            # First try without proxy
            genai.configure(api_key="test_key")
            test_model = genai.GenerativeModel('gemini-pro')
            
        except Exception as e:
            handle_error(f"Direct connection failed, configuring proxy: {e}")
            # If direct connection fails, configure with proxy
            from utils import get_proxies
            proxies = get_proxies()
            os.environ['HTTP_PROXY'] = proxies['http']
            os.environ['HTTPS_PROXY'] = proxies['https']

    def set_api_key(self, api_key):
        """Sets the API key and configures the Gemini API."""
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        try:
            self.model = genai.GenerativeModel(
                model_name=self.config['model'],
                generation_config=self.config['generation_config']
            )
            self.chat_session = self.model.start_chat(history=[])
        except Exception as e:
            handle_error(f"Failed to initialize Gemini model: {e}")
            self.model = None
            self.chat_session = None

    def validate_api_key(self):
        """Validates the API key by attempting to initialize the Gemini model."""
        if not self.api_key:
            handle_error("API key not set.")
            return False

        try:
            # Try to initialize the model and create a chat session
            if not self.model:
                self.model = genai.GenerativeModel(
                    model_name=self.config['model'],
                    generation_config=self.config['generation_config']
                )
                self.chat_session = self.model.start_chat(history=[])
            
            # Try to send a test message
            response = self.chat_session.send_message("test")
            if response and response.text:
                return True
            else:
                handle_error("API key validation failed: No response received")
                return False
        except Exception as e:
            handle_error(f"An error occurred during API key validation: {e}")
            return False

    def send_message(self, message):
        """Sends a message to the Gemini model and returns the response."""
        if not self.chat_session:
            handle_error("Chat session not initialized. Please set API key first.")
            return None

        try:
            response = self.chat_session.send_message(message)
            return response.text
        except Exception as e:
            handle_error(f"Failed to send message: {e}")
            return None