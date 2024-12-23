from utils import handle_error, make_request

class HTMLFetcher:
    def __init__(self, url_handler):
        self.url_handler = url_handler

    def fetch_html(self):
        """Fetches HTML content from the validated URLs with proxy fallback."""
        html_content = {}
        for url in self.url_handler.urls:
            # First try without proxy
            response = make_request(url, use_proxy=False)
            
            # If failed, try with proxy
            if not response:
                handle_error(f"Direct connection failed for {url}, attempting with proxy...")
                response = make_request(url, use_proxy=True)
            
            if response:
                html_content[url] = response.text
            else:
                handle_error(f"Failed to fetch HTML from {url} with both direct and proxy connections")
        
        return html_content