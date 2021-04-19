import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from collections import deque
from urllib import request as req
from app import Website, db

# Inicializace setu s již uloženými URLS
# - pro zamezení ukládání křížových odkazů
saved_urls = set()

# Inicializace fronty URLS ke zpracování
urls_to_process = deque()

# Proměnné řešící logiku hloubky
urls_per_level = 1
counted_urls = 0

# Hloubka samotná
depth = 0

prefix = 0


def read_website(url: str) -> str:
    try:
        fr = req.urlopen(url)
        text = fr.read()
        fr.close()
    except Exception as err:
        print('Error:', err)
        text = ''

    return text


def get_urls(soup: BeautifulSoup, current_url: str) -> str:
    """Vrátí odkazy nacházející se na stránce
    :param soup: HTML předzpracované balíčkem beautifulsoup - soup object
    :param current_url: současné url pro relativní odkazy
    :return: url získané ze soup
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


def scrap_text(soup):
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


def make_title(soup) -> str:
    """
    :param soup: HTML předzpracované balíčkem beautifulsoup - soup object
    :return: title stránky
    """
    # v případě nenalezení head nebo head.text
    if not soup.head or not soup.head.title:
        return ''
    return soup.head.title.text


def process_text(soup):
    scrap = list(scrap_text(soup))  # List of strings from <p> tags
    text1 = ' '.join(scrap)
    text2 = re.sub(r'\s+', ' ', text1)
    return text2


def process_urls(soup, current_url):
    urls = get_urls(soup, current_url)
    urls = filter(lambda x: not re.match(r'^(.*?)\.pdf', x), urls)  # filter pdf files
    urls = filter(lambda x: 'facebook' not in x, urls)
    urls = filter(lambda x: 'youtube' not in x, urls)
    urls = set(urls)
    return urls


def process_html(html: str, current_url):
    """Processes HTML code.
    Separates urls, title and actual content. Serves as a "one call for all" function.
    :param html: html to process
    :param current_url:
    :return: urls, title, text
    """
    soup = BeautifulSoup(html, 'html.parser')
    urls = process_urls(soup, current_url)
    title = make_title(soup)
    if not title:
        return '', '', ''
    text = process_text(soup)
    return urls, title, text


def make_safe_filename(text, chars_to_discard=('\r', '\t', '\n', '!', ':', '\'', '\"', '*', '.', ',', '|', '?', '/',
                                               '\\', '<', '>')):
    """Odstraní nebezpečné znaky u titlu - aby šel uložit soubor"""
    for char in chars_to_discard:
        text = text.replace(char, '')
    return text[:30]


def _get_path(folder: str = 'storage') -> str:
    """Returns path to chosen folder.
    Used for getting path to storage folder -> '../storage/'
    :param folder: path you want to use
    :return: path to folder
    """
    # there is a difference between PyCharm and shell in path tracing, this ensures compatibility
    path = '../' + folder + '/'
    if not os.path.exists(path):
        path = './' + folder + '/'
    return path


def skip_page():
    """Skips page which is not possible to process"""
    global depth, urls_per_level, counted_urls, urls_to_process, saved_urls
    urls_per_level -= 1
    if urls_per_level < 1:
        urls_per_level = counted_urls
        counted_urls = 0
        depth += 1


def main(start_url: str = 'https://cs.wikipedia.org/wiki/Wikipedie:%C4%8Cl%C3%A1nek_t%C3%BDdne', max_depth: int = 2):
    # Inicializace globálních proměnných
    global depth, urls_per_level, counted_urls, urls_to_process, saved_urls
    saved_urls.add(start_url)
    urls_to_process.append(start_url)

    # Cyklus zpracovávající po sobě řazené URLS ve frontě
    while depth < max_depth:
        if not urls_to_process:
            return

        # URL ke zpracování
        url_to_read = urls_to_process.popleft()

        # HTML ke zpracování
        html = read_website(url_to_read)

        # Pokud se nepodařilo načíst HTML, přeskočí další zpracování
        if not html:
            skip_page()
            continue

        # Zpracování HTML
        urls, title, text = process_html(html, url_to_read)

        # Výpis do konzole
        # - pro každou zpracovávanou stránku je vypsán její název pro vizualizaci běhu programu
        print('Zpracování stránky {}'.format(str(title)))

        # Pokud se nepodařilo zpracovat HTML, přeskočí další zpracování
        if not title:
            skip_page()
            continue

        # Save to DB
        new_website = Website(title=title, content=text, url=url_to_read)
        db.session.add(new_website)
        db.session.commit()

        # Uložení zpracovaného URL do setu již zpracovaných
        saved_urls.add(url_to_read)

        # Přidání všech doposud neuložených URLS do fronty k zpracování
        for url in urls:
            if url not in saved_urls:
                urls_to_process.append(url)
                counted_urls += 1

        # Logika hloubky
        urls_per_level -= 1
        if urls_per_level < 1:
            urls_per_level = counted_urls
            counted_urls = 0
            depth += 1


if __name__ == '__main__':
    main()
