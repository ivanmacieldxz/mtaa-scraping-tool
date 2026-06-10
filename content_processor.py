import os
import re
import json
from bs4 import BeautifulSoup
from readability import Document
from html2text import HTML2Text, escape_md, urlparse


def slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[\s\t\n]+", "-", text)
    text = re.sub(r"[^a-z0-9\-]+", "", text)
    return text or "scraped-page"


def html_to_markdown(html):
    converter = HTML2Text()
    converter.body_width = 0
    converter.unicode_snob = True
    converter.single_line_break = True
    converter.inline_links = True
    converter.protect_links = False
    converter.ignore_images = True
    converter.ignore_links = False

    markdown = converter.handle(html)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip() + "\n"

    def strip_link_title(match):
        text = match.group(1)
        url = match.group(2) or match.group(3) or ""
        return f"[{text}]({url})"

    markdown = re.sub(
        r"\[([^\]]+)\]\((?:<([^>]+)>|([^\)\s]+))(?:\s+\"[^\"]*\")?\)",
        strip_link_title,
        markdown,
    )
    return markdown


def first_heading_text(html):
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find(["h1", "h2", "h3", "h4", "h5", "h6"])
    return heading.get_text(" ", strip=True) if heading else None


def save_markdown_from_html(html, output_dir=".", url=""):
    """Process HTML with readability and save the main content as Markdown and JSON metadata."""
    doc = Document(html)
    page_title = doc.short_title()
    summary_html = doc.summary()
    main_text = html_to_markdown(summary_html)

    if not main_text.strip():
        fallback_soup = BeautifulSoup(html, "html.parser")
        main_text = html_to_markdown(str(fallback_soup))

    first_heading = first_heading_text(summary_html)
    if not first_heading:
        fallback_html = str(BeautifulSoup(html, "html.parser"))
        first_heading = first_heading_text(fallback_html)

    filename_title = first_heading or page_title or "untitled"

    os.makedirs(output_dir, exist_ok=True)
    filename = f"{slugify(filename_title)}.md" if filename_title != "untitled" else "untitled.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as md_file:
        md_file.write(main_text)

    # Save JSON metadata with same filename
    json_filename = filename.replace(".md", ".json")
    json_filepath = os.path.join(output_dir, json_filename)
    json_metadata = {
        "url": url,
        "title": filename_title
    }
    # Añadir nombre del archivo MD generado y del archivo JSON de metadatos
    json_metadata["file"] = filename
    json_metadata["metadata-file"] = json_filename
    with open(json_filepath, "w", encoding="utf-8") as json_file:
        json.dump(json_metadata, json_file, ensure_ascii=False, indent=2)

    return filepath, filename_title
