from datetime import datetime, timezone

from config import (
    BASE_URL,
    CACHE_FILE,
    SCAN_LIMIT,
)

from cache import (
    load_articles,
    get_known_links,
    update_cache,
)

from sources.base import (
    download,
    text,
    attr,
    absolute,
)


# ----------------------------------------------------
# Segédfüggvények
# ----------------------------------------------------

def article_link(article):
    """
    Cikk URL.
    """

    link = attr(
        article,
        ".//a/@href",
    )

    return absolute(
        BASE_URL,
        link,
    )


def article_title(article):
    """
    Cikk címe.
    """

    for xpath in (
        ".//h1",
        ".//h2",
        ".//h3",
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
    """
    Rövid leírás.
    """

    description = text(
        article,
        ".//p",
    )

    return description


def article_image(article):
    """
    Cikk képe.
    """

    for xpath in (
        ".//img/@src",
        ".//img/@data-src",
        ".//img/@data-original",
    ):

        image = attr(
            article,
            xpath,
        )

        if image:
            return absolute(
                BASE_URL,
                image,
            )

    return None


def article_category(article):
    """
    Kategória.
    """

    return ""


def article_author(article):
    """
    Szerző.
    """

    return ""


def article_date(article):
    """
    Megpróbálja kiolvasni a cikk dátumát.
    """

    value = attr(article, ".//time/@datetime")

    if value:
        return value

    return datetime.now(timezone.utc).isoformat()

def collect_new_articles():
    """
    Letölti a Maszol főoldalát, kigyűjti az új cikkeket,
    frissíti a cache-t és visszaadja a teljes listát.
    """

    print("Maszol letöltése...")

    tree = download(BASE_URL)

    old_articles = load_articles(CACHE_FILE)
    known_links = get_known_links(old_articles)

    new_articles = []

    scanned = 0

    forbidden = (
        "/velemeny/",
        "/podcast/",
        "/konyvsarok/",
        "/recept/",
    )

    for article in tree.xpath("//article"):

        if scanned >= SCAN_LIMIT:
            break

        scanned += 1

        link = article_link(article)

        if not link:
            continue

        if link in known_links:
            continue

        if any(x in link.lower() for x in forbidden):
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

    print(f"Cache mentve ({len(articles)} cikk)")

    return articles
