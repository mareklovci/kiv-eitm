import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from collections import deque
from urllib import request as req


def get_urls(soup: BeautifulSoup, current_url: str) -> str:
    """Return all link on the page
    :param soup: HTML Soup object
    :param current_url: When href contains relative URL, we would have problem, therefore we need referential domain
    :return: All page URLs
    """
    url_pattern = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'
    for link in soup.find_all('a'):
        href = link.get('href')
        if href is None:
            continue
        if re.match(url_pattern, href):
            yield href
        else:
            joined_url = urljoin(current_url, href)
            yield joined_url


def scrap_text(soup: BeautifulSoup):
    """Returns string from bs4 placed in <p> tag"""

    # Vrácení prázdného stringu v případě soup.body = None
    if not soup.body:
        return ''

    if not soup.body.find('p'):
        return ''

    for string in soup.body.find('p').next_elements:
        string = str(string)
        if re.match(r'<[^>]*>', string):
            continue
        if re.match(r'\s', string):  # deletes 'standalone' whitespaces and other blank characters
            continue
        else:
            yield string


def make_title(soup: BeautifulSoup) -> str:
    """
    :param soup: HTML předzpracované balíčkem beautifulsoup - soup object
    :return: title stránky
    """
    # v případě nenalezení head nebo head.text
    if not soup.head or not soup.head.title:
        return ''
    return soup.head.title.text


def process_text(soup: BeautifulSoup):
    scrap = list(scrap_text(soup))  # List of strings from <p> tags
    text1 = ' '.join(scrap)
    text2 = re.sub(r'\s+', ' ', text1)
    return text2


def process_urls(soup: BeautifulSoup, current_url: str):
    urls = get_urls(soup, current_url)
    urls = filter(lambda x: not re.match(r'^(.*?)\.pdf', x), urls)  # filter pdf files
    urls = filter(lambda x: 'facebook' not in x, urls)
    urls = filter(lambda x: 'youtube' not in x, urls)
    urls = set(urls)
    return urls


def process_html(html, current_url: str):
    """Processes HTML code.
    Separates urls, title and actual content. Serves as a "one call for all" function.
    :param html: html to process
    :param current_url:
    :return: urls, title, text
    """
    soup = BeautifulSoup(html, 'html5lib')
    urls = process_urls(soup, current_url)
    title = make_title(soup)
    text = process_text(soup)
    return urls, title, text


def main():
    pass


if __name__ == '__main__':
    main()
