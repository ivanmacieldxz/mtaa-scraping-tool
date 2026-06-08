import argparse
from scraper import extract_info
from content_processor import save_markdown_from_html


def main():
    parser = argparse.ArgumentParser(
        description="Extract the main text from a webpage and save it as Markdown."
    )

    # define script's required url argument
    parser.add_argument("url", help="Webpage to analyze full url.")
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory where the Markdown file will be saved.",
    )

    args = parser.parse_args()
    html = extract_info(args.url)

    try:
        filepath, title = save_markdown_from_html(html, output_dir=args.output_dir)
        print(f"\n[+] Page title:\n-> {title}\n")
        print(f"[+] Se guardó el contenido principal en: {filepath}")
    except Exception as err:
        print(f"[!] Error procesando el contenido: {err}")


if __name__ == "__main__":
    main()