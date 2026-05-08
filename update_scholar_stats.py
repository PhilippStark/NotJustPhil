"""
Fetch citation stats from Google Scholar and patch the hardcoded values in index.html.
Run by GitHub Actions weekly; safe to run locally too.
"""
import re
import sys
from datetime import date

SCHOLAR_ID = "WewG57wAAAAJ"
INDEX_FILE = "index.html"

def fetch_stats(scholar_id):
    from scholarly import scholarly
    print(f"Fetching Scholar profile for {scholar_id} ...")
    author = scholarly.search_author_id(scholar_id)
    author = scholarly.fill(author, sections=["basics"])
    citations = int(author.get("citedby", 0))
    hindex    = int(author.get("hindex",  0))
    # paper count: use publication list length from basics fill
    papers = len(author.get("publications", []))
    print(f"  citations={citations}, h-index={hindex}, papers={papers}")
    return citations, hindex, papers

def patch_html(citations, hindex, papers):
    with open(INDEX_FILE, encoding="utf-8") as f:
        html = f.read()

    def replace_metric(html, elem_id, value):
        return re.sub(
            rf'(<div class="m-val" id="{elem_id}">)\d+(</div>)',
            rf'\g<1>{value}\2',
            html
        )

    html = replace_metric(html, "m-cit", citations)
    html = replace_metric(html, "m-h",   hindex)
    if papers > 0:
        html = replace_metric(html, "m-n", papers)

    # Update the "Last updated" line in pub-status
    month_year = date.today().strftime("%B %Y")
    html = re.sub(
        r'(· Last updated )[A-Za-z]+ \d{4}',
        rf'\g<1>{month_year}',
        html
    )

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Patched {INDEX_FILE}")

if __name__ == "__main__":
    try:
        citations, hindex, papers = fetch_stats(SCHOLAR_ID)
        patch_html(citations, hindex, papers)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("Keeping existing hardcoded values.")
        sys.exit(0)   # exit 0 so the workflow doesn't fail
