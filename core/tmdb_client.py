"""Fresh TMDb client implementation (simple and testable).

Provides:
- fetch_tmdb(path, params=None)
- normalize_movie(movie)
- get_popular_movies(page=1)
- get_top_rated_movies(page=1)

This module intentionally uses simple prints for debugging during development.
"""
from django.conf import settings
import requests


TMDB_API_KEY = getattr(settings, 'TMDB_API_KEY', None)
TMDB_BASE_URL = getattr(settings, 'TMDB_BASE_URL', 'https://api.themoviedb.org/3')
TMDB_IMAGE_BASE_URL = getattr(settings, 'TMDB_IMAGE_BASE_URL', 'https://image.tmdb.org/t/p')
REQUEST_TIMEOUT = 5


def fetch_tmdb(path, params=None):
    params = dict(params or {})
    params.update({'api_key': TMDB_API_KEY, 'language': 'tr-TR'})
    url = TMDB_BASE_URL.rstrip('/') + '/' + path.lstrip('/')
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    except Exception as e:
        print(f"[tmdb] Request error: {e}")
        return {}
    if resp.status_code != 200:
        print(f"[tmdb] Non-200 response for {resp.url}: {resp.status_code} - {resp.text}")
        return {}
    try:
        return resp.json()
    except Exception as e:
        print(f"[tmdb] JSON decode error for {resp.url}: {e}")
        return {}


def normalize_movie(movie):
    if not movie or not isinstance(movie, dict):
        return None
    poster_path = movie.get('poster_path')
    poster_url = f"{TMDB_IMAGE_BASE_URL}/w500{poster_path}" if poster_path else None
    return {
        'media_type': 'movie',
        'external_id': movie.get('id'),
        'title': movie.get('title') or movie.get('name') or '',
        'year': (movie.get('release_date') or '')[:4] if movie.get('release_date') else None,
        'poster_url': poster_url,
        'rating': movie.get('vote_average'),
    }


def get_popular_movies(page=1):
    if not TMDB_API_KEY:
        print('[tmdb] TMDB_API_KEY is not set in settings')
        return []
    data = fetch_tmdb('/movie/popular', {'page': page})
    results = data.get('results', []) if isinstance(data, dict) else []
    movies = [normalize_movie(m) for m in results if normalize_movie(m)]
    print('Popular movies count:', len(movies))
    if movies:
        try:
            print('Sample movie poster:', movies[0].get('poster_url'))
        except Exception:
            pass
    return movies


def get_top_rated_movies(page=1):
    if not TMDB_API_KEY:
        print('[tmdb] TMDB_API_KEY is not set in settings')
        return []
    data = fetch_tmdb('/movie/top_rated', {'page': page})
    results = data.get('results', []) if isinstance(data, dict) else []
    movies = [normalize_movie(m) for m in results if normalize_movie(m)]
    print('Top rated movies count:', len(movies))
    return movies


def search_movies(query, page=1):
    """Search TMDb for movies matching `query` and return normalized movie dicts.

    Returns a list of dicts in the same shape as get_popular_movies / get_top_rated_movies.
    """
    if not TMDB_API_KEY:
        print('[tmdb] TMDB_API_KEY is not set in settings')
        return []
    if not query:
        return []
    params = {'page': page, 'query': query, 'include_adult': False}
    data = fetch_tmdb('/search/movie', params)
    results = data.get('results', []) if isinstance(data, dict) else []
    movies = [normalize_movie(m) for m in results if normalize_movie(m)]
    print(f"Search '{query}' returned {len(movies)} movies (page {page})")
    return movies


def get_movie_details(movie_id):
    """Fetch detailed movie info including credits and normalize into expected dict."""
    if not TMDB_API_KEY or not movie_id:
        return {}
    data = fetch_tmdb(f'/movie/{movie_id}', {'append_to_response': 'videos'})
    credits = fetch_tmdb(f'/movie/{movie_id}/credits')
    director = None
    try:
        crew = credits.get('crew', []) if isinstance(credits, dict) else []
        for c in crew:
            if c.get('job') == 'Director':
                director = c.get('name')
                break
    except Exception:
        director = None

    poster_path = data.get('poster_path')
    poster_url = f"{TMDB_IMAGE_BASE_URL}/w780{poster_path}" if poster_path else None

    genres = [g.get('name') for g in data.get('genres', []) if isinstance(g, dict)] if data else []
    return {
        'media_type': 'movie',
        'external_id': data.get('id'),
        'title': data.get('title') or data.get('name'),
        'year': (data.get('release_date') or '')[:4] if data.get('release_date') else None,
        'runtime': data.get('runtime'),
        'director': director,
        'genres': genres,
        'overview': data.get('overview'),
        'poster_url': poster_url,
        'platform_rating': data.get('vote_average'),
    }
