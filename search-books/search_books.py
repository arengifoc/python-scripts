#!/usr/bin/env python3
"""
Script that searches for books in www.gutenberg.org
"""
import argparse
import logging
import requests

import bs4


BASE_URL = 'https://www.gutenberg.org'
SEARCH_URL = BASE_URL + '/ebooks/search/?query='

# Configurar logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def search_books(search_url):
    """
    Search for books in www.gutenberg.org

    Args:
        search_url (str): URL to search for books
    """
    try:
        response = requests.get(search_url, timeout=5)
        response.raise_for_status()
        # Verificar la codificación del contenido de la respuesta
        response.encoding = response.apparent_encoding
        # Usar el parser html5lib
        soup = bs4.BeautifulSoup(response.text, 'html5lib')
        books = soup.select('li.booklink')
        if not books:
            logger.warning("No books found for the given keywords.")
        for i, book in enumerate(books, start=1):
            title_tag = book.select_one('span.title')
            title = title_tag.text.strip() if title_tag else 'Unknown'
            author_tag = book.select_one('span.subtitle')
            author = author_tag.text.strip() if author_tag else 'Unknown'
            link_tag = book.select_one('a')
            link = BASE_URL + \
                link_tag['href'].strip() if link_tag else 'Unknown'
            print(f"{i}. {title} by {author} - {link}")
    except requests.exceptions.HTTPError as err:
        logger.error("HTTP error occurred: %s", err)
    except requests.exceptions.RequestException as err:
        logger.error("Error occurred: %s", err)


def main():
    """
    Main function

    Args:
        String: Keywords to search for
    """
    parser = argparse.ArgumentParser(
        description="Search for books in www.gutenberg.org")
    parser.add_argument("keywords", metavar="KEYWORDS",
                        nargs='+', help="Keywords to search for")
    args = parser.parse_args()
    keywords = '+'.join(args.keywords)
    url = SEARCH_URL + keywords
    search_books(url)


if __name__ == "__main__":
    main()
