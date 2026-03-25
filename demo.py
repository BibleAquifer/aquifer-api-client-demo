"""
Aquifer API Client Demo

Demonstrates:
1. Listing all resource collections
2. Finding the first collection with fewer than 200 articles (in English)
3. Downloading all articles in English and one non-Roman-script language
   (Hindi, Russian, or Traditional Chinese, in that order of preference)

Results are saved to output/<language_code>/<article_name>.md
"""

import re
from pathlib import Path

from dotenv import load_dotenv

from aquifer import AquiferClient

# Preferred non-Roman-script languages, in priority order
PREFERRED_LANGUAGES = ["hin", "rus", "zht"]
ARTICLE_LIMIT = 200


def safe_filename(name: str) -> str:
    """Convert an article name to a safe filename."""
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = name.strip(". ")
    return name[:200] or "unnamed"


def find_collection_under_limit(client: AquiferClient, collections: list[dict], limit: int) -> tuple[str, str, int] | None:
    """
    Return (code, display_name, eng_article_count) for the first collection
    with between 1 and `limit` English articles.
    """
    for col in collections:
        code = col["code"]
        display_name = col["displayName"]
        detail = client.get_resource_collection(code, language_codes=["eng"])
        eng_languages = [
            lang for lang in detail["availableLanguages"]
            if lang["languageCode"] == "eng"
        ]
        count = eng_languages[0]["resourceItemCount"] if eng_languages else 0
        print(f"  {display_name} ({code}): {count} English articles")
        if 0 < count < limit:
            return code, display_name, count
    return None


def get_all_articles(client: AquiferClient, collection_code: str, language_code: str) -> list[dict]:
    """Paginate through all articles in a collection for a given language."""
    items = []
    offset = 0
    page_size = 100
    while True:
        page = client.search_resources(
            resource_collection_code=collection_code,
            language_code=language_code,
            limit=page_size,
            offset=offset,
        )
        batch = page.get("items", [])
        items.extend(batch)
        offset += len(batch)
        if offset >= page["totalItemCount"] or not batch:
            break
    return items


def pick_language(client: AquiferClient, content_id: int) -> str | None:
    """
    Return the best available non-Roman-script language code for an article,
    preferring hin > rus > zht, then falling back to the first non-English language.
    """
    available = client.get_resource_available_languages(content_id)
    codes = {lang["languageCode"] for lang in available}
    for lang in PREFERRED_LANGUAGES:
        if lang in codes:
            return lang
    # Fall back to first non-English language
    for lang in available:
        if lang["languageCode"] != "eng":
            return lang["languageCode"]
    return None


def download_articles(
    client: AquiferClient,
    articles: list[dict],
    language_code: str,
    output_dir: Path,
) -> int:
    """
    Fetch and save full Markdown content for each article.
    Returns the number of articles successfully saved.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    saved = 0
    for article in articles:
        content_id = article["id"]
        name = article["name"]
        try:
            if language_code == "eng":
                resource = client.get_resource(content_id, text_type="Markdown")
            else:
                resource = client.get_resource_by_language(
                    content_id, language_code=language_code, text_type="Markdown"
                )
            raw = resource.get("content") or ""
            content = "\n\n".join(raw) if isinstance(raw, list) else raw
            filename = safe_filename(name) + ".md"
            (output_dir / filename).write_text(content, encoding="utf-8")
            print(f"  [OK] {name}")
            saved += 1
        except Exception as exc:
            print(f"  [SKIP] {name}: {exc}")
    return saved


def main() -> None:
    load_dotenv()

    print("=== Aquifer API Client Demo ===\n")

    with AquiferClient.from_env() as client:

        # Step 1: List all resource collections
        print("--- Resource Collections ---")
        collections = client.get_resource_collections(limit=100)
        for col in collections:
            print(f"  {col['displayName']} ({col['code']})")
        print()

        # Step 2: Find first collection with < 200 English articles
        print(f"--- Finding a collection with fewer than {ARTICLE_LIMIT} English articles ---")
        result = find_collection_under_limit(client, collections, limit=ARTICLE_LIMIT)
        if result is None:
            print("No suitable collection found.")
            return
        collection_code, collection_name, article_count = result
        print(f"\nSelected: {collection_name!r} ({collection_code}) — {article_count} English articles\n")

        # Steps 3 & 4: Download all English articles
        print(f"--- Downloading {article_count} articles in English ---")
        english_articles = get_all_articles(client, collection_code, "eng")
        eng_dir = Path("output") / "eng"
        saved_eng = download_articles(client, english_articles, "eng", eng_dir)
        print(f"\nSaved {saved_eng} English articles to {eng_dir}/\n")

        # Step 5: Pick a non-Roman-script language
        if not english_articles:
            print("No articles found; cannot determine alternate language.")
            return
        first_id = english_articles[0]["id"]
        lang_code = pick_language(client, first_id)
        if lang_code is None:
            print("No alternate language available for this collection.")
            return
        print(f"--- Selected alternate language: {lang_code} ---\n")

        # Step 6: Download all articles in the alternate language
        alt_articles = get_all_articles(client, collection_code, lang_code)
        if not alt_articles:
            print(f"No articles found for language '{lang_code}'.")
            return
        print(f"--- Downloading {len(alt_articles)} articles in {lang_code} ---")
        alt_dir = Path("output") / lang_code
        saved_alt = download_articles(client, alt_articles, lang_code, alt_dir)
        print(f"\nSaved {saved_alt} {lang_code} articles to {alt_dir}/\n")

    print("=== Done ===")


if __name__ == "__main__":
    main()
