# Scraping Tool

A simple Python tool to extract information from a web page.

## Current features

- HTTP connection to a URL provided via command line.
- Extraction of the page title.
- Printing the page text content to the console.

## Planned features

- Graphical user interface for easier use.
- Download scraping results as PDF or Markdown.

## Requirements

- Python 3.8+ (using a virtual environment is recommended).
- Libraries:
  - `requests`
  - `beautifulsoup4`

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
   pip install requests beautifulsoup4
   ```

## Usage

Run the script with the URL you want to analyze as an argument:

```bash
python scraper.py https://example.com
```

### Example

```bash
python scraper.py https://www.python.org
```

The script will print the page title and extracted text content to the console.

## Notes

- Currently the tool works as a command-line application.
- A graphical interface and export to PDF/Markdown are planned as future improvements.
