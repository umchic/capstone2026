import requests
import trafilatura
from pathlib import Path

URL = "https://www.britannica.com/place/Washington-DC"
OUTPUT_FILE = Path("Washington DC descriptions/websites/washingtondc_britannica.txt")


def get_britannica_text(url):
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

    text = trafilatura.extract(
        response.text,
        include_links=False,
        include_images=False,
        include_tables=False,
        include_comments=False,
        favor_precision=True
    )

    if not text:
        raise RuntimeError(
            "Could not extract article text. "
            "The page may be blocked or its structure may have changed."
        )

    return text


try:
    text = get_britannica_text(URL)

    # Create the output directory if necessary
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Save as UTF-8 plain text
    OUTPUT_FILE.write_text(text, encoding="utf-8")

    print(f"Saved to: {OUTPUT_FILE.resolve()}")
    print(f"Characters: {len(text):,}")

except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
    if e.response is not None and e.response.status_code == 403:
        print(
            "Britannica denied the request. "
            "Try an authorized access method or use another source."
        )

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")

except RuntimeError as e:
    print(f"Extraction failed: {e}")

