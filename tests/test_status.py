# ABOUTME: Tests for the provider status feed fetching and parsing.
# ABOUTME: Covers Atom XML parsing, date filtering, content filtering, and frontmatter formatting.

from datetime import datetime, timezone, timedelta

from llm_weather.status import (
    _parse_atom_date,
    _parse_atom_entries,
    status_for_frontmatter,
)


def _make_atom_feed(entries_xml: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Test Status</title>
  {entries_xml}
</feed>"""


def _make_entry(title: str, updated: str, content: str = "", link: str = "") -> str:
    link_xml = f'<link href="{link}"/>' if link else ""
    content_xml = f"<content>{content}</content>" if content else ""
    return f"""<entry>
  <title>{title}</title>
  <updated>{updated}</updated>
  {link_xml}
  {content_xml}
</entry>"""


class TestParseAtomDate:
    def test_iso_with_offset(self):
        dt = _parse_atom_date("2026-04-14T12:00:00+00:00")
        assert dt is not None
        assert dt.year == 2026
        assert dt.tzinfo is not None

    def test_iso_with_z(self):
        dt = _parse_atom_date("2026-04-14T12:00:00Z")
        assert dt is not None
        assert dt.tzinfo == timezone.utc

    def test_invalid_returns_none(self):
        assert _parse_atom_date("not-a-date") is None

    def test_with_microseconds(self):
        dt = _parse_atom_date("2026-04-14T12:00:00.123456+00:00")
        assert dt is not None


class TestParseAtomEntries:
    def test_recent_entry_included(self):
        now = datetime.now(timezone.utc)
        entry = _make_entry("API down", now.strftime("%Y-%m-%dT%H:%M:%S+00:00"))
        feed = _make_atom_feed(entry)
        entries = _parse_atom_entries(feed, max_age_hours=1)
        assert len(entries) == 1
        assert entries[0]["title"] == "API down"

    def test_old_entry_excluded(self):
        old = datetime.now(timezone.utc) - timedelta(hours=72)
        entry = _make_entry("Old issue", old.strftime("%Y-%m-%dT%H:%M:%S+00:00"))
        feed = _make_atom_feed(entry)
        entries = _parse_atom_entries(feed, max_age_hours=48)
        assert len(entries) == 0

    def test_link_extracted(self):
        now = datetime.now(timezone.utc)
        entry = _make_entry(
            "Test",
            now.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            link="https://status.example.com/1",
        )
        feed = _make_atom_feed(entry)
        entries = _parse_atom_entries(feed, max_age_hours=1)
        assert entries[0]["link"] == "https://status.example.com/1"

    def test_content_snippet_truncated(self):
        now = datetime.now(timezone.utc)
        long_content = "x" * 500
        entry = _make_entry(
            "Test",
            now.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            content=long_content,
        )
        feed = _make_atom_feed(entry)
        entries = _parse_atom_entries(feed, max_age_hours=1)
        assert len(entries[0]["content_snippet"]) == 300

    def test_invalid_xml_returns_empty(self):
        entries = _parse_atom_entries("not xml at all")
        assert entries == []


class TestStatusForFrontmatter:
    def test_flattens_providers(self):
        status = {
            "openai": [
                {
                    "provider": "OpenAI",
                    "title": "API errors",
                    "updated": "2026-04-14T12:00:00+00:00",
                    "link": "https://status.openai.com/1",
                    "content_snippet": "some details",
                },
            ],
            "anthropic": [
                {
                    "provider": "Anthropic",
                    "title": "Elevated errors",
                    "updated": "2026-04-14T11:00:00+00:00",
                    "link": "https://status.anthropic.com/1",
                    "content_snippet": "some details",
                },
            ],
        }
        items = status_for_frontmatter(status)
        assert len(items) == 2
        assert all("content_snippet" not in item for item in items)
        providers = {item["provider"] for item in items}
        assert providers == {"OpenAI", "Anthropic"}

    def test_empty_status(self):
        assert status_for_frontmatter({}) == []
