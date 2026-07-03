from urllib.parse import urljoin

import requests
from lxml import html

from config import HEADERS, REQUEST_TIMEOUT


def download(url):
    """
    Letölt egy oldalt és lxml HTML fát ad vissza.
    """

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    return html.fromstring(response.text)


def first(node, xpath):
    """
    Az első XPath találat.
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

    if hasattr(value, "text_content"):
        return value.text_content().strip()

    return str(value).strip()


def attr(node, xpath):
    """
    Attribútum XPath alapján.
    """

    value = first(node, xpath)

    if value is None:
        return None

    return str(value).strip()


def absolute(base_url, url):
    """
    Relatív URL -> abszolút URL.
    """

    if not url:
        return None

    return urljoin(base_url, url)
