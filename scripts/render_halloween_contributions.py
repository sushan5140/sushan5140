#!/usr/bin/env python3
"""Render a public GitHub contribution calendar using GitHub's Halloween dark palette.

No third-party service or Python dependencies are required.
GitHub's authenticated GraphQL API supplies the real day counts/levels.
"""
import html
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

LOGIN = os.environ.get("TARGET_GITHUB_USER") or os.environ.get("GITHUB_REPOSITORY_OWNER") or "sushan5140"
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUT = Path("assets/halloween-contributions.svg")

# GitHub's Halloween dark-mode variables; level 4 is intentionally yellow.
COLORS = {
    "NONE": "#151b23",
    "FIRST_QUARTILE": "#fac68f",
    "SECOND_QUARTILE": "#c46212",
    "THIRD_QUARTILE": "#984b10",
    "FOURTH_QUARTILE": "#e3d04f",
}
ORDER = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date weekday contributionCount contributionLevel }
        }
      }
    }
  }
}
"""

def fetch_calendar():
    if not TOKEN:
        raise RuntimeError("GH_TOKEN is required; cannot display invented contribution data")
    body = json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode("utf-8")
    request = Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": "Bearer " + TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": "halloween-contributions-profile",
        },
    )
    with urlopen(request, timeout=30) as response:
        data = json.load(response)
    if data.get("errors"):
        raise RuntimeError("GitHub GraphQL error: " + str(data["errors"]))
    user = data.get("data", {}).get("user")
    if not user:
        raise RuntimeError("GitHub user not found: " + LOGIN)
    return user["contributionsCollection"]["contributionCalendar"]

def render(calendar):
    weeks = calendar["weeks"]
    if not weeks:
        raise RuntimeError("No contribution weeks returned")
    gap, cell, left, top = 3, 10, 42, 66
    step = gap + cell
    width = max(790, left + len(weeks) * step + 24)
    height = 196
    total = int(calendar["totalContributions"])
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-label="GitHub Halloween contribution calendar for ' + html.escape(LOGIN, quote=True) + '" '
        'viewBox="0 0 ' + str(width) + ' ' + str(height) + '" width="' + str(width) + '" height="' + str(height) + '">',
        '<rect width="100%" height="100%" rx="14" fill="#0d1117"/>',
        '<rect x="0.5" y="0.5" width="' + str(width-1) + '" height="' + str(height-1) + '" rx="14" fill="none" stroke="#30363d"/>',
        '<g font-family="Arial, Helvetica, sans-serif">',
        '<text x="20" y="28" font-size="15" font-weight="bold" fill="#e6edf3">SUSAN\'S CONTRIBUTIONS</text>',
        '<text x="' + str(width-20) + '" y="28" text-anchor="end" font-size="12" font-weight="bold" fill="#e3d04f">HALLOWEEN EDITION &#x1F383;</text>',
        '<text x="20" y="46" font-size="11" fill="#8b949e">' + format(total, ",") + ' contributions in the last year · updates daily</text>',
    ]
    for weekday, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = top + weekday * step + 8
        lines.append(f'<text x="13" y="{y}" font-size="10" fill="#8b949e">{label}</text>')

    labeled_months = set()
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for i, week in enumerate(weeks):
        x = left + i * step
        for day in week["contributionDays"]:
            date = day["date"]
            weekday = int(day["weekday"])
            level = day["contributionLevel"]
            color = COLORS.get(level)
            if color is None:
                raise RuntimeError("Unknown GitHub contribution level: " + str(level))
            if not 0 <= weekday <= 6:
                raise RuntimeError("Invalid weekday: " + str(weekday))
            count = int(day["contributionCount"])
            y = top + weekday * step
            tooltip = html.escape(f'{date}: {count} contribution' + ("" if count == 1 else "s"))
            lines.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{color}"><title>{tooltip}</title></rect>')
            month_key = date[:7]
            if int(date[8:10]) <= 7 and month_key not in labeled_months:
                labeled_months.add(month_key)
                month = month_names[int(date[5:7])-1]
                lines.append(f'<text x="{x}" y="{top-11}" font-size="10" fill="#8b949e">{month}</text>')

    base = top + 7*step + 22
    lines.extend([
        f'<text x="20" y="{base+2}" font-size="10" fill="#8b949e">Real public GitHub activity · Halloween dark theme</text>',
        f'<text x="{width-157}" y="{base+2}" font-size="10" fill="#8b949e">Less</text>',
    ])
    for i, level in enumerate(ORDER):
        x = width - 124 + i * 18
        lines.append(f'<rect x="{x}" y="{base-8}" width="11" height="11" rx="2" fill="{COLORS[level]}"/>')
    lines.extend([
        f'<text x="{width-14}" y="{base+2}" text-anchor="end" font-size="10" fill="#8b949e">More</text>',
        '</g></svg>',
    ])
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    calendar = fetch_calendar()
    svg = render(calendar)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}: {calendar['totalContributions']} public contributions for {LOGIN}")
