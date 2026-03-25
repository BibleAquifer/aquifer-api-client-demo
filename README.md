# Aquifer API Client Demo

A minimal demo of the [aquifer-api-client](https://github.com/BibleAquifer/aquifer-api-client) Python library.

## What this demo does

1. Lists all available resource collections from the Aquifer API
2. Finds the first collection with fewer than 200 articles
3. Downloads the full Markdown content of every article in that collection — once in **English** and once in a **non-Roman-script language** (Hindi, Russian, or Traditional Chinese, in that order of preference)
4. Saves the results to `output/eng/` and `output/<lang>/`

## Prerequisites

- Python 3.11 or newer
- An Aquifer API key (contact [Aquifer](https://aquifer.bible))
- Git (to install the library from GitHub)

## Setup

```bash
git clone https://github.com/BibleAquifer/aquifer-api-client-demo
cd aquifer-api-client-demo

python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env and set AQUIFER_API_KEY=your-key-here
```

## Usage

```bash
python demo.py
```

Progress is printed to stdout. Downloaded articles are saved to:

```
output/
  eng/          # English Markdown files
  hin/          # Hindi Markdown files (or rus/ or zht/)
```

The `output/` directory is excluded from version control.

## Links

- [aquifer-api-client library](https://github.com/BibleAquifer/aquifer-api-client)
- [Aquifer API documentation](https://api.aquifer.bible/docs/index.html?url=/swagger/v1/swagger.json)
