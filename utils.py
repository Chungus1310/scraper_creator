import re
import logging
import requests
from typing import Optional, Dict

# Configure logging
logging.basicConfig(
    filename='web_scraper.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_proxies() -> Dict[str, str]:
    """
    Returns proxy configuration. Can be extended to load from config file.
    """
    return {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080'
    }

def make_request(url: str, use_proxy: bool = False, timeout: int = 10) -> Optional[requests.Response]:
    """
    Makes an HTTP request with optional proxy support.
    
    Args:
        url (str): The URL to request
        use_proxy (bool): Whether to use proxy
        timeout (int): Request timeout in seconds
        
    Returns:
        Optional[requests.Response]: Response object if successful, None otherwise
    """
    try:
        proxies = get_proxies() if use_proxy else None
        response = requests.get(url, proxies=proxies, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        handle_error(f"Request failed: {str(e)}")
        return None


def handle_error(error_message):
    """Logs an error message and displays it to the user.

    Args:
        error_message (str): The error message to log and display.
    """
    logging.error(error_message)
    print(f"Error: {error_message}")  # Placeholder for GUI error display

def extract_python_code(response_text):
    """Extracts Python code from a response that might contain markdown.
    
    Args:
        response_text (str): The text containing potential Python code blocks
        
    Returns:
        str: The extracted Python code with markdown formatting removed
    """
    # Try to find code between ```python and ``` markers
    python_blocks = re.findall(r'```python\s*(.*?)\s*```', response_text, re.DOTALL)
    
    if python_blocks:
        # Return the first Python code block found
        return python_blocks[0].strip()
    
    # Try to find code between just ``` markers
    code_blocks = re.findall(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
    if code_blocks:
        # Return the first code block found
        return code_blocks[0].strip()
    
    # If no code blocks found, return the original text
    # Remove any markdown-style formatting
    cleaned_text = re.sub(r'#\s+', '# ', response_text)  # Fix header formatting
    cleaned_text = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned_text)  # Remove bold
    cleaned_text = re.sub(r'\*(.*?)\*', r'\1', cleaned_text)  # Remove italic
    
    return cleaned_text.strip()