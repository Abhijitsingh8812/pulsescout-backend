def deduplicate_articles(articles):

    seen_titles = set()
    unique_articles = []

    for article in articles:

        title = article.get("title")

        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)

    return unique_articles