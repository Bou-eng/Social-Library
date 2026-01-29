"""Simple Open Library client for subject-based popular books.

Provides:
- fetch_openlibrary(url, params=None)
- normalize_book_from_subject(work)
- get_popular_books(subject='fiction', limit=20)

This is intentionally small and prints debug info during development.
"""
import requests

OPENLIBRARY_BASE_URL = 'https://openlibrary.org'
REQUEST_TIMEOUT = 5


def fetch_openlibrary(url, params=None):
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    except Exception as e:
        print(f"[openlib] Request error: {e}")
        return {}
    if resp.status_code != 200:
        print(f"[openlib] Non-200 response for {resp.url}: {resp.status_code} - {resp.text}")
        return {}
    try:
        return resp.json()
    except Exception as e:
        print(f"[openlib] JSON decode error for {resp.url}: {e}")
        return {}


def normalize_book_from_subject(work):
    if not work or not isinstance(work, dict):
        return None
    cover_id = work.get('cover_id')
    cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None
    authors = work.get('authors') or []
    author_names = ', '.join(a.get('name') for a in authors if isinstance(a, dict) and a.get('name')) if authors else None
    return {
        'media_type': 'book',
        'external_id': work.get('key'),
        'title': work.get('title'),
        'authors': author_names,
        'year': work.get('first_publish_year'),
        'cover_url': cover_url,
    }


def get_popular_books(subject='fiction', limit=20):
    url = f"{OPENLIBRARY_BASE_URL}/subjects/{subject}.json"
    data = fetch_openlibrary(url, params={'limit': limit})
    works = data.get('works', []) if isinstance(data, dict) else []
    books = [normalize_book_from_subject(w) for w in works[:limit] if normalize_book_from_subject(w)]
    print('Popular books count:', len(books))
    if books:
        try:
            print('Sample book cover:', books[0].get('cover_url'))
        except Exception:
            pass
    return books


def normalize_book_from_search(doc):
    """Normalize a search doc from Open Library search.json to the same shape used elsewhere."""
    if not doc or not isinstance(doc, dict):
        return None
    cover_id = doc.get('cover_i') or doc.get('cover_id')
    cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None
    authors = doc.get('author_name') or []
    author_names = ', '.join(authors) if authors else None
    # docs may have 'key' as work key or 'edition_key' etc
    external_key = doc.get('key') or ("/works/" + (doc.get('work_id')[0] if doc.get('work_id') else ''))
    return {
        'media_type': 'book',
        'external_id': external_key,
        'title': doc.get('title'),
        'authors': author_names,
        'year': doc.get('first_publish_year'),
        'cover_url': cover_url,
    }


def search_books(query, limit=20, start_index=None, max_results=None):
    """Search Open Library for books matching `query`.

    Supports the simple (query, limit) call as well as older callers passing
    start_index/max_results. Returns a list of normalized book dicts.
    """
    if not query:
        return []
    # support legacy params
    if max_results:
        limit = max_results
    params = {'q': query, 'limit': limit}
    # OpenLibrary search.json endpoint
    url = f"{OPENLIBRARY_BASE_URL}/search.json"
    data = fetch_openlibrary(url, params=params)
    docs = data.get('docs', []) if isinstance(data, dict) else []
    # support slicing from start_index / max_results if provided (legacy callers)
    try:
        if max_results is not None and isinstance(start_index, int):
            slice_start = int(start_index)
            slice_end = slice_start + int(max_results)
            docs_slice = docs[slice_start:slice_end]
        elif start_index is not None and isinstance(start_index, int):
            slice_start = int(start_index)
            docs_slice = docs[slice_start:slice_start + int(limit)]
        else:
            docs_slice = docs[:limit]
    except Exception:
        docs_slice = docs[:limit]

    books = [normalize_book_from_search(d) for d in docs_slice if normalize_book_from_search(d)]
    print(f"OpenLibrary search '{query}' returned {len(books)} books")
    return books


def get_book_details(external_key):
    """Fetch book/work details for a work key like '/works/OL123W' or an id.

    Returns normalized dict similar to movie details.
    """
    if not external_key:
        return {}
    # ensure it starts with /works/
    key = external_key
    if not key.startswith('/works/') and not key.startswith('works/'):
        # try to handle simple ids
        key = '/works/' + key
    url = f"{OPENLIBRARY_BASE_URL}{key}.json"
    data = fetch_openlibrary(url)
    if not data:
        return {}
    # get description which may be dict or string
    desc = data.get('description')
    if isinstance(desc, dict):
        overview = desc.get('value')
    else:
        overview = desc
    authors = []
    try:
        author_entries = data.get('authors', [])
        for a in author_entries:
            if isinstance(a, dict) and a.get('author') and a['author'].get('key'):
                auth_data = fetch_openlibrary(f"{OPENLIBRARY_BASE_URL}{a['author']['key']}.json")
                if auth_data and auth_data.get('name'):
                    authors.append(auth_data.get('name'))
    except Exception:
        pass
    authors_str = ', '.join(authors) if authors else None
    cover_id = data.get('covers') and data.get('covers')[0] if data.get('covers') else None
    cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None
    subjects = data.get('subjects') or []

    return {
        'media_type': 'book',
        'external_id': key,
        'title': data.get('title'),
        'year': data.get('first_publish_date') or data.get('created', {}).get('value', '')[:4] if data.get('created') else None,
        'pages': data.get('number_of_pages') or None,
        'author': authors_str,
        'genres': subjects,
        'overview': overview,
        'cover_url': cover_url,
        'platform_rating': None,
    }
