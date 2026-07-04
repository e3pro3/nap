from datetime import datetime, timezone

from config import (
    BASE_URL,
    CACHE_FILE,
    SCAN_LIMIT,
)

from cache import (
    load_articles,
    save_articles,
    get_known_links,
    update_cache,
)

from sources.base import (
    download,
    text,
    attr,
    absolute,
)

def collect_new_articles():
    """
    Letölti a Hargita Népe főoldalát, kigyűjti az új cikkeket,
    frissíti a cache-t és visszaadja a teljes listát.
    """

    print("Forrás letöltése...")

    tree = download(BASE_URL)

    old_articles = load_articles(CACHE_FILE)
    known_links = get_known_links(old_articles)

    new_articles = []

    scanned = 0

    for article in tree.xpath("//article"):

        if scanned >= SCAN_LIMIT:
            break

        scanned += 1

        link = article_link(article)

        if not link:
            continue

        if link in known_links:
            continue

        title = article_title(article)

        if not title:
            continue

        description = article_description(article)

        if not description:
            description = title

        image = article_image(article)

        new_articles.append(
            {
                "title": title,
                "link": link,
                "description": description,
                "image": image,
                "published": article_date(article),
                "author": article_author(article),
                "category": article_category(article),
            }
        )

        print(f"Új cikkek: {len(new_articles)}")

    articles = update_cache(
        CACHE_FILE,
        new_articles,
    )

    if new_articles:
        print(f"Új cikkek összesen: {len(new_articles)}")

    print(f"Cache mentve ({len(articles)} cikk)")

    return articles
def article_link(article):

    link = attr(
        article,
        ".//a/@href",
    )

    return absolute(
        BASE_URL,
        link,
    )


def article_title(article):

    for xpath in (
        ".//h2",
        ".//h3",
        ".//h5",
        ".//a",
    ):

        title = text(
            article,
            xpath,
        )

        if title:
            return title

    return ""


def article_description(article):
  
def article_image(article):
    """
    Kép URL.
    """

    xpaths = (
        ".//img/@src",
        ".//img/@data-src",
        ".//img/@data-original",
        ".//img/@data-lazy-src",
        ".//img/@srcset",
        ".//source/@srcset",
    )

    for xpath in xpaths:

        value = attr(article, xpath)

        if not value:
            continue

        if "," in value:
            value = value.split(",")[0]

        value = value.split()[0]

        return absolute(
            BASE_URL,
            value,
        )

    return None


def article_category(article):
    """
    Kategória.
    """

    return ""


def article_author(article):
    """
    Forrás.
    """

    return "Hargita Népe"


def article_date(article):
    """
    Dátum.
    """

    value = attr(
        article,
        ".//time/@datetime",
    )

    if value:
        return value

    return datetime.now(
        timezone.utc
    ).isoformat()
  

    return text(
        article,
        ".//p",
    )
