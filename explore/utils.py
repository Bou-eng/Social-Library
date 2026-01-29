from django.conf import settings
from django.core.cache import cache

# Import requests lazily and provide a helpful error if missing
try:
    import requests
    _HAS_REQUESTS = True
except Exception:
    requests = None
    _HAS_REQUESTS = False

def _ensure_requests():
    if not _HAS_REQUESTS:
        raise RuntimeError(
            "The 'requests' library is required by explore.utils.\n"
            "Please install dependencies: run `pip install -r requirements.txt` from the project root."
        )

# Simple cache helper: cache API results for `timeout` seconds
def cache_get(key):
    return cache.get(key)

def cache_set(key, value, timeout=60*30):
    cache.set(key, value, timeout)

def search_tmdb(query, page=1):
    """Search TMDb for movies by query. Returns list of dicts.
    Uses TMDB_API_KEY from settings.
    """
    if not query:
        return []
    api_key = getattr(settings, 'TMDB_API_KEY', None)
    if not api_key:
        return []
    cache_key = f"tmdb:search:{query}:{page}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    url = 'https://api.themoviedb.org/3/search/movie'
    params = {'api_key': api_key, 'query': query, 'page': page, 'include_adult': False}
    _ensure_requests()
    resp = requests.get(url, params=params, timeout=5)
    if resp.status_code != 200:
        return []
    data = resp.json()
    results = []
    for item in data.get('results', []):
        results.append({
            'id': item.get('id'),
            'type': 'movie',
            'title': item.get('title') or item.get('name'),
            'year': (item.get('release_date') or '')[:4],
            'poster_path': item.get('poster_path'),
            'overview': item.get('overview'),
            'rating': item.get('vote_average'),
            'raw': item,
        })
    cache_set(cache_key, results)
    return results

