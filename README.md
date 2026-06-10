# Scraping Tool

A desktop Python application that extracts the main content of a web page and saves it as Markdown, with JSON metadata.

## Current features

- Graphical user interface built with `PySide6`.
- Download HTML from a provided URL using `requests`.
- Extract the main article content using `readability-lxml`.
- Convert HTML to Markdown using `BeautifulSoup`.
- Save the extracted content as a `.md` file.
- Save metadata such as URL, title, Markdown filename, and metadata filename as a `.json` file.
- Open the generated Markdown and JSON files directly from the app.
- Material theme support with `qt-material`.

## Files

- `main.py`: main GUI application and scraping workflow.
- `scraper.py`: downloads raw HTML from the provided URL.
- `content_processor.py`: processes HTML and saves Markdown and JSON.

## Requirements

- Python 3.8 or newer.
- Python packages:
  - `requests`
  - `beautifulsoup4`
  - `readability-lxml`
  - `html2text`
  - `PySide6`
  - `qt-material` (optional for improved styling)

## Virtual environment setup

1. Open a terminal in the project folder:
   ```bash
   cd <your-project-folder-location>
   ```

2. Create the virtual environment:
   ```bash
   python3 -m venv .venv
   ```

3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

4. Install the required dependencies:
   ```bash
   pip install requests beautifulsoup4 readability-lxml html2text PySide6

   pip install qt-material
   ```

## Usage

With the virtual environment activated, run:

```bash
python main.py
```

Then:

1. Enter the URL of the page to scrape.
2. Choose or confirm the output directory.
3. Click `Extraer Contenido en md`.
4. Open the generated Markdown and JSON files using the app buttons.

## Default output location

The default output directory is:

- `~/mtaa-scraping-tool/output` on Linux/macOS
- `%USERPROFILE%\mtaa-scraping-tool\output` on Windows

If you want to save files elsewhere, choose a different folder in the app.
