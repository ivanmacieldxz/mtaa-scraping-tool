import os
import re
from bs4 import BeautifulSoup
from readability import Document


def slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[\s\t\n]+", "-", text)
    text = re.sub(r"[^a-z0-9\-]+", "", text)
    return text or "scraped-page"


def save_markdown_from_html(html, output_dir="."):
    """Process HTML with readability and save the main content as Markdown."""
    doc = Document(html)
    title = doc.short_title() or "sin título"
    summary_html = doc.summary()
    summary_soup = BeautifulSoup(summary_html, "html.parser")
    main_text = summary_soup.get_text("\n", strip=True)

    if not main_text:
        fallback_soup = BeautifulSoup(html, "html.parser")
        main_text = fallback_soup.get_text("\n", strip=True)

    markdown_content = f"# {title}\n\n{main_text}\n"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{slugify(title)}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_content)

    return filepath, title
