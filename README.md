# 🐈 Kitten Scraper: Your Personal Web Scraping Buddy! 🎉

Hey there, fellow code adventurer! 👋 Welcome to the land of Kitten Scraper, This project is your one-stop shop for all things scraping, built with the power of Google's Gemini AI and a whole lot of love. ❤️

## What's in the Box? 🎁

Kitten Scraper is more than just a tool; it's a magical journey into the world of data extraction. Here's what makes it special:

-   **Gemini AI-Powered:** We've got Google's Gemini AI doing the heavy lifting. It analyzes HTML like a pro and even generates the scraping code for you! 🤯
-   **GUI Goodness:** No scary command lines here! Our user-friendly interface (built with `ttkbootstrap` and `customtkinter`) makes scraping a breeze, even if you're new to the game.
-   **Proxy Power:**  Kitten Scraper is smart about proxies. It automatically fetches and uses them if needed, so you can scrape without getting blocked. 🚫
-   **Word Doc Magic:**  Your scraped data gets beautifully formatted into a Word document, ready for you to admire. 📄✨
-   **Error Handling Hero:**  We've got your back! Kitten Scraper is designed to handle errors gracefully and give you helpful messages if things go wrong.

## How to Play with the Kitten 🐾

1. **Get Your API Key:** You'll need a Google Gemini API key to get started.
2. **Enter Your URLs:** Tell the Kitten which websites you want to explore.
3. **Describe Your Target:** Explain what data you're looking for (e.g., "all the cat pictures," "all youtube videos about cats").
4. **Hit "Start Scraping":**  Let the magic happen! The Kitten will fetch the HTML, analyze it with Gemini, generate Python code, and execute it to get your data.
5. **Enjoy Your Results:**  Your scraped data will be neatly organized in a Word document, waiting for you in the `output.docx` file.

## Files Explained: A Quick Tour 🗺️

-   **`api_handler.py`:**  Handles all the nitty-gritty details of talking to the Gemini API.
-   **`code_executor.py`:**  Takes the code generated by Gemini and runs it like a boss.
-   **`config.py`:**  Holds all the important settings and prompts for the AI.
-   **`gemini_api_handler.py`:** Manages the Gemini API calls, including timeouts, because even AI needs a break sometimes.
-   **`generate_proxy_json.py`:** This is our proxy fetching friend!
-   **`html_fetcher.py`:**  Fetches the HTML content from the websites you specify.
-   **`main.py`:**  The heart of the application, where the GUI and all the other components come together.
-   **`output_formatter.py`:**  Turns your scraped data into a beautiful Word document.
-   **`proxy.json`:** Stores the list of working proxies.
-   **`requirements.txt`:**  Lists all the Python packages you need to install.
-   **`save_to_word.py`:** Contains helper functions to format the output doc.
-   **`scraper.py`:** The python file generated by the AI, that does the scraping.
-   **`target_parser.py`:**  Handles the target description you provide.
-   **`url_handler.py`:**  Makes sure the URLs you enter are valid.
-   **`utils.py`:**  Contains some handy utility functions, like error handling and making web requests.

## Installation: Let's Get This Party Started! 🥳

1. Clone this repository:
    ```bash
    git clone https://github.com/Chungus1310/scraper_creator
    ```
2. Navigate to the project directory:
    ```bash
    cd scraper_creator
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
4. Get some proxies!
    ```bash
    python generate_proxy_json.py
    ```
5. Run the app:
    ```bash
    python main.py
    ```

## Need Help? 🤔

If you run into any trouble or have questions, feel free to open an issue on GitHub. We're always happy to help a fellow scraper enthusiast!

## Disclaimer 🚨

Web scraping is a powerful tool, but it's important to use it responsibly and ethically. Always respect the website's `robots.txt` file and terms of service. Happy scraping, and remember to be kind to the internet!

## Let's Scrape the Web Together! 🚀

Kitten Scraper is an open-source project, and we welcome contributions from the community. If you have ideas for improvements or want to help us make the Kitten even more awesome, feel free to submit a pull request.

Now go forth and scrape some data! 🐱💻
