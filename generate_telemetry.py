
import os
import json
import urllib.request
from datetime import date, timedelta

# =====================================================
# CONFIGURATION
# =====================================================

USERNAME = "abdulrahmanrifayath"
TOKEN = os.environ["GH_TOKEN"]

# =====================================================
# FETCH GITHUB CONTRIBUTION DATA
# =====================================================

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
    "variables": {
        "user": USERNAME
    }
}).encode("utf-8")

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "GitHub-Telemetry"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.load(response)

# Check GraphQL errors
if result.get("errors"):
    raise RuntimeError(result["errors"])

user_data = result.get("data", {}).get("user")

if not user_data:
    raise RuntimeError("GitHub user not found.")

calendar = user_data["contributionsCollection"]["contributionCalendar"]

days = [
    day
    for week in calendar["weeks"]
    for day in week["contributionDays"]
]

days.sort(key=lambda x: x["date"])

# =====================================================
# PREPARE CONTRIBUTION DATA
# =====================================================

active = {
    date.fromisoformat(day["date"])
    for day in days
    if day["contributionCount"] > 0
}

# Use the latest date returned by GitHub
latest_date = max(
    date.fromisoformat(day["date"])
    for day in days
)

# =====================================================
# CURRENT STREAK
# =====================================================

current = 0
cursor = latest_date

while cursor in active:
    current += 1
    cursor -= timedelta(days=1)

if current > 0:
    current_start = latest_date - timedelta(days=current - 1)
    current_end = latest_date
else:
    current_start = None
    current_end = None

# =====================================================
# LONGEST STREAK
# =====================================================

ordered = sorted(active)

longest = 0
run = 0
longest_start = None
longest_end = None
run_start = None
previous = None

for day in ordered:

    if previous is None or day - previous != timedelta(days=1):
        run = 1
        run_start = day
    else:
        run += 1

    if run > longest:
        longest = run
        longest_start = run_start
        longest_end = day

    previous = day

# =====================================================
# FORMAT DATES
# =====================================================

def fmt(day):
    return day.strftime("%d %b %Y") if day else "—"

# =====================================================
# GENERATE SVG DASHBOARD
# =====================================================

total_contributions = calendar["totalContributions"]

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
font-family="monospace" font-size="14">
CURRENT STREAK
</text>

<text x="42" y="183" fill="#58A6FF"
font-family="monospace" font-size="40" font-weight="bold">
{current} DAYS
</text>

<text x="42" y="210" fill="#C9D1D9"
font-family="monospace" font-size="12">
{fmt(current_start)} → {fmt(current_end)}
</text>

<text x="360" y="140" fill="#8B949E"
font-family="monospace" font-size="14">
LONGEST STREAK
</text>

<text x="360" y="183" fill="#BC8CFF"
font-family="monospace" font-size="40" font-weight="bold">
{longest} DAYS
</text>

<text x="360" y="210" fill="#C9D1D9"
font-family="monospace" font-size="12">
{fmt(longest_start)} → {fmt(longest_end)}
</text>

<text x="710" y="140" fill="#8B949E"
font-family="monospace" font-size="14">
TOTAL CONTRIBUTIONS
</text>

<text x="710" y="183" fill="#39D353"
font-family="monospace" font-size="40" font-weight="bold">
{total_contributions}
</text>

<text x="710" y="210" fill="#C9D1D9"
font-family="monospace" font-size="12">
CONTRIBUTION CALENDAR
</text>

<rect x="42" y="250" width="916" height="40"
rx="8" fill="#161B22"/>

<text x="60" y="276" fill="#58A6FF"
font-family="monospace" font-size="13">
STATUS: ONLINE // DATA SOURCE: GITHUB CONTRIBUTION CALENDAR
</text>

</svg>"""

# =====================================================
# SAVE SVG
# =====================================================

os.makedirs("assets", exist_ok=True)

output_path = "assets/github-telemetry.svg"

with open(output_path, "w", encoding="utf-8") as file:
    file.write(svg)

# =====================================================
# LOG RESULTS
# =====================================================

print("=" * 55)
print("RIFAYATH // GITHUB TELEMETRY")
print("=" * 55)
print(f"Current streak : {current} days")
print(f"Current period : {fmt(current_start)} → {fmt(current_end)}")
print(f"Longest streak : {longest} days")
print(f"Longest period : {fmt(longest_start)} → {fmt(longest_end)}")
print(f"Total commits  : {total_contributions}")
print(f"Generated file : {output_path}")
print("=" * 55)
