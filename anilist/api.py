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
            filtered = filter_entries(entries, statuses, title_sub)
            return filtered
        else:
            handled = handle_rate_limit(resp)
            if not handled:
                raise Exception(f"Failed to fetch {media_type} list: HTTP {resp.status_code} {resp.text}")

def get_custom_lists(auth_token, media_type):
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
    existing = get_custom_lists(auth_token, media_type)
    if list_name in existing:
        return True

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
    # New: handle multiple custom lists (AniList API only allows one per mutation)
    custom_lists = entry.get("customLists", []) or []
    # Use first custom list if present
    custom_list = custom_lists[0] if custom_lists else None
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
    query = '''
    query { Viewer { id name } }
    '''
    headers = { "Authorization": f"Bearer {token}" }
    resp = requests.post(ANILIST_API, json={"query": query}, headers=headers)
    return resp.status_code == 200