from datetime import datetime, timezone
from email.utils import format_datetime

from lxml import etree

from config import (
    FEED_URL,
    FEED_TITLE,
    FEED_DESCRIPTION,
    FEED_LANGUAGE,
    RSS_FILE,
    MEDIA_NS,
    ATOM_NS,
)

from sources.base import mime_type


NSMAP = {
    "media": MEDIA_NS,
    "atom": ATOM_NS,
}


def text(parent, tag, value):
    element = etree.SubElement(parent, tag)
    element.text = value
    return element


def cdata(parent, tag, value):
    element = etree.SubElement(parent, tag)
    element.text = etree.CDATA(value)
    return element


def create_feed():

    rss = etree.Element(
        "rss",
        version="2.0",
        nsmap=NSMAP,
    )

    channel = etree.SubElement(rss, "channel")

    text(channel, "title", FEED_TITLE)
    text(channel, "link", FEED_URL)
    text(channel, "description", FEED_DESCRIPTION)
    text(channel, "language", FEED_LANGUAGE)
    
    text(
         channel,
         "lastBuildDate",
         format_datetime(datetime.now(timezone.utc)),
    )

    text(
         channel,
         "generator",
         "NAP RSS Generator v1.0",
    )
    
    atom = etree.SubElement(
        channel,
        "{%s}link" % ATOM_NS,
    )

    atom.set("href", FEED_URL)
    atom.set("rel", "self")
    atom.set("type", "application/rss+xml")

    return rss, channel


def add_article(channel, article):

    item = etree.SubElement(channel, "item")

    text(item, "title", article["title"])
    text(item, "link", article["link"])
    
    guid = text(
        item,
        "guid",
        article["link"],
    )

    guid.set(
        "isPermaLink",
        "true",
    )

    description = article.get(
        "description",
        article["title"],
    )

    image = article.get("image")

    if image:

        html = (
            f'<img src="{image}" /><br/>'
            f'{description}'
        )

    else:

        html = description

    cdata(
        item,
        "description",
        html,
    )

    published = article.get("published")

    if published:

        dt = datetime.fromisoformat(
            published
        )

        if dt.tzinfo is None:
            dt = dt.replace(
                tzinfo=timezone.utc
            )

        text(
            item,
            "pubDate",
            format_datetime(dt),
        )

    category = article.get("category")

    if category:
        text(item, "category", category)

    author = article.get("author")

    if author:
        text(item, "author", author)

    if image:

        media = etree.SubElement(
            item,
            "{%s}content" % MEDIA_NS,
        )

        media.set("url", image)
        media.set("medium", "image")

        enclosure = etree.SubElement(
            item,
            "enclosure",
        )

        enclosure.set("url", image)
        enclosure.set(
            "type",
            mime_type(image),
        )
        enclosure.set(
            "length",
            "0",
        )


def build_feed(articles):

    rss, channel = create_feed()

    for article in articles:
        add_article(
            channel,
            article,
        )

    tree = etree.ElementTree(rss)

    tree.write(
        str(RSS_FILE),
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=True,
    )
    
