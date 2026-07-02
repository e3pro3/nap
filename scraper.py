from sources.maszol import collect_new_articles
from rss import build_feed


def main():
    print("=" * 60)
    print("Maszol RSS Generator")
    print("=" * 60)

    articles = collect_new_articles()

    print(f"RSS-be kerülő cikkek: {len(articles)}")

    build_feed(articles)

    print()
    print("✔ RSS sikeresen elkészült!")
    print()


if __name__ == "__main__":
    main()
    
    
