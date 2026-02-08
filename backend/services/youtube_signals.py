"""
YouTube Trending Signals — live alternative-sentiment data.

Pulls the current trending videos for a country via the YouTube Data API,
computes high-level content-mix features, and returns a plain-text summary
that can be injected into the LLM prompt as "Sephira social intelligence".
"""
import os
import re
import requests
from collections import Counter
from typing import Dict, Any, Optional

# ---------------------------------------------------------------------------
# Country name → YouTube region code mapping (24 priority countries)
# ---------------------------------------------------------------------------
COUNTRY_TO_REGION: Dict[str, str] = {
    "united states": "US",
    "china": "CN",         # note: YT may be blocked; fallback handled
    "japan": "JP",
    "germany": "DE",
    "united kingdom": "GB",
    "india": "IN",
    "france": "FR",
    "italy": "IT",
    "canada": "CA",
    "south korea": "KR",
    "brazil": "BR",
    "australia": "AU",
    "russia": "RU",
    "mexico": "MX",
    "indonesia": "ID",
    "saudi arabia": "SA",
    "turkey": "TR",
    "taiwan": "TW",
    "poland": "PL",
    "argentina": "AR",
    "south africa": "ZA",
    "nigeria": "NG",
    "israel": "IL",
    "egypt": "EG",
}

# YouTube category IDs
ENTERTAINMENT_CATS = {"23", "24"}   # Comedy, Entertainment
EDU_CATS = {"26", "27"}             # Howto & Style, Education
NEWS_CATS = {"25"}                  # News & Politics

# Keyword patterns
_SHORTS_RE = re.compile(r"(#shorts\b|\bshorts\b)", re.IGNORECASE)
_ESCAPISM_RE = re.compile(
    r"(asmr|relax|sleep|lofi|lo-fi|mukbang|minecraft|fortnite|roblox|"
    r"valorant|gta|gaming|kpop|bts|prank|reaction|compilation|memes|funny|tiktok)",
    re.IGNORECASE,
)
_SELFHELP_RE = re.compile(
    r"(self[- ]?help|motivation|mindfulness|meditat|anxiety|depression|"
    r"therapy|gratitude|productivity|discipline|habits|mental health|stress)",
    re.IGNORECASE,
)
_CRISIS_RE = re.compile(
    r"(news|breaking|election|politic|war|attack|terror|"
    r"earthquake|flood|storm|wildfire|pandemic|"
    r"inflation|recession|crash|tragedy|protest|coup|sanction)",
    re.IGNORECASE,
)


def _parse_duration_iso(iso: str) -> int:
    """PT1H2M3S → seconds."""
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s


def _matches(pattern: re.Pattern, title: str, tags: list) -> bool:
    text = f"{title} {' '.join(tags or [])}"
    return bool(pattern.search(text))


def fetch_youtube_signals(country: str) -> Optional[Dict[str, Any]]:
    """
    Call the YouTube Data API for trending videos in *country* and return
    computed content-mix features.  Returns None if the API key is missing
    or the call fails.
    """
    api_key = os.getenv("YT_API_KEY")
    if not api_key:
        return None

    region = COUNTRY_TO_REGION.get(country.lower())
    if not region:
        return None

    try:
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet,contentDetails",
                "chart": "mostPopular",
                "regionCode": region,
                "maxResults": 50,
                "key": api_key,
            },
            timeout=8,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except Exception as e:
        print(f"YouTube API error for {country}: {e}")
        return None

    if not items:
        return None

    n = len(items)
    cats = []
    shorts_count = 0
    escapism_count = 0
    selfhelp_count = 0
    crisis_count = 0

    for item in items:
        snippet = item.get("snippet", {})
        content = item.get("contentDetails", {})

        cat = snippet.get("categoryId", "0")
        title = snippet.get("title", "")
        tags = snippet.get("tags", [])
        dur = _parse_duration_iso(content.get("duration", ""))

        cats.append(cat)

        if dur <= 60 or _matches(_SHORTS_RE, title, tags):
            shorts_count += 1
        if _matches(_ESCAPISM_RE, title, tags):
            escapism_count += 1
        if _matches(_SELFHELP_RE, title, tags):
            selfhelp_count += 1
        if _matches(_CRISIS_RE, title, tags):
            crisis_count += 1

    cat_counts = Counter(cats)
    news_share = sum(cat_counts.get(c, 0) for c in NEWS_CATS) / n
    entertainment_share = sum(cat_counts.get(c, 0) for c in ENTERTAINMENT_CATS) / n
    edu_share = sum(cat_counts.get(c, 0) for c in EDU_CATS) / n

    return {
        "region": region,
        "videos_sampled": n,
        "news_share": round(news_share, 3),
        "entertainment_share": round(entertainment_share, 3),
        "education_share": round(edu_share, 3),
        "shorts_share": round(shorts_count / n, 3),
        "escapism_share": round(escapism_count / n, 3),
        "selfhelp_share": round(selfhelp_count / n, 3),
        "crisis_share": round(crisis_count / n, 3),
    }


def format_youtube_context(signals: Dict[str, Any], country: str) -> str:
    """Turn raw signals dict into a prose paragraph for prompt injection."""
    parts = [f"Sephira social intelligence for {country} (YouTube trending analysis, {signals['videos_sampled']} videos):"]

    news = signals["news_share"]
    esc = signals["escapism_share"]
    crisis = signals["crisis_share"]
    selfhelp = signals["selfhelp_share"]
    shorts = signals["shorts_share"]
    ent = signals["entertainment_share"]

    parts.append(
        f"News/politics content is {news:.0%} of trending, "
        f"crisis-related keywords appear in {crisis:.0%} of titles/tags, "
        f"escapism content is {esc:.0%}, "
        f"self-help/mental-health content is {selfhelp:.0%}, "
        f"entertainment is {ent:.0%}, "
        f"short-form is {shorts:.0%}."
    )

    # Interpretive flags
    if crisis > 0.15:
        parts.append("Elevated crisis-content signal — population attention is focused on conflict, disaster, or political instability.")
    if esc > 0.35:
        parts.append("High escapism signal — consistent with economic pessimism or social fatigue.")
    if selfhelp > 0.10:
        parts.append("Elevated self-help signal — social stress indicators rising.")
    if news < 0.03 and crisis < 0.05:
        parts.append("Low news engagement — suggests complacency or stability.")

    return " ".join(parts)
