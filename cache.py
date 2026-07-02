import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from config import KEEP_DAYS


def load_articles(cache_file):
    """
    Betölti a cache fájlt.
    """

    cache_file = Path(cache_file)

    if not cache_file.exists():
        return []

    try:
        with cache_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_articles(cache_file, articles):
    """
    Elmenti a cache fájlt.
    """

    cache_file = Path(cache_file)

    cache_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with cache_file.open("w", encoding="utf-8") as f:
        json.dump(
            articles,
            f,
            ensure_ascii=False,
            indent=2,
        )


def filter_old_articles(articles):
    """
    Kidobja a KEEP_DAYS napnál régebbi cikkeket.
    """

    limit = datetime.now(timezone.utc) - timedelta(days=KEEP_DAYS)

    result = []

    for article in articles:

        published = article.get("published")

        if not published:
            continue

        try:
            dt = datetime.fromisoformat(published)

            if dt.tzinfo is None:
                dt = dt.replace(
                    tzinfo=timezone.utc
                )

            if dt >= limit:
                result.append(article)

        except (ValueError, TypeError):
            continue

    return result


def merge_articles(old_articles, new_articles):
    """
    Régi és új cikkek egyesítése.
    """

    merged = {}

    for article in old_articles + new_articles:

        link = article.get("link")

        if link:
            merged[link] = article

    articles = sorted(
        merged.values(),
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


def update_cache(cache_file, new_articles):
    """
    Betölti, frissíti és elmenti a cache-t.
    """

    old_articles = load_articles(cache_file)

    articles = merge_articles(
        old_articles,
        new_articles,
    )

    articles = filter_old_articles(
        articles
    )

    save_articles(
        cache_file,
        articles,
    )

    return articles
