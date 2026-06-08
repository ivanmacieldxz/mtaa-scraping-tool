import argparse
import requests
from bs4 import BeautifulSoup

def extract_info(url):
    """connects to url and extracts data"""
    print(f"[+] Connecting to: {url}...")

    # define basic user-agent to not get blocked as a bot
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        # GET request
        response = requests.get(url, headers=headers, timeout=10)

        # raise exception if state is not 200 (OK)
        response.raise_for_status()

        # parse html content
        soup = BeautifulSoup(response.text, "html.parser")

        # extract info
        # get title
        title = soup.title.string if soup.title else "sin título"
        print(f"\nPage title:\n-> {title}\n")

        text_content = soup.text
        print(f"\nPage content: \n\n{text_content}")

    except requests.exceptions.RequestException as e:
        print(f"[!] Error while trying to connect: {e}")


def main():
    # setup console argument handler
    parser = argparse.ArgumentParser(
        description="Basic info extracting from webpage script"
    )

    # define script's required url argument
    parser.add_argument("url", help="Webpage to analyze full url.")

    # parse user introduced arguments
    args = parser.parse_args()

    # execute main function with input url
    extract_info(args.url)

if __name__ == "__main__":
    main()

        