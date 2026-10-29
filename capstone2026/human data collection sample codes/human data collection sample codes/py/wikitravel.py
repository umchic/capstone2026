
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path


def clean_text(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]*\n+", "\n\n", text)
    return text.strip()


def get_wikitravel_article(page_title):
    api_url = "https://wikitravel.org/wiki/en/api.php"

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

    print("Requesting Wikitravel...", flush=True)

    response = requests.get(
        api_url,
        params=params,
        headers=headers,
        timeout=30,
    )

    print("HTTP status:", response.status_code, flush=True)

    if response.status_code == 403:
        raise RuntimeError(
            "Wikitravel denied the request (403 Forbidden). "
            "Use an authorized access method or collect data "
            "from another permitted source."
        )

    response.raise_for_status()
    data = response.json()

    if "error" in data:
        raise RuntimeError(f"API error: {data['error']}")

    if "parse" not in data:
        raise RuntimeError(f"Unexpected API response: {data}")

    print("Article:", data["parse"]["title"], flush=True)

    html = data["parse"]["text"]["*"]
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "table", "sup"]):
        tag.decompose()

    for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
        heading.insert_before("\n\n")
        heading.insert_after("\n")

    for link in soup.find_all("a"):
        link.replace_with(link.get_text(" ", strip=True))

    text = clean_text(soup.get_text("\n"))

    if not text:
        raise RuntimeError("No article text could be extracted.")

    return text


try:
    city = "Washington, D.C."
    text = get_wikitravel_article(city)

    output_file = (
        Path("Washington DC descriptions")
        / "websites"
        / "washingtondc_wikitravel.txt"
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(text, encoding="utf-8")

    print(f"Saved to: {output_file.resolve()}")
    print(f"Characters: {len(text):,}")

except (requests.exceptions.RequestException, RuntimeError, ValueError, KeyError) as error:
    print(f"Collection failed: {error}")
    

