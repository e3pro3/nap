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
    Megpróbálja minden lehetséges helyről kinyerni a képet.
    """

    xpaths = (
        ".//img/@src",
        ".//img/@data-src",
        ".//img/@data-original",
        ".//img/@data-lazy-src",
        ".//img/@data-srcset",
        ".//img/@srcset",
        ".//source/@srcset",
    )

    for xpath in xpaths:

        value = attr(article, xpath)

        if not value:
            continue

        # srcset esetén az első URL kell
        if "," in value:
            value = value.split(",")[0]

        value = value.split()[0]

        return absolute(BASE_URL, value)

    return None


def fetch_article_image(url):
    """
    A cikkoldalról próbálja megszerezni a borítóképet.
    """

    try:
        tree = download(url)

        xpaths = (
            '//meta[@property="og:image"]/@content',
            '//meta[@property="og:image:secure_url"]/@content',
            '//meta[@name="twitter:image"]/@content',
            '//meta[@name="twitter:image:src"]/@content',
            '//link[@rel="image_src"]/@href',
        )

        for xpath in xpaths:
            image = attr(tree, xpath)

            if image:
                print(f"✔ Meta kép: {image}")
                return image.strip()

        print("⚠ Nem találtam meta képet:", url)

    except Exception as e:
        print(e)

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

        if not image:
            print(f"Listaoldalon nincs kép:")

            print(link)

            image = fetch_article_image(link)

            if image:
                print("✔ Kép megvan a cikkoldalon")
            else:
                print("✖ A cikkoldalon sincs kép")

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

    for article in new_articles:
        if article["image"]:
            print("KÉP:", article["image"])
        else:
            print("NINCS KÉP:", article["link"])

    articles = update_cache(
        CACHE_FILE,
        new_articles,
    )

    for article in articles:
        if article.get("image"):
            print("KÉP:", article["link"])
        else:
            print("NINCS KÉP:", article["link"])

    print(f"Cache mentve ({len(articles)} cikk)")

    return articles

def debug_article(url):
    """
    Egy cikk képének tesztelése.
    """

    print("=" * 60)
    print(url)
    print("=" * 60)

    image = fetch_article_image(url)

    if image:
        print("KÉP:")
        print(image)
    else:
        print("NINCS KÉP")
