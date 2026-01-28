"""
Generate population-adjusted chart of ICE violent confrontations.
Data sources:
- Incidents: Tiers 1-4 JSON files (2025-2026)
- Population: Migration Policy Institute county estimates (mid-2023)
"""

import json
import os
from collections import Counter
import matplotlib.pyplot as plt

exec(open("scripts/generate_county_map.py").read().split("# Load incident data")[0])

incident_files = [
    "data/incidents/tier1_deaths_in_custody.json",
    "data/incidents/tier2_shootings.json",
    "data/incidents/tier2_less_lethal.json",
    "data/incidents/tier3_incidents.json",
    "data/incidents/tier4_incidents.json"
]

non_immigrant_categories = ["us_citizen", "bystander", "officer", "protester", "journalist", "legal_resident"]
county_counts = Counter()
total_mapped = 0

for filepath in incident_files:
    if not os.path.exists(filepath):
        continue
    with open(filepath, "r", encoding="utf-8") as f:
        incidents = json.load(f)
    for inc in incidents:
        victim_cat = inc.get("victim_category", "").lower()
        is_us_citizen = inc.get("us_citizen", False)
        protest_related = inc.get("protest_related", False)
        is_non_immigrant = (victim_cat in non_immigrant_categories or is_us_citizen or protest_related or "citizen" in victim_cat or "protest" in victim_cat)
        if is_non_immigrant:
            city, state = inc.get("city", ""), inc.get("state", "")
            city_state = f"{city}, {state}"
            if city_state in CITY_TO_COUNTY:
                fips = CITY_TO_COUNTY[city_state][1] + CITY_TO_COUNTY[city_state][2]
                county_counts[fips] += 1
                total_mapped += 1
            else:
                city_lower = city.lower().split(",")[0].split("(")[0].strip()
                for key, value in CITY_TO_COUNTY.items():
                    key_city = key.split(",")[0].lower().strip()
                    key_state = key.split(",")[1].strip() if "," in key else ""
                    if city_lower == key_city and state == key_state:
                        county_counts[value[1] + value[2]] += 1
                        total_mapped += 1
                        break

MIN_INCIDENTS = 4
filtered_counts = {k: v for k, v in county_counts.items() if v >= MIN_INCIDENTS}

FIPS_DATA = {
    "17031": {"city": "Chicago", "unauthorized_pop": 369000},
    "06037": {"city": "Los Angeles", "unauthorized_pop": 1101000},
    "27053": {"city": "Minneapolis", "unauthorized_pop": 34000},
    "36061": {"city": "New York City", "unauthorized_pop": 571000},
    "41051": {"city": "Portland", "unauthorized_pop": 33000},
    "06075": {"city": "San Francisco", "unauthorized_pop": 42000},
    "53033": {"city": "Seattle", "unauthorized_pop": 124000},
    "34013": {"city": "Newark", "unauthorized_pop": 68000},
}

data = []
for fips, incidents in filtered_counts.items():
    if fips in FIPS_DATA:
        city = FIPS_DATA[fips]["city"]
        pop = FIPS_DATA[fips]["unauthorized_pop"]
        data.append({"city": city, "incidents": incidents, "unauthorized_pop": pop, "rate": (incidents / pop) * 100000})

top_pop = sum(FIPS_DATA[f]["unauthorized_pop"] for f in filtered_counts.keys() if f in FIPS_DATA)
other_incidents = total_mapped - sum(filtered_counts.values())
other_pop = 13738000 - top_pop
other_rate = (other_incidents / other_pop) * 100000
data.append({"city": "All Other
Counties", "incidents": other_incidents, "unauthorized_pop": other_pop, "rate": other_rate})
data_sorted = sorted(data, key=lambda x: -x["rate"])

minneapolis_rate = next(d["rate"] for d in data_sorted if d["city"] == "Minneapolis")
multiplier = minneapolis_rate / other_rate
print(f"Minneapolis is {multiplier:.1f}x higher than 3,135 other counties")

cities = [d["city"] for d in data_sorted]
rates = [d["rate"] for d in data_sorted]
raw_incidents = [d["incidents"] for d in data_sorted]
colors = ["#8B0000"] + ["#CD5C5C"] * (len(data_sorted) - 2) + ["#808080"]

fig, ax = plt.subplots(figsize=(18, 12))
bars = ax.barh(cities[::-1], rates[::-1], color=colors[::-1], edgecolor="black", linewidth=0.5)

for bar, rate in zip(bars, rates[::-1]):
    w = bar.get_width()
    ax.text(w - 0.5 if w > 5 else w + 0.5, bar.get_y() + bar.get_height()/2, f"{rate:.1f}", ha="right" if w > 5 else "left", va="center", fontsize=22, fontweight="bold", color="white" if w > 5 else "black")

for bar, inc in zip(bars, raw_incidents[::-1]):
    ax.text(65, bar.get_y() + bar.get_height()/2, f"({inc} incidents)", ha="left", va="center", fontsize=18, color="#555555")

ax.set_xlabel("Violent Confrontations per 100,000 Illegal Aliens", fontsize=24, fontweight="bold")
ax.set_title("ICE Violent Confrontations Adjusted by Illegal Alien Population
(Protesters, Journalists, Bystanders, Officers, US Citizens)", fontsize=28, fontweight="bold", pad=20)
ax.tick_params(axis="y", labelsize=24)
ax.tick_params(axis="x", labelsize=24)
ax.set_xlim(0, 75)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.annotate(f"Minneapolis rate is
{multiplier:.0f}x higher than
3,135 other counties", xy=(minneapolis_rate, len(data_sorted) - 1), xytext=(42, len(data_sorted) - 3.5), fontsize=20, fontweight="bold", color="#8B0000", arrowprops=dict(arrowstyle="->", color="#8B0000", lw=2), bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFF0F0", edgecolor="#8B0000"))

plt.tight_layout()
plt.savefig("ice_confrontations_adjusted_by_population.png", dpi=150, bbox_inches="tight", facecolor="white")
print("Saved: ice_confrontations_adjusted_by_population.png")
plt.close()
