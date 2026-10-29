import requests
from bs4 import BeautifulSoup
import re


URL = "https://www.visitingvienna.com/visitorinfo/introduction-to-washingtondc/"
OUTPUT_FILE = "visiting_washingtondc.txt"


def get_page_text(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove elements that aren't part of the article text
    for tag in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "header",
        "footer",
        "aside",
        "form",
        "iframe",
        "svg"
    ]):
        tag.decompose()

    # Try to find the main article content
    article = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", class_=re.compile(r"content|article|post", re.I))
    )

    if article:
        soup = article

    # Extract text
    text = soup.get_text("\n")

    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces around line breaks
    text = re.sub(r" *\n *", "\n", text)

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


text = get_page_text(URL)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Saved to: {OUTPUT_FILE}")
print(f"Characters: {len(text):,}")