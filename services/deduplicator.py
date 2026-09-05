# services/deduplicator.py

def deduplicate(articles):

    seen = set()

    unique_articles = []

    for article in articles:

        title = article.get("title", "").strip()

        if not title:
            continue

        if title not in seen:

            seen.add(title)

            unique_articles.append(article)

    return unique_articles