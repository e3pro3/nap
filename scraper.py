import os
import json
import email.utils
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
from datetime import datetime, timezone, timedelta

BASE_URL = "https://maszol.ro"
RSS_FILE = "maszol.xml"
DATA_FILE = "data/articles.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

DAYS_BACK = 5
MAX_ARTICLES = 40  # Érdemes kicsit megemelni, hogy több hír férjen el
SCAN_LIMIT = 60

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

def extract_image(article):
    img = article.find("img")
    if not img:
        return None
    image = img.get("src") or img.get("data-src") or img.get("data-original")
    if image:
        return urljoin(BASE_URL, image)
    return None

def scrape():
    html = requests.get(BASE_URL, headers=HEADERS, timeout=20).text
    soup = BeautifulSoup(html, "lxml")

    old_articles = load_articles()
    known_links = {a["link"] for a in old_articles if "link" in a}

    new_articles = []
    scanned = 0
    most_idopont = datetime.now(timezone.utc)

    # Csak azokat a kategóriákat engedjük át, amik nem fixen rögzített archív blokkok
    tiltott_szekciok = ["/velemeny/", "/podcast/", "/konyvsarok/", "/recept/"]

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

        if any(tiltott in link.lower() for tiltott in tiltott_szekciok):
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

        new_articles.append({
            "title": title,
            "link": link,
            "description": description,
            "image": image,
            "date": most_idopont.isoformat()
        })

    # Összegyűjtjük a régieket és az újakat
    all_articles = new_articles + old_articles

    # 🔥 5 NAPOS IDŐSZŰRÉS: Kidobjuk a túl régi adatokat az adatbázisból
    friss_articles = []
    for item in all_articles:
        try:
            cikk_datuma = datetime.fromisoformat(item["date"])
            # Ha a cikk fiatalabb, mint 5 nap, megtartjuk
            if (most_idopont - cikk_datuma) < timedelta(days=DAYS_BACK):
                friss_articles.append(item)
        except:
            pass

    # Biztonsági mentés: ha túl üres a szűrő, a legfrissebb 10-et mindenképp hagyjuk meg
    if len(friss_articles) < 10:
        friss_articles = all_articles[:10]
    else:
        friss_articles = friss_articles[:200]

    save_articles(friss_articles)

    # XML GENERÁLÁS a megtartott friss cikkekből
    fg = FeedGenerator()
    fg.id(BASE_URL)
    fg.title("Maszol.ro - Friss hírek")
    fg.link(href=BASE_URL, rel="alternate")
    fg.language("hu")
    fg.description("Automatikusan frissülő Maszol RSS feed")

    for item in friss_articles[:MAX_ARTICLES]:
        entry = fg.add_entry()
        entry.id(item["link"])
        entry.title(item["title"])
        entry.link(href=item["link"])
        
        desc = item.get("description", item["title"])
        if item["image"]:
            desc = f'<img src="{item["image"]}" style="max-width:100%;" /><br>{desc}'
        entry.description(desc)

        dt = datetime.fromisoformat(item["date"])
        entry.pubDate(email.utils.format_datetime(dt))

        if item["image"]:
            entry.enclosure(item["image"], "0", "image/jpeg")

    os.makedirs("dist", exist_ok=True)
    fg.rss_file(RSS_FILE, pretty=True)

    print(f"RSS kész. Új cikkek: {len(new_articles)}, Összesen az XML-ben: {len(fg.entry())}")

if __name__ == "__main__":
    scrape()
