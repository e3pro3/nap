from email.utils import format_datetime
from datetime import datetime, timezone

from lxml import etree

from config import (
    BASE_URL,
    FEED_TITLE,
    FEED_DESCRIPTION,
    FEED_LANGUAGE,
    RSS_FILE,
    MEDIA_NS,
    ATOM_NS,
)


def cdata(parent, tag, text):
    """
    CDATA elem létrehozása.
    """

    el = etree.SubElement(parent, tag)
    el.text = etree.CDATA(text or "")
    return el


def text(parent, tag, value):
    """
    Egyszerű XML elem.
    """

    el = etree.SubElement(parent, tag)
    el.text = value or ""
    return el

def create_feed():

    nsmap = {
        "atom": ATOM_NS,
        "media": MEDIA_NS,
    }

    rss = etree.Element(
        "rss",
        version="2.0",
        nsmap=nsmap,
    )

    channel = etree.SubElement(
        rss,
        "channel",
    )

    text(channel, "title", FEED_TITLE)

    text(channel, "link", BASE_URL)

    text(
        channel,
        "description",
        FEED_DESCRIPTION,
    )

    text(
        channel,
        "language",
        FEED_LANGUAGE,
    )

    text(
        channel,
        "generator",
        "Maszol RSS Generator v2",
    )

    text(
        channel,
        "lastBuildDate",
        format_datetime(
            datetime.now(timezone.utc)
        ),
    )

    atom = etree.SubElement(
        channel,
        "{%s}link" % ATOM_NS,
    )

    atom.set("href", BASE_URL)

    atom.set("rel", "self")

    atom.set(
        "type",
        "application/rss+xml",
    )

    return rss, channel

def add_article(channel, article):
    """
    Egy RSS <item> létrehozása.
    """

    item = etree.SubElement(channel, "item")

    # ----- Kötelező mezők -----

    text(item, "title", article.get("title", ""))

    text(item, "link", article.get("link", ""))

    text(item, "guid", article.get("link", ""))

    # ----- Leírás -----

    description = article.get("description", "")

    image = article.get("image")

    if image:
        html = f"""
        <p>
            <img src="{image}" alt="" />
        </p>
        <p>{description}</p>
        """
    else:
        html = f"<p>{description}</p>"

    cdata(
        item,
        "description",
        html.strip(),
    )

    # ----- Publikálási dátum -----

    published = article.get("published")

    if published:
        try:

            dt = datetime.fromisoformat(published)

            if dt.tzinfo is None:
                dt = dt.replace(
                    tzinfo=timezone.utc
                )

            text(
                item,
                "pubDate",
                format_datetime(dt),
            )

        except Exception:
            pass

    # ----- Kategória -----

    category = article.get("category")

    if category:
        text(
            item,
            "category",
            category,
        )

    # ----- Szerző -----

    author = article.get("author")

    if author:
        text(
            item,
            "author",
            author,
        )

    # ----- Kép (media namespace) -----

    if image:

        media = etree.SubElement(
            item,
            "{%s}content" % MEDIA_NS,
        )

        media.set("url", image)

        media.set("medium", "image")

    # ----- Enclosure -----

    if image:

        enclosure = etree.SubElement(
            item,
            "enclosure",
        )

        enclosure.set(
            "url",
            image,
        )

        enclosure.set(
            "type",
            "image/jpeg",
        )

        enclosure.set(
            "length",
            "0",
        )

      def save_feed(rss):
    """
    XML mentése.
    """

    tree = etree.ElementTree(rss)

    tree.write(
        str(RSS_FILE),
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=True,
    )

  def build_feed(articles):

    rss, channel = create_feed()

    for article in articles:
        add_article(
            channel,
            article,
        )

    save_feed(rss)

  
