from rss import build_feed
from config import MAX_ARTICLES

from sources.maszol import collect_new_articles as maszol
from sources.hargitanepe import collect_new_articles as hargita


def main():

    print("=" * 60)
    print("RSS Generator")
    print("=" * 60)

    articles = []

    articles.extend(maszol())
    articles.extend(hargita())

    articles.sort(
        key=lambda x: x["published"],
        reverse=True,
    )

    articles = articles[:MAX_ARTICLES]

    print(f"RSS-be kerülő cikkek: {len(articles)}")

    build_feed(articles)

    print()
    print("✔ RSS sikeresen elkészült!")
    print()


if __name__ == "__main__":
    main()
