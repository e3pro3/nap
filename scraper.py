from sources.maszol import collect_new_articles
from sources.maszol import debug_article
from rss import build_feed


def main():

    debug_article(
        "https://maszol.ro/belfold/A-kanikula-az-uj-normalitas-Egy-erdelyi-varosban-is-aggasztoan-novekszik-az-atlaghomerseklet"
    )

    return

    print("=" * 60)
    print("RSS Generator")
    print("=" * 60)

    articles = collect_new_articles()

    print(f"RSS-be kerülő cikkek: {len(articles)}")

    build_feed(articles)

    print()
    print("✔ RSS sikeresen elkészült!")
    print()


if __name__ == "__main__":
    main()
    
    
