import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path


def get_wikivoyage_article(page_title):
    api_url = "https://en.wikivoyage.org/w/api.php"

    params = {
        "action": "parse",
        "page": page_title,
        "prop": "text",
        "redirects": 1,
        "format": "json",
    }

    headers = {
        "User-Agent": "WashingtonDCCityResearch/1.0 (educational project)"
    }

    print("1. Connecting to Wikivoyage...", flush=True)

    response = requests.get(
        api_url,
        params=params,
        headers=headers,
        timeout=30
    )

    print("2. HTTP status:", response.status_code, flush=True)
    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise RuntimeError(data["error"])

    if "parse" not in data:
        raise RuntimeError(f"Unexpected API response: {data}")

    print("3. Article:", data["parse"]["title"], flush=True)

    html = data["parse"]["text"]["*"]
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup([
        "script", "style", "noscript", "table",
        "img", "figure", "sup"
    ]):
        tag.decompose()

    for link in soup.find_all("a"):
        link.replace_with(link.get_text(" ", strip=True))

    text = soup.get_text("\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    text = text.strip()

    if not text:
        raise RuntimeError("The article returned no extractable text.")

    print(f"4. Extracted {len(text):,} characters.", flush=True)

    return text


try:
    # Use the canonical article title
    page = "Washington, D.C."

    text = get_wikivoyage_article(page)

    output_file = (
        Path("Washington DC descriptions")
        / "websites"
        / "washingtondc_wikivoyage.txt"
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(text, encoding="utf-8")

    print("5. SUCCESS!", flush=True)
    print(f"Saved to: {output_file.resolve()}", flush=True)

except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}", flush=True)

