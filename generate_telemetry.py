
import os
import json
import urllib.request
from datetime import date, timedelta

USERNAME = "abdulrahmanrifayath"
TOKEN = os.environ["GH_TOKEN"]

query = """
query($user: String!) {
  user(login: $user) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

payload = json.dumps({
    "query": query,
    "variables": {"user": USERNAME}
}).encode()

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.load(response)

calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]

days = [
    day
    for week in calendar["weeks"]
    for day in week["contributionDays"]
]

days.sort(key=lambda x: x["date"])

active = {
    date.fromisoformat(d["date"])
    for d in days
    if d["contributionCount"] > 0
}

today = max(
    date.fromisoformat(d["date"]) for d in days
)

# Current streak
current = 0
cursor = today

while cursor in active:
    current += 1
    cursor -= timedelta(days=1)

# Longest streak
longest = 0
run = 0
longest_start = None
longest_end = None
run_start = None

for d in sorted(active):
    if run == 0:
        run_start = d

    if d - (d - timedelta(days=1)) == timedelta(days=1):
        pass

    if run > 0 and d - previous != timedelta(days=1):
        run = 0
        run_start = d

    run += 1

    if run > longest:
        longest = run
        longest_start = run_start
        longest_end = d

    previous = d

# Fix the first-day edge case
if active:
    ordered = sorted(active)
    longest = 1
    run = 1
    longest_start = ordered[0]
    longest_end = ordered[0]
    run_start = ordered[0]

    for i in range(1, len(ordered)):
        if ordered[i] - ordered[i - 1] == timedelta(days=1):
            run += 1
        else:
            run = 1
            run_start = ordered[i]

        if run > longest:
            longest = run
            longest_start = run_start
            longest_end = ordered[i]

# Dates for current streak
if current:
    current_start = today - timedelta(days=current - 1)
    current_end = today
else:
    current_start = None
    current_end = None

def fmt(d):
    return d.strftime("%d %b %Y") if d else "—"

# Generate SVG
svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
width="1000" height="330" viewBox="0 0 1000 330">
<rect width="1000" height="330" rx="18" fill="#0D1117"/>

<text x="42" y="45" fill="#8B949E"
font-family="monospace" font-size="14">
RIFAYATH // CONTRIBUTION TELEMETRY
</text>

<text x="42" y="85" fill="#E6EDF3"
font-family="monospace" font-size="24" font-weight="bold">
GITHUB ACTIVITY REPORT
</text>

<line x1="42" y1="105" x2="958" y2="105"
stroke="#30363D"/>

<text x="42" y="140" fill="#8B949E"
font-family="monospace" font-size="14">CURRENT STREAK</text>

<text x="42" y="183" fill="#58A6FF"
font-family="monospace" font-size="40" font-weight="bold">
{current} DAYS
</text>

<text x="42" y="210" fill="#C9D1D9"
font-family="monospace" font-size="12">
{fmt(current_start)} → {fmt(current_end)}
</text>

<text x="360" y="140" fill="#8B949E"
font-family="monospace" font-size="14">LONGEST STREAK</text>

<text x="360" y="183" fill="#BC8CFF"
font-family="monospace" font-size="40" font-weight="bold">
{longest} DAYS
</text>

<text x="360" y="210" fill="#C9D1D9"
font-family="monospace" font-size="12">
{fmt(longest_start)} → {fmt(longest_end)}
</text>

<text x="710" y="140" fill="#8B949E"
font-family="monospace" font-size="14">TOTAL CONTRIBUTIONS</text>

<text x="710" y="183" fill="#39D353"
font-family="monospace" font-size="40" font-weight="bold">
{calendar["totalContributions"]}
</text>

<text x="710" y="210" fill="#C9D1D9"
font-family="monospace" font-size="12">
RECENT CONTRIBUTION YEAR
</text>

<rect x="42" y="250" width="916" height="40" rx="8"
fill="#161B22"/>

<text x="60" y="276" fill="#58A6FF"
font-family="monospace" font-size="13">
STATUS: ONLINE  //  DATA SOURCE: GITHUB CONTRIBUTION CALENDAR
</text>

</svg>"""

os.makedirs("assets", exist_ok=True)

with open("assets/github-telemetry.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("Telemetry SVG generated successfully.")
