from pathlib import Path

# --- Webhely ---

BASE_URL = "https://maszol.ro"

FEED_TITLE = "Maszol - Friss hírek"

FEED_DESCRIPTION = "Automatikusan generált RSS feed"

FEED_LANGUAGE = "hu"

# --- Fájlok ---

ROOT = Path(__file__).parent

DATA_DIR = ROOT / "data"

CACHE_FILE = DATA_DIR / "articles.json"

RSS_FILE = ROOT / "maszol.xml"

# --- Scraper ---

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/137.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT
}

REQUEST_TIMEOUT = 20

SCAN_LIMIT = 60

MAX_ARTICLES = 40

KEEP_DAYS = 5

# --- XML ---

MEDIA_NS = "http://search.yahoo.com/mrss/"

ATOM_NS = "http://www.w3.org/2005/Atom/"
