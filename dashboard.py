#!/usr/bin/env python3
"""Build dashboard.html from state.json and the core PRs the bot reviewed."""

import argparse
import datetime as dt
import html
import json
import subprocess
from pathlib import Path

REPO = "home-assistant/core"
PR_URL = f"https://github.com/{REPO}/pull/"
DONE = ("merged", "closed")


def search_reviewed(reviewer: str, since: str) -> list[dict]:
    """Return PRs reviewed by `reviewer` and updated on or after `since`."""
    query = f"repo:{REPO} is:pr reviewed-by:{reviewer} updated:>={since}"
    items: list[dict] = []
    for page in range(1, 11):  # Search returns at most 1000 results.
        out = subprocess.run(
            ["gh", "api", "-X", "GET", "search/issues", "-f", f"q={query}",
             "-f", "per_page=100", "-f", f"page={page}"],
            capture_output=True, text=True, check=True,
        ).stdout
        batch = json.loads(out)["items"]
        items += batch
        if len(batch) < 100:
            break
    return items


def build_rows(state: dict, items: list[dict]) -> list[dict]:
    prs = state.get("prs", {})
    muted = {int(n) for n in state.get("muted", [])}
    rows: dict[int, dict] = {}
    for item in items:
        if (item.get("pull_request") or {}).get("merged_at"):
            status = "merged"
        elif item["state"] == "closed":
            status = "closed"
        elif item.get("draft"):
            status = "draft"
        else:
            status = "open"
        rows[item["number"]] = {
            "title": item["title"],
            "author": item["user"]["login"],
            "status": status,
            "updated_at": item["updated_at"],
        }
    # Tracked PRs the search index hasn't caught up with yet.
    for key in prs:
        rows.setdefault(int(key), {"title": None, "author": None, "status": "open", "updated_at": None})
    for number, row in rows.items():
        entry = prs.get(str(number), {})
        review_ids = entry.get("review_ids") or []
        row.update(
            number=number,
            muted=number in muted,
            reviewed_at=entry.get("reviewed_at"),
            findings=entry.get("findings"),
            review_id=review_ids[-1] if review_ids else None,
        )
    ordered = sorted(rows.values(), key=lambda r: r["updated_at"] or r["reviewed_at"] or "", reverse=True)
    return sorted(ordered, key=lambda r: r["status"] in DONE)


def fmt_time(value: str | None) -> str:
    return value[:16].replace("T", " ") if value else "—"


def fmt_findings(findings: dict | None) -> tuple[str, str]:
    if not findings:
        return "—", ""
    parts = [f"{findings[k]} {k}" for k in ("critical", "problem") if findings.get(k)]
    return (", ".join(parts), "bad") if parts else ("Looks good", "good")


def render_row(row: dict) -> str:
    n = row["number"]
    esc = html.escape
    status = row["status"] + (" · muted" if row["muted"] else "")
    reviewed = esc(fmt_time(row["reviewed_at"]))
    if row["review_id"]:
        reviewed = f'<a href="{PR_URL}{n}#pullrequestreview-{int(row["review_id"])}">{reviewed}</a>'
    result, result_class = fmt_findings(row["findings"])
    return (
        "<tr>"
        f'<td class="nowrap"><a href="{PR_URL}{n}">#{n}</a></td>'
        f"<td>{esc(row['title'] or '—')}</td>"
        f"<td>{esc(row['author'] or '—')}</td>"
        f'<td class="nowrap s-{row["status"]}">{esc(status)}</td>'
        f'<td class="nowrap">{reviewed}</td>'
        f'<td class="nowrap {result_class}">{esc(result)}</td>'
        "</tr>"
    )


def render(state: dict, rows: list[dict], reviewer: str, days: int) -> str:
    now = dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    open_rows = [r for r in rows if r["status"] not in DONE]
    counts = [
        ("open", len(open_rows)),
        ("changes requested", sum(fmt_findings(r["findings"])[1] == "bad" for r in open_rows)),
        ("looks good", sum(fmt_findings(r["findings"])[1] == "good" for r in open_rows)),
        ("merged", sum(r["status"] == "merged" for r in rows)),
        ("closed", sum(r["status"] == "closed" for r in rows)),
    ]
    counts_html = "".join(f"<li><b>{n}</b> {label}</li>" for label, n in counts)
    if rows:
        body = (
            '<div class="wrap"><table><thead><tr>'
            "<th>PR</th><th>Title</th><th>Author</th><th>State</th><th>Last review (UTC)</th><th>Result</th>"
            "</tr></thead><tbody>" + "".join(render_row(r) for r in rows) + "</tbody></table></div>"
        )
    else:
        body = "<p>No reviewed PRs yet.</p>"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Core PR triage</title>
<style>
:root {{ color-scheme: light dark; --bg: #fff; --fg: #1f2328; --muted: #59636e; --line: #d1d9e0; --good: #1a7f37; --bad: #cf222e; --merged: #8250df; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg: #0d1117; --fg: #e6edf3; --muted: #9198a1; --line: #3d444d; --good: #3fb950; --bad: #f85149; --merged: #ab7df8; }} }}
body {{ margin: 0; padding: 24px 16px; background: var(--bg); color: var(--fg); font: 14px/1.5 system-ui, sans-serif; }}
main {{ max-width: 1100px; margin: 0 auto; }}
h1 {{ font-size: 20px; margin: 0 0 4px; }}
.meta, th, .s-draft, .s-closed {{ color: var(--muted); }}
.meta {{ margin: 0 0 16px; }}
.counts {{ display: flex; flex-wrap: wrap; gap: 8px 24px; margin: 0 0 16px; padding: 0; list-style: none; }}
.counts b {{ font-size: 18px; }}
.wrap {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{ font-weight: 600; white-space: nowrap; }}
.nowrap {{ white-space: nowrap; }}
a {{ color: inherit; }}
.s-open, .good {{ color: var(--good); }}
.s-merged {{ color: var(--merged); }}
.bad {{ color: var(--bad); }}
</style>
</head>
<body>
<main>
<h1>Core PR triage</h1>
<p class="meta">Last run: {html.escape(fmt_time(state.get("last_run_at")))} UTC · Built: {fmt_time(now)} UTC · PRs reviewed by {html.escape(reviewer)}, updated in the last {days} days.</p>
<ul class="counts">{counts_html}</ul>
{body}
</main>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", default="state.json")
    parser.add_argument("--out", default="dashboard.html")
    parser.add_argument("--reviewer", default="hacoreview")
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()
    path = Path(args.state)
    state = json.loads(path.read_text()) if path.exists() else {}
    since = (dt.datetime.now(dt.UTC) - dt.timedelta(days=args.days)).strftime("%Y-%m-%d")
    rows = build_rows(state, search_reviewed(args.reviewer, since))
    Path(args.out).write_text(render(state, rows, args.reviewer, args.days))


if __name__ == "__main__":
    main()
