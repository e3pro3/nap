from rss import build_feed

from sources.maszol import collect_new_articles as maszol
from sources.hargitanepe import collect_new_articles as hargita

articles = []

articles.extend(maszol())
articles.extend(hargita())

articles.sort(
    key=lambda x: x["published"],
    reverse=True,
)

build_feed(articles)

def main():

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
