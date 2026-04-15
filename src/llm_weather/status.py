# ABOUTME: Fetches provider status feeds (OpenAI, Anthropic, Google Cloud).
# ABOUTME: Parses Atom/RSS feeds and returns recent incidents for correlation with drift.

import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError

logger = logging.getLogger(__name__)

FEEDS = {
    "openai": {
        "url": "https://status.openai.com/history.atom",
        "provider": "OpenAI",
    },
    "anthropic": {
        "url": "https://status.anthropic.com/history.atom",
        "provider": "Anthropic",
    },
    "google": {
        "url": "https://status.cloud.google.com/en/feed.atom",
        "provider": "Google Cloud",
        "filter_terms": ["vertex", "gemini", "ai platform"],
    },
}

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def _parse_atom_date(date_str: str) -> datetime | None:
    """Parse an Atom date string to a timezone-aware datetime."""
    for fmt in [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ]:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def _fetch_feed(url: str, timeout: int = 15) -> str | None:
    """Fetch a feed URL, following redirects. Returns XML string or None."""
    try:
        req = Request(url, headers={"User-Agent": "llm-weather/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except (URLError, TimeoutError, OSError) as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return None


def _parse_atom_entries(xml_str: str, max_age_hours: int = 48) -> list[dict]:
    """Parse Atom feed XML and return entries within max_age_hours."""
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError as exc:
        logger.warning("Failed to parse Atom feed: %s", exc)
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    entries = []

    for entry in root.findall("atom:entry", ATOM_NS):
        title_el = entry.find("atom:title", ATOM_NS)
        updated_el = entry.find("atom:updated", ATOM_NS)
        content_el = entry.find("atom:content", ATOM_NS)
        link_el = entry.find("atom:link", ATOM_NS)

        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        updated_str = updated_el.text if updated_el is not None and updated_el.text else ""
        content = content_el.text.strip() if content_el is not None and content_el.text else ""
        link = link_el.get("href", "") if link_el is not None else ""

        updated = _parse_atom_date(updated_str)
        if updated and updated < cutoff:
            continue

        entries.append({
            "title": title,
            "updated": updated.isoformat() if updated else updated_str,
            "link": link,
            "content_snippet": content[:300] if content else "",
        })

    return entries


def fetch_provider_status(max_age_hours: int = 48) -> dict[str, list[dict]]:
    """Fetch recent incidents from all provider status feeds.

    Returns a dict keyed by provider slug with lists of incident dicts.
    Only includes providers with active/recent incidents.
    """
    results = {}

    for slug, feed_config in FEEDS.items():
        xml_str = _fetch_feed(feed_config["url"])
        if not xml_str:
            continue

        entries = _parse_atom_entries(xml_str, max_age_hours=max_age_hours)

        filter_terms = feed_config.get("filter_terms")
        if filter_terms:
            entries = [
                e for e in entries
                if any(
                    term in e["title"].lower() or term in e["content_snippet"].lower()
                    for term in filter_terms
                )
            ]

        if entries:
            for e in entries:
                e["provider"] = feed_config["provider"]
            results[slug] = entries

    return results


def status_for_frontmatter(provider_status: dict[str, list[dict]]) -> list[dict]:
    """Flatten provider status into a list suitable for Hugo frontmatter.

    Returns a list of dicts with provider, title, updated, and link fields.
    Strips content_snippet to keep frontmatter clean.
    """
    items = []
    for _slug, entries in provider_status.items():
        for entry in entries:
            items.append({
                "provider": entry["provider"],
                "title": entry["title"],
                "updated": entry["updated"],
                "link": entry["link"],
            })
    return items
