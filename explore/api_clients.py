"""
Exploration API helpers: delegates TMDb movie calls to core.tmdb_client and
implements Open Library book search / subject endpoints.
"""
from django.conf import settings
from django.core.cache import cache
import logging

from core.tmdb_client import get_popular_movies as tmdb_get_popular_movies, search_movies as tmdb_search_movies

try:
    import requests
except Exception:
    requests = None

logger = logging.getLogger(__name__)

# Timeouts and caching
REQUEST_TIMEOUT = 5
CACHE_TIMEOUT_POPULAR = 60 * 30  # 30 minutes
CACHE_TIMEOUT_SEARCH = 60 * 10   # 10 minutes

OPENLIB_SEARCH = 'https://openlibrary.org/search.json'
OPENLIB_SUBJECT = 'https://openlibrary.org/subjects/{subject}.json'


def _ensure_requests():
    if not requests:
        raise RuntimeError("The 'requests' library is required. Install via 'pip install requests'.")


def _cache_get(key):
    return cache.get(key)


def _cache_set(key, value, timeout):
    cache.set(key, value, timeout)


# --- Movie helpers (delegate to core.tmdb_client) ---

def get_popular_movies(page=1):
    try:
        return tmdb_get_popular_movies(page=page)
    except Exception:
        logger.exception('Error fetching popular movies from TMDb')
        return []


def search_movies(query, page=1):
    try:
        return tmdb_search_movies(query, page=page)
    except Exception:
        logger.exception('Error searching movies on TMDb')
        return []


def get_top_rated_movies(page=1):
    try:
        from core.tmdb_client import get_top_rated_movies as _get_top
        return _get_top(page=page)
    except Exception:
        logger.exception('Error fetching top rated movies from TMDb')
        return []


# --- Open Library (books) ---

def search_books(query, start_index=0, max_results=20):
    """Search Open Library and normalize docs into book dicts."""
    if not query:
        return []
    _ensure_requests()
    cache_key = f"openlib:search:{query}:{start_index}:{max_results}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    params = {'q': query, 'limit': max_results, 'offset': start_index}
    try:
        resp = requests.get(OPENLIB_SEARCH, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        try:
            data = resp.json()
        except Exception:
            data = {}
        print(f"[openlib] SEARCH {resp.url} {resp.status_code} results={len(data.get('docs', []))}")
        if resp.status_code != 200:
            print(f"[openlib] Error response: {resp.text}")
    except Exception as e:
        logger.exception('Open Library search failed: %s', e)
        return []

    results = []
    for doc in data.get('docs', []):
        cover_i = doc.get('cover_i')
        cover_url = f"https://covers.openlibrary.org/b/id/{cover_i}-M.jpg" if cover_i else None
        authors = doc.get('author_name') or []
        results.append({
            'media_type': 'book',
            'external_id': doc.get('key'),
            'title': doc.get('title') or '',
            'authors': ', '.join(authors) if authors else '',
            'year': doc.get('first_publish_year'),
            'description': None,
            'page_count': doc.get('number_of_pages_median'),
            'cover_url': cover_url,
            'raw': doc,
        })

    _cache_set(cache_key, results, CACHE_TIMEOUT_SEARCH)
    return results


def get_popular_books(subject='fiction', limit=20):
    """Fetch popular books using Open Library subjects API (works list)."""
    _ensure_requests()
    cache_key = f"openlib:subject:{subject}:{limit}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        resp = requests.get(OPENLIB_SUBJECT.format(subject=subject), params={'limit': limit}, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        try:
            data = resp.json()
        except Exception:
            data = {}
        print(f"[openlib] SUBJECT {resp.url} {resp.status_code} works={len(data.get('works', []))}")
        if resp.status_code != 200:
            print(f"[openlib] Error response: {resp.text}")
    except Exception as e:
        logger.exception('Open Library subject fetch failed: %s', e)
        return []

    results = []
    for work in data.get('works', [])[:limit]:
        cover_id = work.get('cover_id')
        cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None
        authors = work.get('authors') or []
        author_names = [a.get('name') for a in authors if isinstance(a, dict) and a.get('name')]
        results.append({
            'media_type': 'book',
            'external_id': work.get('key'),
            'title': work.get('title') or '',
            'authors': ', '.join(author_names) if author_names else '',
            'year': work.get('first_publish_year'),
            'description': None,
            'page_count': None,
            'cover_url': cover_url,
            'raw': work,
        })

    _cache_set(cache_key, results, CACHE_TIMEOUT_POPULAR)
    return results
