"""
anilist/api.py

Handles all AniList GraphQL API queries and mutations:
- User lookup
- Fetching lists (public/private, anime/manga)
- Filtering by status/title
- SaveMediaListEntry mutations for restore
- Viewer info for token/account verification

Depends on: anilist/auth.py, anilist/ratelimit.py, anilist/formatter.py
"""

import requests
from anilist.ratelimit import handle_rate_limit
from anilist.formatter import filter_entries

ANILIST_API = "https://graphql.anilist.co"

def get_user_id(username):
    query = '''
    query ($name: String) {
        User(search: $name) { id }
    }
    '''
    variables = {'name': username}
    resp = requests.post(ANILIST_API, json={'query': query, 'variables': variables})
    if resp.status_code == 200:
        data = resp.json()
        uid = data.get('data', {}).get('User', {}).get('id')
        if uid:
            return uid
    raise Exception(f"Unable to find AniList user '{username}'.")

def get_viewer_info(token):
    """
    Returns dict { "id": ..., "username": ... } for authenticated user.
    """
    query = '''
    query { Viewer { id name } }
    '''
    headers = { "Authorization": f"Bearer {token}" }
    resp = requests.post(ANILIST_API, json={"query": query}, headers=headers)
    if resp.status_code == 200:
        viewer = resp.json()["data"]["Viewer"]
        return {"id": viewer["id"], "username": viewer["name"]}
    return None

def get_viewer_username(token):
    info = get_viewer_info(token)
    return info["username"] if info else None

def get_viewer_id(token):
    info = get_viewer_info(token)
    return info["id"] if info else None

def fetch_list(
    user_id,
    media_type,
    auth_token=None,
    statuses=None,
    title_sub=None
):
    """
    Fetches anime or manga list for a user.
    - If auth_token is given, fetches with user auth (can include private entries).
    - statuses: Optional list of status codes to filter (e.g. ["COMPLETED"])
    - title_sub: Optional substring filter for title (case-insensitive)
    Returns: entries (list of dicts)
    """
    query = '''
    query ($userId: Int, $type: MediaType) {
        MediaListCollection(userId: $userId, type: $type) {
            lists {
                entries {
                    status
                    score(format: POINT_10)
                    progress
                    progressVolumes
                    notes
                    private
                    startedAt { year month day }
                    completedAt { year month day }
                    media {
                        id
                        idMal
                        episodes
                        chapters
                        volumes
                        title { romaji }
                        type
                    }
                }
            }
        }
    }
    '''
    variables = {'userId': user_id, 'type': media_type}
    headers = {}
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    while True:
        resp = requests.post(ANILIST_API, json={'query': query, 'variables': variables}, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            lists = data["data"]["MediaListCollection"]["lists"]
            entries = [entry for lst in lists for entry in lst["entries"]]
            # Filter entries if needed
            filtered = filter_entries(entries, statuses, title_sub)
            return filtered
        else:
            # Handle rate limit or other errors
            handled = handle_rate_limit(resp)
            if not handled:
                raise Exception(f"Failed to fetch {media_type} list: HTTP {resp.status_code} {resp.text}")

def restore_entry(
    entry,
    media_type,
    auth_token
):
    """
    Restores a single entry using SaveMediaListEntry mutation.
    Returns: True if success, False otherwise.
    """
    mutation = '''
    mutation ($mediaId: Int, $status: MediaListStatus, $score: Float, $progress: Int, $progressVolumes: Int, $notes: String, $startedAt: FuzzyDateInput, $completedAt: FuzzyDateInput, $private: Boolean) {
      SaveMediaListEntry(
        mediaId: $mediaId,
        status: $status,
        score: $score,
        progress: $progress,
        progressVolumes: $progressVolumes,
        notes: $notes,
        startedAt: $startedAt,
        completedAt: $completedAt,
        private: $private
      ) {
        id
        status
      }
    }
    '''
    # Prepare variables from entry
    variables = {
        "mediaId": entry["media"]["id"],
        "status": entry.get("status"),
        "score": float(entry.get("score", 0)),
        "progress": entry.get("progress"),
        "progressVolumes": entry.get("progressVolumes"),
        "notes": entry.get("notes"),
        "private": entry.get("private"),
        "startedAt": entry.get("startedAt"),
        "completedAt": entry.get("completedAt"),
    }
    # Remove nulls (AniList API doesn't like nulls)
    variables = {k: v for k, v in variables.items() if v is not None}
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    while True:
        resp = requests.post(ANILIST_API, json={"query": mutation, "variables": variables}, headers=headers)
        if resp.status_code == 200:
            # Success!
            return True
        else:
            # Handle rate limit or other errors
            handled = handle_rate_limit(resp)
            if not handled:
                # Other errors: skip or raise
                return False

def test_token(token):
    """
    Verifies if an AniList OAuth token is valid.
    """
    query = '''
    query { Viewer { id name } }
    '''
    headers = { "Authorization": f"Bearer {token}" }
    resp = requests.post(ANILIST_API, json={"query": query}, headers=headers)
    return resp.status_code == 200
