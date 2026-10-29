
import requests
import re
from pathlib import Path


def get_wikipedia_plain_text(page_title):
    """Download plain text from a Wikipedia article using its API."""

    api_url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "prop": "extracts",
        "titles": page_title,
        "explaintext": 1,
        "exsectionformat": "plain",
        "format": "json",
        "formatversion": 2,
    }

    headers = {
        "User-Agent": (
            "WashingtonDCCityResearch/1.0 "
            "(educational research project)"
        )
    }

    response = requests.get(
        api_url,
        params=params,
        headers=headers,
        timeout=30
    )
    response.raise_for_status()

    data = response.json()
    pages = data.get("query", {}).get("pages", [])

    if not pages:
        raise RuntimeError(f"Page not found: {page_title}")

    page = pages[0]

    if "missing" in page:
        raise RuntimeError(f"Wikipedia page does not exist: {page_title}")

    text = page.get("extract", "")

    if not text.strip():
        raise RuntimeError("The Wikipedia article returned no text.")

    # Clean excessive whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# Download the Washington, D.C. article
page = "Washington, D.C."
text = get_wikipedia_plain_text(page)

# Save the article in the project directory
output_file = Path("Washington DC descriptions/websites/washingtondc_wikipedia.txt")
output_file.parent.mkdir(parents=True, exist_ok=True)
output_file.write_text(text, encoding="utf-8")

print(f"Saved: {output_file.resolve()}")
print(f"Characters: {len(text):,}")

