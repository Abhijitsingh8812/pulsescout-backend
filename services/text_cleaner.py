from bs4 import BeautifulSoup
import re


def clean_html(text: str) -> str:

    if not text:
        return ""

    soup = BeautifulSoup(
        text,
        "html.parser"
    )

    cleaned = soup.get_text(
        " ",
        strip=True
    )

    cleaned = re.sub(
        r"http\S+",
        "",
        cleaned
    )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned
    )

    return cleaned.strip()