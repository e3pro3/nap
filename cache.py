import json
from datetime import datetime, timedelta, timezone

from config import CACHE_FILE, DATA_DIR, KEEP_DAYS


def load_articles():
    """
    Betölti az articles.json tartalmát.
    """

    if not CACHE_FILE.exists():
        return []

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_articles(articles):
    """
    Elmenti az articles.json fájlt.
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            articles,
            f,
            ensure_ascii=False,
            indent=2,
        )


def filter_old_articles(articles):
    """
    Kidobja az 5 napnál régebbi cikkeket.
    """

    limit = datetime.now(
        timezone.utc
    ) - timedelta(days=KEEP_DAYS)

    result = []

    for article in articles:

        date = article.get("published")

        if not date:
            continue

        try:
            published = datetime.fromisoformat(date)
        except Exception:
            continue

        if published.tzinfo is None:
            published = published.replace(
                tzinfo=timezone.utc
            )

        if published >= limit:
            result.append(article)

    return result


def merge_articles(old_articles, new_articles):
    """
    Régi és új cikkek egyesítése.
    """

    merged = {}

    for article in old_articles:
        link = article.get("link")
        if link:
            merged[link] = article

    for article in new_articles:
        link = article.get("link")
        if link:
            merged[link] = article

    articles = list(
        merged.values()
    )

    articles.sort(
        key=lambda x: x.get(
            "published",
            ""
        ),
        reverse=True,
    )

    return articles


def get_known_links(articles):
    """
    Már ismert linkek.
    """

    return {
        article["link"]
        for article in articles
        if article.get("link")
    }
