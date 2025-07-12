"""
anilist/api.py

Handles all AniList GraphQL API queries and mutations:
- User lookup
- Fetching lists (public/private, anime/manga, with custom lists)
- Filtering by status/title
- SaveMediaListEntry mutations for restore
- Viewer info for token/account verification
- Creating custom lists if missing

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
                name
                isCustomList
                entries {
                    status
                    score(format: POINT_10)
                    progress
                    progressVolumes
                    notes
                    private
                    customLists
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
            # Fix customLists: ensure it's always a list, not a dict/object
            for entry in entries:
                cl = entry.get("customLists", None)
                # If customLists is a dict (old bug), convert to list of keys with True value
                if isinstance(cl, dict):
                    entry["customLists"] = [k for k, v in cl.items() if v]
                elif cl is None:
                    entry["customLists"] = []
            filtered = filter_entries(entries, statuses, title_sub)
            return filtered
        else:
            handled = handle_rate_limit(resp)
            if not handled:
                raise Exception(f"Failed to fetch {media_type} list: HTTP {resp.status_code} {resp.text}")

def get_custom_lists(auth_token, media_type):
    """
    Returns a set of existing custom list names for the user (for anime or manga).
    """
    query = '''
    query ($type: MediaType) {
        Viewer {
            mediaListOptions {
                %s {
                    customLists
                }
            }
        }
    }
    ''' % ("animeList" if media_type == "ANIME" else "mangaList")
    headers = { "Authorization": f"Bearer {auth_token}" }
    resp = requests.post(ANILIST_API, json={"query": query, "variables": {"type": media_type}}, headers=headers)
    if resp.status_code == 200:
        options = resp.json()["data"]["Viewer"]["mediaListOptions"]
        key = "animeList" if media_type == "ANIME" else "mangaList"
        return set(options[key]["customLists"] or [])
    return set()

def create_custom_list(auth_token, media_type, list_name):
    """
    Adds a custom list (by name) to the user's list options. Only adds if not present.
    """
    existing = get_custom_lists(auth_token, media_type)
    if list_name in existing:
        return True  # Already exists

    new_custom_lists = list(existing) + [list_name]
    mutation = '''
    mutation ($customLists: [String]) {
      SaveUserOptions(
        %s: { customLists: $customLists }
      ) {
        id
      }
    }
    ''' % ("animeList" if media_type == "ANIME" else "mangaList")
    variables = { "customLists": new_custom_lists }
    headers = { "Authorization": f"Bearer {auth_token}" }
    while True:
        resp = requests.post(ANILIST_API, json={"query": mutation, "variables": variables}, headers=headers)
        if resp.status_code == 200:
            return True
        handled = handle_rate_limit(resp)
        if not handled:
            return False

def restore_entry(
    entry,
    media_type,
    auth_token,
    auto_create_custom_lists=True
):
    """
    Restores a single entry using SaveMediaListEntry mutation.
    If entry has customLists and any doesn't exist, creates it first if auto_create_custom_lists is True.
    Returns: True if success, False otherwise.
    """
    # Accept either customLists (list), or customList (string, legacy)
    custom_lists = entry.get("customLists", [])
    custom_list = None
    if isinstance(custom_lists, list) and custom_lists:
        custom_list = custom_lists[0]  # Only one custom list can be set per mutation
    elif isinstance(custom_lists, str):
        custom_list = custom_lists
    elif entry.get("customList"):
        custom_list = entry.get("customList")
    if custom_list and auto_create_custom_lists:
        create_custom_list(auth_token, media_type, custom_list)

    mutation = '''
    mutation ($mediaId: Int, $status: MediaListStatus, $score: Float, $progress: Int, $progressVolumes: Int, $notes: String, $startedAt: FuzzyDateInput, $completedAt: FuzzyDateInput, $private: Boolean, $customList: String) {
      SaveMediaListEntry(
        mediaId: $mediaId,
        status: $status,
        score: $score,
        progress: $progress,
        progressVolumes: $progressVolumes,
        notes: $notes,
        startedAt: $startedAt,
        completedAt: $completedAt,
        private: $private,
        customList: $customList
      ) {
        id
        status
      }
    }
    '''
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
        "customList": custom_list,
    }
    variables = {k: v for k, v in variables.items() if v is not None}
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    while True:
        resp = requests.post(ANILIST_API, json={"query": mutation, "variables": variables}, headers=headers)
        if resp.status_code == 200:
            return True
        else:
            handled = handle_rate_limit(resp)
            if not handled:
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