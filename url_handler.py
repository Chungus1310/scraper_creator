import requests
import json
from utils import handle_error

class URLHandler:
    def __init__(self):
        self.urls = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://alphacoders.com/',
            'DNT': '1',
            'Connection': 'keep-alive'
        })
        self.proxies = self.load_proxies()

    def load_proxies(self):
        try:
            with open('proxy.json', 'r') as f:
                proxies_data = json.load(f)
                return proxies_data.get('proxies', [])
        except FileNotFoundError:
            print("Proxy file not found.")
            return []
        except json.JSONDecodeError:
            print("Error decoding proxy JSON file.")
            return []

    def add_url(self, url):
        """Adds a URL to the list of URLs."""
        self.urls.append(url)

    def validate_urls(self):
        """Validates the URLs by checking for valid format and accessibility."""
        if not self.urls:
            handle_error("No URLs provided")
            return False

        validated_urls = []
        for url in self.urls:
            try:
                response = self.session.head(url, timeout=10)
                if response.status_code in [200, 301, 302]:
                    validated_urls.append(url)
                elif response.status_code == 403:
                    if not self.proxies:
                        handle_error("No proxies available to try.")
                        return False
                    for proxy in self.proxies:
                        try:
                            print(f"Trying proxy: {proxy}")
                            proxy_dict = {'http': proxy, 'https': proxy}
                            response = self.session.get(url, proxies=proxy_dict, timeout=10)
                            if response.status_code == 200:
                                print(f"Proxy {proxy} succeeded.")
                                validated_urls.append(url)
                                break
                            elif response.status_code == 403:
                                print(f"Proxy {proxy} received 403.")
                                continue
                        except requests.exceptions.RequestException as e:
                            print(f"Proxy {proxy} failed with error: {e}")
                            continue
                    if url not in validated_urls:
                        handle_error(f"All proxies failed to access {url}.")
                else:
                    handle_error(f"URL validation failed for {url}: Status code {response.status_code}")
            except requests.exceptions.RequestException as e:
                handle_error(f"URL validation failed for {url}: {str(e)}")
                continue

        self.urls = validated_urls
        return len(validated_urls) > 0