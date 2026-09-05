import re


STOP_WORDS = {

    "the",
    "a",
    "an",
    "is",
    "are",
    "of",
    "in",
    "to",
    "for",
    "with",
    "and",
    "on",
    "at"
}


def extract_topics(text):

    if not text:

        return []

    words = re.findall(
        r"\b[A-Za-z]{3,}\b",
        text
    )

    topics = []

    for word in words:

        word = word.lower()

        if word in STOP_WORDS:

            continue

        topics.append(word)

    return list(
        set(topics)
    )[:10]