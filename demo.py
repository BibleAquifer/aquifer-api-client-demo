"""
Aquifer API Client Demo (Aquifer API v2)

Demonstrates:
1. Listing all resources (v2's name for what v1 called collections)
2. Finding the first resource with fewer than 200 articles in English
3. Downloading all articles in English and one non-Roman-script language
   (Hindi, Russian, or Traditional Chinese, in that order of preference)

Results are saved to output/<language_code>/<article_title>.md
"""

import re
from pathlib import Path

from dotenv import load_dotenv

from aquifer import AquiferClient

# Preferred non-Roman-script languages, in priority order
PREFERRED_LANGUAGES = ["hin", "rus", "zht"]
ARTICLE_LIMIT = 200


def safe_filename(name: str) -> str:
    """Convert an article title to a safe filename."""
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = name.strip(". ")
    return name[:200] or "unnamed"


def find_resource_under_limit(client: AquiferClient, limit: int) -> tuple[dict, dict] | None:
    """
    Return (resource_summary, resource_detail) for the first resource with
    between 1 and `limit` English articles.
    """
    for res in client.iter_resources(language="eng"):
        code = res["resource_code"]
        try:
            detail = client.get_resource(code)
        except Exception as exc:
            print(f"  {res['display_name']} ({code}): skipped ({exc})")
            continue
        eng = [lang for lang in detail["available_languages"] if lang["language"] == "eng"]
        count = eng[0]["article_count"] if eng else 0
        print(f"  {res['display_name']} ({code}): {count} English articles")
        if 0 < count < limit:
            return res, detail
    return None


def pick_language(detail: dict) -> str | None:
    """
    Return the best available non-Roman-script language code for a resource,
    preferring hin > rus > zht, then falling back to the first non-English language.
    """
    available = [lang for lang in detail["available_languages"] if lang["article_count"] > 0]
    codes = {lang["language"] for lang in available}
    for lang in PREFERRED_LANGUAGES:
        if lang in codes:
            return lang
    # Fall back to first non-English language
    for lang in available:
        if lang["language"] != "eng":
            return lang["language"]
    return None


def download_articles(
    client: AquiferClient,
    resource_code: str,
    language_code: str,
    output_dir: Path,
) -> int:
    """
    Fetch and save Markdown content for every article of a resource in one language.
    Returns the number of articles successfully saved.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    saved = 0
    # One bulk request per page returns titles and Markdown content together.
    for article in client.iter_articles(
        resource_code, language_code, include="content", content_format="markdown"
    ):
        title = article["title"]
        try:
            content = article.get("content") or ""
            filename = safe_filename(title) + ".md"
            (output_dir / filename).write_text(content, encoding="utf-8")
            print(f"  [OK] {title}")
            saved += 1
        except Exception as exc:
            print(f"  [SKIP] {title}: {exc}")
    return saved


def main() -> None:
    load_dotenv()

    print("=== Aquifer API Client Demo ===\n")

    with AquiferClient.from_env() as client:

        # Step 1: List all resources
        print("--- Resources ---")
        for res in client.iter_resources(language="eng"):
            print(f"  {res['display_name']} ({res['resource_code']})")
        print()

        # Step 2: Find first resource with < 200 English articles
        print(f"--- Finding a resource with fewer than {ARTICLE_LIMIT} English articles ---")
        result = find_resource_under_limit(client, limit=ARTICLE_LIMIT)
        if result is None:
            print("No suitable resource found.")
            return
        resource, detail = result
        code = resource["resource_code"]
        name = resource["display_name"]
        print(f"\nSelected: {name!r} ({code})\n")

        # Step 3: Download all English articles
        print("--- Downloading articles in English ---")
        eng_dir = Path("output") / "eng"
        saved_eng = download_articles(client, code, "eng", eng_dir)
        print(f"\nSaved {saved_eng} English articles to {eng_dir}/\n")

        # Step 4: Pick a non-Roman-script language
        lang_code = pick_language(detail)
        if lang_code is None:
            print("No alternate language available for this resource.")
            return
        print(f"--- Selected alternate language: {lang_code} ---\n")

        # Step 5: Download all articles in the alternate language
        print(f"--- Downloading articles in {lang_code} ---")
        alt_dir = Path("output") / lang_code
        saved_alt = download_articles(client, code, lang_code, alt_dir)
        print(f"\nSaved {saved_alt} {lang_code} articles to {alt_dir}/\n")

    print("=== Done ===")


if __name__ == "__main__":
    main()
