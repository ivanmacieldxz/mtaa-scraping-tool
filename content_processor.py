import os
import re
import json
from bs4 import BeautifulSoup, NavigableString
from readability import Document


def slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[\s\t\n]+", "-", text)
    text = re.sub(r"[^a-z0-9\-]+", "", text)
    return text or "scraped-page"


def html_to_markdown(html):
    soup = BeautifulSoup(html, "html.parser")

    def render(node):
        if isinstance(node, NavigableString):
            return str(node)

        name = node.name.lower() if node.name else None
        if not name:
            return ""

        if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(name[1])
            text = node.get_text(" ", strip=True)
            return f"{('#' * level)} {text}\n\n"

        if name == "p":
            text = node.get_text(" ", strip=True)
            return f"{text}\n\n" if text else ""

        if name == "br":
            return "\n"

        if name == "li":
            text = "".join(render(child) for child in node.children).strip()
            return f"- {text}\n"

        if name in {"ul", "ol"}:
            items = [render(child) for child in node.children if getattr(child, "name", None) == "li"]
            return "".join(items) + "\n"

        if name == "a":
            href = node.get("href", "")
            text = node.get_text(" ", strip=True) or href
            return f"[{text}]({href})" if href else text

        if name in {"strong", "b"}:
            return f"**{node.get_text(' ', strip=True)}**"

        if name in {"em", "i"}:
            return f"*{node.get_text(' ', strip=True)}*"

        if name == "code" and node.parent and node.parent.name != "pre":
            return f"`{node.get_text(' ', strip=True)}`"

        if name == "pre":
            text = node.get_text("\n", strip=True)
            return f"```\n{text}\n```\n\n"

        if name in {"div", "section", "article", "header", "main", "footer", "blockquote", "figure"}:
            content = "".join(render(child) for child in node.children).strip()
            return f"{content}\n\n" if content else ""

        return "".join(render(child) for child in node.children)

    markdown = render(soup)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()
    markdown = re.sub(r"\t{2,}", "\t", markdown).strip()
    markdown = re.sub(r" {2,}", " ", markdown).strip() + "\n"
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
        "titulo": filename_title
    }
    with open(json_filepath, "w", encoding="utf-8") as json_file:
        json.dump(json_metadata, json_file, ensure_ascii=False, indent=2)

    return filepath, filename_title
