from urllib.parse import urljoin

import requests
from lxml import html

from config import HEADERS, REQUEST_TIMEOUT


def download(url):
    """
    Letölti az oldalt és visszaad egy lxml fát.
    """

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )

    r.raise_for_status()

    return html.fromstring(r.text)


def first(node, xpath):
    """
    Első XPath találat.
    """

    result = node.xpath(xpath)

    if result:
        return result[0]

    return None


def text(node, xpath):
    """
    Szöveg XPath alapján.
    """

    value = first(node, xpath)

    if value is None:
        return ""

    return str(value).strip()


def absolute(base, url):
    if not url:
        return None

    return urljoin(base, url)
