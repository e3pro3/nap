import os
import json
import email.utils
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
from datetime import datetime, timezone, timedelta

BASE_URL = "https://maszol.ro"
RSS_FILE = "dist/maszol.xml"
DATA_FILE = "data/articles.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Maszol RSS Bot/1.0)"
}

DAYS_BACK = 5
MAX_ARTICLES = 20
SCAN_LIMIT = 60


# ----------------------------
# JSON KEZELÉS
# ----------------------------

def load_articles():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_articles(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ----------------------------
# FRISS SZŰRÉS
# ----------------------------

def is_recent(pub_date):
    if not pub_date:
        return False
    return pub_date >= datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)


# ----------------------------
# OLDAL LETÖLTÉS
# ----------------------------

def get_page():
    r = requests.get(BASE_URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text


# ----------------------------
# FEED
# ----------------------------

def create_feed():
    fg = FeedGenerator()
    fg.id(BASE_URL)
    fg.title("Maszol.ro - Friss hírek")
    fg.link(href=BASE_URL, rel="alternate")
    fg.language("hu")
    fg.description("Automatikusan generált Maszol RSS feed")
    return fg


# ----------------------------
# KÉP
# ----------------------------

def extract_image(article):
    img = article.find("img")
    if not img:
        return None

    image = img.get("src") or img.get("data-src") or img.get("data-original")
    if image:
        return urljoin(BASE_URL, image)
    return None


# ----------------------------
# DÁTUM
# ----------------------------

def extract_date(article):
    time_tag = article.find("time")

    if time_tag and time_tag.get("datetime"):
        try:
            return datetime.fromisoformat(
                time_tag["datetime"].replace("Z", "+00:00")
            )
        except:
            return None

    return None


# ----------------------------
# SCRAPE
# ----------------------------

def scrape():

    html = get_page()
    soup = BeautifulSoup(html, "lxml")

    fg = create_feed()

    old_articles = load_articles()
    known_links = {a["link"] for a in old_articles if "link" in a}

    new_articles = []
    scanned = 0

    for article in soup.find_all("article"):

        if scanned >= SCAN_LIMIT:
            break

        scanned += 1

        link_tag = article.find("a")
        if not link_tag:
            continue

        link = link_tag.get("href")
        if not link:
            continue

        link = urljoin(BASE_URL, link)

        if link in known_links:
            continue

        title = link_tag.get_text(" ", strip=True)

        if not title:
            h = article.find(["h1", "h2", "h3"])
            if h:
                title = h.get_text(" ", strip=True)

        if not title:
            continue

        desc_tag = article.find("p")
        description = desc_tag.get_text(" ", strip=True) if desc_tag else title

        image = extract_image(article)
        pub_date = extract_date(article)

        # 🔥 FRISS SZŰRÉS (5 nap)
        if not is_recent(pub_date):
            continue

        if image:
            description = f'<img src="{image}" style="max-width:100%;" /><br>{description}'

        entry = fg.add_entry()
        entry.id(link)
        entry.title(title)
        entry.link(href=link)
        entry.description(description)

        entry.pubDate(
            email.utils.format_datetime(pub_date)
            if pub_date
            else email.utils.format_datetime(datetime.now(timezone.utc))
        )

        if image:
            entry.enclosure(image, "0", "image/jpeg")

        new_articles.append({
            "title": title,
            "link": link,
            "image": image,
            "date": pub_date.isoformat() if pub_date else None
        })

        if len(new_articles) >= MAX_ARTICLES:
            break


    # mentés
    all_articles = (new_articles + old_articles)[:200]
    save_articles(all_articles)

    # RSS
    os.makedirs("dist", exist_ok=True)
    fg.rss_file(RSS_FILE, pretty=True)

    print(f"RSS kész: {RSS_FILE}")
    print(f"Új cikkek: {len(new_articles)}")


if __name__ == "__main__":
    scrape()
