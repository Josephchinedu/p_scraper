import requests
from bs4 import BeautifulSoup
from rest_framework.pagination import PageNumberPagination


class ScraperHelper:
    def __init__(self, url: str, keywords: dict):
        self.url = url
        self.keywords = keywords

    def get_html_content(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def extract_product_info(self):
        html_content = self.get_html_content()

        if html_content is None:
            return None

        soup = BeautifulSoup(html_content, "html.parser")

        # Extract page titles
        title = soup.find("h1").text.strip()

        # Extract links from the page
        links = [link["href"] for link in soup.find_all("a") if link.get("href")]

        product_info_list = []

        for keyword in self.keywords:
            product_names = soup.find_all(
                string=lambda text: keyword.lower() in text.lower()
            )
            product_info_list.append(
                {"keyword": keyword, "product_names": product_names}
            )

        product_info_list.append({"title": title, "links": links})

        return product_info_list




class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100