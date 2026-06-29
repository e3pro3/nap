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
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def load_articles():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_articles(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def scrape():
    old_articles = load_articles()
    known_links = {x.get("link") for x in old_articles}

    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=20)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print(f"Hiba az oldal letöltésekor: {e}")
        return

    soup = BeautifulSoup(html, "lxml")
    new_articles = []
    most_idopont = datetime.now(timezone.utc)

    # Nem releváns és statikus szekciók URL mintái, amiket teljesen ki akarunk zárni
    tiltott_szavak = ["/velemeny/", "/podcast/", "/konyvsarok/", "/recept/"]

    for article in soup.find_all("article"):
        link_tag = article.find("a")
        if not link_tag:
            continue
        link = link_tag.get("href")
        if not link:
            continue
        link = urljoin(BASE_URL, link)

        # Ha a cikk már szerepel az adatbázisban, átugorjuk
        if link in known_links:
            continue

        # Kiszűrjük a véleményeket, könyveket, podcastokat, amik hetekig kint állnak a főoldalon
        if any(szoval in link.lower() for szoval in tiltott_szavak):
            continue

        title = link_tag.get_text(" ", strip=True)
        if not title:
            h = article.find(["h1", "h2", "h3"])
            if h:
                title = h.get_text(" ", strip=True)
        if not title:
            continue

        paragraph = article.find("p")
        description = paragraph.get_text(" ", strip=True) if paragraph else title

        image = None
        img = article.find("img")
        if img:
            image = img.get("src") or img.get("data-src") or img.get("data-original")
            if not image and img.get("srcset"):
                try:
                    image = img["srcset"].split(",")[0].strip().split()[0]
                except Exception:
                    pass
            if image:
                image = urljoin(BASE_URL, image)

        new_articles.append({
            "title": title,
            "link": link,
            "description": description,
            "image": image,
            "date": most_idopont.isoformat()
        })

    # Kombináljuk a meglévő és az új cikkeket
    all_articles = new_articles + old_articles

    # IDŐSZŰRÉS: Szigorúan töröljük a 3 napnál (72 óránál) régebben feldolgozott cikkeket
    friss_articles = []
    for item in all_articles:
        try:
            cikk_datuma = datetime.fromisoformat(item["date"])
            # Csak akkor tartjuk meg, ha a kor különbsége kisebb, mint 3 nap
            if (most_idopont - cikk_datuma) < timedelta(days=3):
                friss_articles.append(item)
        except Exception:
            pass

    # Ha a szűrés után túl üres lenne a feed, a legújabb 8 darabot mindenképp megtartjuk biztonsági hálónak
    if len(friss_articles) < 8:
        friss_articles = all_articles[:8]
    else:
        friss_articles = friss_articles[:100]

    save_articles(friss_articles)

    fg = FeedGenerator()
    fg.id(BASE_URL)
    fg.title("Maszol.ro - Legfrissebb hírek")
    fg.link(href=BASE_URL, rel="alternate")
    fg.description("Automatikusan frissülő Maszol RSS feed")
    fg.language("hu")

    # Csak a kitisztított, friss listát tesszük bele az XML feedbe
    for item in friss_articles:
        entry = fg.add_entry()
        entry.id(item["link"])
        entry.title(item["title"])
        entry.link(href=item["link"])
        
        desc = item["description"]
        if item["image"]:
            desc = f'<img src="{item["image"]}" style="max-width:100%;" /><br>{desc}'
        entry.description(desc)
        
        dt = datetime.fromisoformat(item["date"])
        entry.pubDate(email.utils.format_datetime(dt))
        
        if item["image"]:
            entry.enclosure(item["image"], "0", "image/jpeg")

    os.makedirs("dist", exist_ok=True)
    fg.rss_file(RSS_FILE, pretty=True)
    print(f"RSS kész. Új cikkek: {len(new_articles)}, Összesen a frissített XML-ben: {len(fg.entry())}")

if __name__ == "__main__":
    scrape()
