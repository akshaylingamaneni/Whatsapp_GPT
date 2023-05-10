import requests
from bs4 import BeautifulSoup


class WebScraper:
    def __init__(self, url):
        self.url = url

    def extract_text(self):
        # Make a request to the website
        response = requests.get(self.url)

        # Parse the HTML content with Beautiful Soup
        soup = BeautifulSoup(response.text, "html.parser")

        # Find and remove header tags
        header = soup.find("header")
        if header:
            header.decompose()

        # Find and remove footer tags
        footer = soup.find("footer")
        if footer:
            footer.decompose()

        # Find the main content tags
        main_content = soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"])

        # Extract the text from the main content tags
        text = ""
        for tag in main_content:
            text += tag.get_text()

        # Remove any unwanted characters
        text = text.replace("\n", "").strip()

        # Return the extracted text

        return text


# webscrapper = WebScraper("https://www.w3schools.com/python/python_classes.asp")
# print(webscrapper.extract_text())