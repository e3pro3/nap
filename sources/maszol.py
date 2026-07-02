
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone

from config import (
    BASE_URL,
    HEADERS,
    REQUEST_TIMEOUT,
    SCAN_LIMIT,
)


def download(url):
    """
    Oldal letöltése.
    """

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )

    r.raise_for_status()

    return BeautifulSoup(r.text, "lxml")


def get_meta(soup, name=None, property=None):
    """
    Meta tag tartalmának kiolvasása.
    """

    if property:
        tag = soup.find("meta", property=property)

        if tag:
            return tag.get("content", "").strip()

    if name:
        tag = soup.find("meta", attrs={"name": name})

        if tag:
            return tag.get("content", "").strip()

    return ""


def parse_homepage():
    """
    Maszol főoldal feldolgozása.
    """

    soup = download(BASE_URL)

    articles = []

    scanned = 0

    for article in soup.find_all("article"):

        if scanned >= SCAN_LIMIT:
            break

        scanned += 1

        a = article.find("a", href=True)

        if not a:
            continue

        link = urljoin(
            BASE_URL,
            a["href"],
        )

        title = a.get_text(
            " ",
            strip=True,
        )

        if not title:

            h = article.find(
                ["h1", "h2", "h3"]
            )

            if h:
                title = h.get_text(
                    " ",
                    strip=True,
                )

        if not title:
            continue

        articles.append(
            {
                "title": title,
                "link": link,
            }
        )

    return articles

def scrape_article(url):
    """
    Egy cikk részletes adatainak letöltése.
    """

    try:
        soup = download(url)
    except Exception:
        return None

    # ---------- Cím ----------

    title = get_meta(soup, property="og:title")

    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(" ", strip=True)

    # ---------- Leírás ----------

    description = get_meta(
        soup,
        property="og:description"
    )

    if not description:
        p = soup.find("p")
        if p:
            description = p.get_text(" ", strip=True)

    # ---------- Kép ----------

    image = get_meta(
        soup,
        property="og:image"
    )

    if image:
        image = urljoin(BASE_URL, image)

    # ---------- Kategória ----------

    category = get_meta(
        soup,
        property="article:section"
    )

    # ---------- Szerző ----------

    author = (
        get_meta(soup, name="author")
        or get_meta(soup, property="article:author")
    )

    # ---------- Publikálási dátum ----------

    published = (
        get_meta(
            soup,
            property="article:published_time"
        )
    )

    if not published:

        time_tag = soup.find("time")

        if (
            time_tag
            and time_tag.has_attr("datetime")
        ):
            published = time_tag["datetime"]

    if not published:

        published = (
            datetime.now(timezone.utc)
            .isoformat()
        )

    # ---------- Visszatérés ----------

    return {

        "title": title,

        "link": url,

        "description": description,

        "image": image,

        "category": category,

        "author": author,

        "published": published,

    }

from cache import (
    load_articles,
    merge_articles,
    filter_old_articles,
    save_articles,
    get_known_links,
)


def collect_new_articles():
    """
    Csak az új cikkeket tölti le.
    """

    print("Cache betöltése...")

    old_articles = load_articles()

    known_links = get_known_links(old_articles)

    print(f"Cache: {len(old_articles)} cikk")

    homepage_articles = parse_homepage()

    print(f"Főoldalon: {len(homepage_articles)} cikk")

    new_articles = []

    skipped = 0

    for article in homepage_articles:

        if article["link"] in known_links:
            skipped += 1
            continue

        print("Új:", article["title"])

        data = scrape_article(article["link"])

        if data:
            new_articles.append(data)

    print(f"Új cikkek: {len(new_articles)}")
    print(f"Kihagyva: {skipped}")

    articles = merge_articles(
        old_articles,
        new_articles,
    )

    articles = filter_old_articles(
        articles,
    )

    save_articles(
        articles,
    )

    print(f"Cache mentve ({len(articles)} cikk)")

    return articles
