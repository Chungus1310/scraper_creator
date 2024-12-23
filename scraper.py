import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_video_data(url, num_videos=5):
    """
    Extracts video titles, URLs, and thumbnails from a YouTube search results page.

    Args:
        url: The URL of the YouTube search results page.
        num_videos: The number of videos to extract data from.

    Returns:
        A list of dictionaries, where each dictionary represents a video and contains its title, URL, and thumbnail URL.
        Returns an empty list if an error occurs or no videos are found.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')
        video_renderers = soup.select('ytd-video-renderer.style-scope.ytd-item-section-renderer')[:num_videos]

        if not video_renderers:
            logging.warning(f"No video renderers found at {url}")
            return []

        video_data = []
        for renderer in video_renderers:
            try:
                title_element = renderer.select_one('a#video-title')
                title = title_element['title'] if title_element and 'title' in title_element.attrs else None
                
                video_url_path = title_element['href'] if title_element and 'href' in title_element.attrs else None
                video_url = f"https://www.youtube.com{video_url_path}" if video_url_path else None

                thumbnail_element = renderer.select_one('img#img')
                thumbnail_url = thumbnail_element['src'] if thumbnail_element and 'src' in thumbnail_element.attrs else None

                if title and video_url and thumbnail_url:
                  video_data.append({
                      'title': title,
                      'url': video_url,
                      'thumbnail': thumbnail_url
                  })
                else:
                  logging.warning("Missing data for a video element. Skipping.")

            except (AttributeError, TypeError) as e:
                logging.error(f"Error parsing video element: {e}")

        return video_data

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL: {e}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return []