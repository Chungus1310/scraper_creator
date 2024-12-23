import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

# URLs for HTTP proxy lists
PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/blob/master/proxy-list-raw.txt"
]

# Test URL to check proxy functionality
TEST_URL = "http://httpbin.org/ip"

# Timeout and retry settings
TIMEOUT = 0.5  # 0.5 seconds
MAX_RETRIES = 5  # Retry up to 5 times
RETRY_DELAY = 0.1  # 0.1 seconds delay between retries

def fetch_proxies(url):
    """
    Fetches proxies from a given URL.
    
    Args:
        url (str): The URL to fetch proxies from.
    
    Returns:
        list: A list of proxy addresses.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        proxies = response.text.splitlines()
        return proxies
    except requests.exceptions.RequestException as e:
        print(f"Error fetching proxies from {url}: {e}")
        return []

def test_proxy(proxy, timeout=TIMEOUT, max_retries=MAX_RETRIES):
    """
    Tests if an HTTP proxy is working by making a request to a test URL.
    
    Args:
        proxy (str): The proxy address in the format "ip:port".
        timeout (float): Timeout for the request in seconds. Default is 0.5.
        max_retries (int): Maximum number of retries in case of failure. Default is 5.
    
    Returns:
        bool: True if the proxy works, False otherwise.
    """
    proxy_url = f"http://{proxy}"
    proxy_dict = {
        "http": proxy_url,
        "https": proxy_url
    }
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(TEST_URL, proxies=proxy_dict, timeout=timeout)
            if response.status_code == 200:
                print(f"Proxy {proxy} is working.")
                return True
            else:
                print(f"Proxy {proxy} failed with status code {response.status_code}.")
                retries += 1
        except requests.exceptions.ConnectTimeout:
            print(f"Proxy {proxy} timed out during connection.")
            retries += 1
        except requests.exceptions.ReadTimeout:
            print(f"Proxy {proxy} timed out during read.")
            retries += 1
        except requests.exceptions.ProxyError as e:
            print(f"Proxy {proxy} failed with proxy error: {e}")
            retries += 1
        except requests.exceptions.RequestException as e:
            print(f"Proxy {proxy} failed with error: {e}")
            retries += 1
        time.sleep(RETRY_DELAY)  # Small delay between retries

    print(f"Proxy {proxy} failed after {max_retries} retries.")
    return False

def save_proxies_to_json(proxies, output_path="proxy.json"):
    """
    Saves the list of proxies to a JSON file in the required format.
    
    Args:
        proxies (list): A list of proxy addresses.
        output_path (str): Path to save the JSON file. Default is "proxy.json".
    """
    proxy_data = {"proxies": proxies}
    try:
        with open(output_path, 'w') as json_file:
            json.dump(proxy_data, json_file, indent=4)
        print(f"Proxies saved to '{output_path}' successfully.")
    except Exception as e:
        print(f"Error saving JSON file: {e}")

def main():
    working_proxies = []

    # Fetch and test HTTP proxies from the provided URLs
    for url in PROXY_SOURCES:
        print(f"Fetching proxies from: {url}")
        proxies = fetch_proxies(url)
        if not proxies:
            print(f"No proxies found in {url}")
            continue

        # Use ThreadPoolExecutor to test proxies concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(test_proxy, proxy): proxy for proxy in proxies}
            for future in as_completed(futures):
                proxy = futures[future]
                if future.result():
                    working_proxies.append(f"http://{proxy}")
                    if len(working_proxies) >= 5:
                        break  # Stop after finding 5 working proxies

        if len(working_proxies) >= 5:
            break  # Stop after finding 5 working proxies

    # Save the working proxies to a JSON file
    if working_proxies:
        save_proxies_to_json(working_proxies[:5])  # Save only the first 5 working proxies
    else:
        print("No working proxies found.")

if __name__ == "__main__":
    main()