# Scraping Tool

A simple Python command-line tool to extract the main text from a web page and save it as Markdown.

## Current features

- HTTP connection to a URL provided via command line.
- Extraction of the page's main content using `readability-lxml`.
- Saving the cleaned main content to a Markdown file.
- Separation of concerns: `scraper.py` fetches HTML, `content_processor.py` processes and saves it.

## Files

- `main.py`: command-line entrypoint.
- `scraper.py`: downloads raw HTML from the provided URL.
- `content_processor.py`: extracts the main article text and writes Markdown.

## Requirements

- Python 3.8+ (using a virtual environment is recommended).
- Libraries:
  - `requests`
  - `beautifulsoup4`
  - `readability-lxml`

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

4. Install dependencies:
   ```bash
   pip install requests beautifulsoup4 readability-lxml
   ```

## Usage

Run the tool with the URL you want to analyze:

```bash
python main.py https://example.com
```

To save the output in a specific folder:

```bash
python main.py https://example.com --output-dir output
```

### Example

```bash
python main.py https://www.python.org
```

The script will create a Markdown file named after the page title in the current folder by default.

## Notes

- `main.py` is now the entrypoint.
- The tool saves the extracted main article text as Markdown.
- Future improvements can include PDF export or a GUI.
