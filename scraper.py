import requests


def extract_info(url):
    """Fetch the raw HTML from the provided URL."""
    print(f"[+] Connecting to: {url}...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text




        