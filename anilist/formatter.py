"""
anilist/formatter.py

Formats AniList entries for backup/restore.
- Filters by status/title
- Ensures JSON structure is uniform for export/import

Can be extended for future format options.
"""

def filter_entries(entries, statuses=None, title=None):
    """
    Filter entries by statuses (list of codes) and/or substring in title (case-insensitive).
    """
    if not entries:
        return []
    filtered = []
    for entry in entries:
        if statuses and entry.get("status") not in statuses:
            continue
        if title:
            t = entry.get("media", {}).get("title", {}).get("romaji", "")
            if title.lower() not in t.lower():
                continue
        filtered.append(entry)
    return filtered