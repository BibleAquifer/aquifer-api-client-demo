# Aquifer API Client Demo

A minimal demo of the [aquifer-api-client](https://github.com/BibleAquifer/aquifer-api-client) Python library (v0.2, Aquifer API v2).

The `aquifer-api-client` hits the Aquifer database (AquiferDB) to access resources granularly through an API. Note that the API used does not directly access resources available on GitHub here, but an upstream database of resources that is used by the [Bible Well mobile app](https://well.bible). 

Our longer-term intention is to replace the AquiferDB API with an API and MCP server that provide access to the resources in the `BibleAquifer` GitHub repositories.

In API v2 a **resource** is a container (for example a Bible dictionary, keyed by `resource_code`) and an **article** is one item inside it (keyed by `content_id`). v1 called resources "collections".

## What this demo does

1. Lists all available resources from the Aquifer API
2. Finds the first resource with fewer than 200 English articles
3. Downloads the full Markdown content of every article in that resource — once in **English** and once in a **non-Roman-script language** (Hindi, Russian, or Traditional Chinese, in that order of preference; if none is available, the first other non-English language)
4. Saves the results to `output/eng/` and `output/<lang>/`

## Prerequisites

- Python 3.11 or newer
- An Aquifer API key ([request one here](https://www.aquifer.bible/apiaccess); existing v1 keys work with v2)
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

Progress is printed to stdout. Articles are fetched in bulk (one paginated `iter_articles` request returns titles and Markdown content together), and each file is named after the article title. Downloaded articles are saved to:

```
output/
  eng/          # English Markdown files
  hin/          # Hindi Markdown files (or rus/ or zht/)
```

The `output/` directory is excluded from version control.

## Links

- [aquifer-api-client library](https://github.com/BibleAquifer/aquifer-api-client)
- [Aquifer API documentation](https://api2.aquifer.bible/docs)
