from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Avg, Count
from accounts.models import Activity
from core.tmdb_client import get_popular_movies, get_top_rated_movies, search_movies
from core.openlibrary_client import get_popular_books, search_books
from core.tmdb_client import get_movie_details
from core.openlibrary_client import get_book_details
import logging
logger = logging.getLogger(__name__)
from django.core.paginator import Paginator


def _platform_top_rated(limit=12, min_votes=3):
    # Aggregate average ratings per content (content_type, content_id)
    qs = Activity.objects.filter(type='rating').values('content_type', 'content_id').annotate(avg=Avg('rating'), cnt=Count('rating')).filter(cnt__gte=min_votes).order_by('-avg')[:limit]
    items = []
    for row in qs:
        items.append({
            'content_type': row['content_type'],
            'content_id': row['content_id'],
            'avg_rating': row['avg'],
            'votes': row['cnt'],
        })
    return items


def _platform_most_popular(limit=12):
    # Popular by number of activities (reviews + ratings)
    qs = Activity.objects.values('content_type', 'content_id').annotate(total=Count('id')).order_by('-total')[:limit]
    items = []
    for row in qs:
        items.append({
            'content_type': row['content_type'],
            'content_id': row['content_id'],
            'score': row['total'],
        })
    return items


def explore_view(request):
    # Simple wiring: call fresh clients and pass three keys to template
    try:
        top_rated_items = get_top_rated_movies(page=1)
    except Exception as e:
        logger.exception('Error fetching top rated movies: %s', e)
        top_rated_items = []

    try:
        popular_movies = get_popular_movies(page=1)
    except Exception as e:
        logger.exception('Error fetching popular movies: %s', e)
        popular_movies = []

    try:
        popular_books = get_popular_books()
    except Exception as e:
        logger.exception('Error fetching popular books: %s', e)
        popular_books = []
    # Search handling: read 'q' from GET and perform search using TMDb client
    query = request.GET.get('q', '').strip()
    search_results = []
    if query:
        try:
            search_results = search_movies(query, page=int(request.GET.get('page', 1)))
        except Exception:
            logger.exception('Error searching TMDb for query: %s', query)
            search_results = []
    # Book search (Open Library)
    book_search_results = []
    if query:
        try:
            # keep simple signature; search_books supports legacy params too
            book_search_results = search_books(query, limit=20)
        except Exception:
            logger.exception('Error searching OpenLibrary for query: %s', query)
            book_search_results = []

    # --- Filtering: read GET filter params and apply to fetched lists ---
    media_type = request.GET.get('type', 'all') or 'all'
    year_from = request.GET.get('year_from') or request.GET.get('year') or None
    year_to = request.GET.get('year_to') or None
    rating_band = request.GET.get('rating_band') or None

    def _to_int(v):
        try:
            return int(v)
        except Exception:
            return None

    def _to_float(v):
        try:
            return float(v)
        except Exception:
            return None

    yf = _to_int(year_from)
    yt = _to_int(year_to)
    
    # Parse rating band into min/max
    rating_min = None
    rating_max = None
    if rating_band == '2-5':
        rating_min, rating_max = 2.0, 5.0
    elif rating_band == '5-7':
        rating_min, rating_max = 5.0, 7.0
    elif rating_band == '7+':
        rating_min, rating_max = 7.0, None
    
    # Log filter values for debugging
    if yf:
        logger.info(f'Explore: applying year_from filter >= {yf}')
    if rating_band:
        logger.info(f'Explore: applying rating_band filter {rating_band}')

    def apply_filters(items, year_from=None, year_to=None, rating_min=None, rating_max=None, apply_rating=True):
        if not items:
            return []
        out = []
        for it in items:
            year = it.get('year')
            rating = it.get('rating')
            
            # normalize year - handle string, int, and various formats
            year_val = None
            if year is not None:
                try:
                    # Try to extract year from string like "2020" or "2020-01-01"
                    year_str = str(year).strip()
                    if year_str:
                        # If it contains a hyphen (date format), take first part
                        if '-' in year_str:
                            year_str = year_str.split('-')[0]
                        # Remove any non-digit characters
                        year_str = ''.join(c for c in year_str if c.isdigit())
                        if year_str and len(year_str) == 4:  # valid 4-digit year
                            year_val = int(year_str)
                except Exception:
                    year_val = None

            # Apply year_from filter: only keep items with year >= year_from
            # If item has no valid year and year filter is active, include it (don't filter out items with missing data)
            if year_from is not None and year_val is not None and year_val < year_from:
                continue
                
            # Apply year_to filter: only keep items with year <= year_to
            if year_to is not None and year_val is not None and year_val > year_to:
                continue
                
            # Apply rating filter (band logic: min <= rating <= max)
            if apply_rating and (rating_min is not None or rating_max is not None):
                if rating is None:
                    continue  # exclude items without rating when filtering by rating
                try:
                    rating_val = float(rating)
                    if rating_min is not None and rating_val < rating_min:
                        continue
                    if rating_max is not None and rating_val > rating_max:
                        continue
                except (TypeError, ValueError):
                    continue  # exclude items with invalid rating
                    
            out.append(it)
        return out

    # initial copies
    filtered_top_rated = list(top_rated_items) if top_rated_items else []
    filtered_popular_movies = list(popular_movies) if popular_movies else []
    filtered_popular_books = list(popular_books) if popular_books else []
    filtered_movie_search_results = list(search_results) if search_results else []
    filtered_book_search_results = list(book_search_results) if book_search_results else []

    # filter by media type
    if media_type == 'movie':
        filtered_popular_books = []
        filtered_book_search_results = []
    elif media_type == 'book':
        filtered_popular_movies = []
        filtered_movie_search_results = []
        filtered_top_rated = []

    # Check if books have ratings (Open Library typically doesn't provide ratings)
    use_rating_for_books = False
    if filtered_popular_books:
        use_rating_for_books = any(b.get('rating') is not None for b in filtered_popular_books[:5])
    
    # Determine if rating filter should be disabled
    rating_disabled = (media_type == 'book' and not use_rating_for_books)

    # apply year/rating filters
    # Year filter applies to all items (movies and books)
    # Rating filter: for movies always, for books only if they have ratings
    
    # Apply to movies (always apply both year and rating filters)
    filtered_top_rated = apply_filters(filtered_top_rated, yf, yt, rating_min, rating_max, apply_rating=True)
    filtered_popular_movies = apply_filters(filtered_popular_movies, yf, yt, rating_min, rating_max, apply_rating=True)
    filtered_movie_search_results = apply_filters(filtered_movie_search_results, yf, yt, rating_min, rating_max, apply_rating=True)
    
    # Apply to books (always apply year filter, conditionally apply rating filter)
    apply_rating_to_books = use_rating_for_books and rating_band
    filtered_popular_books = apply_filters(filtered_popular_books, yf, yt, rating_min, rating_max, apply_rating=apply_rating_to_books)
    filtered_book_search_results = apply_filters(filtered_book_search_results, yf, yt, rating_min, rating_max, apply_rating=apply_rating_to_books)

    context = {
        'top_rated_items': filtered_top_rated,
        'popular_movies': filtered_popular_movies,
        'popular_books': filtered_popular_books,
        'search_query': query,
        'search_results': filtered_movie_search_results,
        'book_search_results': filtered_book_search_results,
        # echo filters so template can preserve values
        'filter_type': media_type,
        'filter_year_from': year_from,
        'filter_year_to': year_to,
        'filter_rating_band': rating_band,
        'rating_disabled': rating_disabled,
    }
    # include user's custom lists so the Explore modal can show "Özel listeye ekle"
    custom_lists = []
    try:
        if request.user.is_authenticated:
            from accounts.models import CustomList
            custom_lists = list(CustomList.objects.filter(user=request.user).order_by('-created_at')[:50])
    except Exception:
        # If migrations aren't applied or DB access fails, leave custom_lists empty
        custom_lists = []
    context['custom_lists'] = custom_lists
    return render(request, 'explore/explore.html', context)


def get_item_details(request):
    """AJAX endpoint: /explore/item-details/?media_type=movie&id=123

    Returns normalized details for movie or book.
    """
    from django.http import JsonResponse
    media_type = request.GET.get('media_type')
    item_id = request.GET.get('id')
    if not media_type or not item_id:
        return JsonResponse({'error': 'media_type and id required'}, status=400)
    try:
        if media_type == 'movie':
            data = get_movie_details(item_id)
        else:
            data = get_book_details(item_id)
        # include user's saved state and available custom lists if authenticated
        user_state = None
        custom_lists_serialized = []
        try:
            if request.user.is_authenticated:
                from accounts.models import LibraryItem, CustomListItem, CustomList
                li = LibraryItem.objects.filter(user=request.user, media_type=media_type, item_id=str(item_id)).first()
                if li:
                    user_state = {'status': li.status, 'rating': li.rating, 'library_item_pk': li.pk}
                # check if item exists in any custom list for this user
                cli = CustomListItem.objects.filter(item_id=str(item_id), media_type=media_type, custom_list__user=request.user).first()
                if cli:
                    user_state = user_state or {}
                    user_state['custom_list_item_pk'] = cli.pk
                    user_state['custom_list_id'] = cli.custom_list_id
                # fetch user's custom lists for the select
                cls = CustomList.objects.filter(user=request.user).order_by('-created_at')[:50]
                for c in cls:
                    custom_lists_serialized.append({'id': c.id, 'name': c.name, 'emoji': c.emoji})
        except Exception:
            # ignore DB issues
            user_state = user_state or None

        return JsonResponse({'ok': True, 'item': data, 'user_state': user_state, 'custom_lists': custom_lists_serialized})
    except Exception as e:
        logger.exception('Error fetching item details: %s', e)
        return JsonResponse({'ok': False, 'error': 'fetch error'})


from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


@login_required
@require_POST
def save_item_preferences(request):
    """Save user preferences from the Explore modal.

    Expects POST form data (or JSON): media_type, item_id, status, rating, custom_list_id
    """
    from django.http import JsonResponse
    from accounts.models import LibraryItem, CustomListItem, CustomList

    media_type = request.POST.get('media_type') or request.POST.get('mediaType')
    item_id = request.POST.get('item_id') or request.POST.get('itemId')
    status = request.POST.get('status')
    rating = request.POST.get('rating')
    custom_list_id = request.POST.get('custom_list_id')

    if not media_type or not item_id:
        return JsonResponse({'ok': False, 'error': 'media_type and item_id required'}, status=400)

    # validate rating
    try:
        rating_val = int(rating) if rating not in (None, '') else None
        if rating_val is not None and (rating_val < 1 or rating_val > 10):
            return JsonResponse({'ok': False, 'error': 'rating out of range'}, status=400)
    except Exception:
        return JsonResponse({'ok': False, 'error': 'invalid rating'}, status=400)

    # update or create LibraryItem
    li, created = LibraryItem.objects.update_or_create(
        user=request.user,
        media_type=media_type,
        item_id=str(item_id),
        defaults={
            'status': status or '',
            'title': request.POST.get('title') or '',
            'cover_url': request.POST.get('cover_url') or '',
            'rating': rating_val,
        }
    )

    # handle custom list addition
    added_to_list = None
    if custom_list_id:
        try:
            cl = CustomList.objects.get(pk=custom_list_id, user=request.user)
            # create or update CustomListItem
            CustomListItem.objects.update_or_create(
                custom_list=cl,
                item_id=str(item_id),
                defaults={
                    'title': request.POST.get('title') or '',
                    'cover_url': request.POST.get('cover_url') or '',
                    'media_type': media_type,
                }
            )
            added_to_list = cl.id
        except CustomList.DoesNotExist:
            added_to_list = None

    # create or update an Activity entry for this rating
    try:
        try:
            title = request.POST.get('title') or ''
            cover = request.POST.get('cover_url') or ''
            year = request.POST.get('year') or ''
        except Exception:
            title = ''
            cover = ''
            year = ''
        Activity.objects.update_or_create(
            user=request.user,
            content_type=media_type,
            content_id=str(item_id),
            type='rating',
            defaults={
                'rating': rating_val,
                'review': '',
                'title': title,
                'cover_url': cover,
                'year': year,
            }
        )
    except Exception:
        # do not fail the main request if activity logging fails
        logger.exception('Could not record rating activity')

    return JsonResponse({'ok': True, 'library_item_id': li.id, 'added_to_list': added_to_list, 'status': li.status, 'rating': li.rating})




@login_required
@require_POST
def save_comment(request):
    """Save a user comment via POST JSON.

    Expects JSON: { media_type, item_id, comment }
    Returns { success: true } on success.
    """
    from django.http import JsonResponse
    import json
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        payload = {}

    media_type = payload.get('media_type') or request.POST.get('media_type')
    item_id = payload.get('item_id') or request.POST.get('item_id')
    comment_text = payload.get('comment') or request.POST.get('comment')

    if not media_type or not item_id or not comment_text:
        return JsonResponse({'success': False, 'error': 'media_type, item_id and comment required'}, status=400)

    # optional length limit
    if isinstance(comment_text, str) and len(comment_text) > 500:
        return JsonResponse({'success': False, 'error': 'comment too long'}, status=400)

    try:
        from accounts.models import ItemComment
        ic = ItemComment.objects.create(user=request.user, media_type=media_type, item_id=str(item_id), comment=comment_text)
        # also create/update Activity for this comment (review)
        try:
            title = payload.get('title') or ''
            cover = payload.get('cover_url') or ''
            year = payload.get('year') or ''
        except Exception:
            title = ''
            cover = ''
            year = ''
        try:
            Activity.objects.update_or_create(
                user=request.user,
                content_type=media_type,
                content_id=str(item_id),
                type='review',
                defaults={
                    'review': comment_text,
                    'rating': None,
                    'title': title,
                    'cover_url': cover,
                    'year': year,
                }
            )
        except Exception:
            logger.exception('Could not record comment activity')
        return JsonResponse({'success': True})
    except Exception as e:
        logger.exception('Error saving comment: %s', e)
        return JsonResponse({'success': False, 'error': 'save error'}, status=500)


@require_GET
def explore_search(request):
    q = request.GET.get('q', '').strip()
    ctype = request.GET.get('type', 'movie')
    genre = request.GET.get('genre')
    year = request.GET.get('year')
    rating_band = request.GET.get('rating_band')
    page = int(request.GET.get('page', 1))
    
    # Parse rating band
    rating_min = None
    rating_max = None
    if rating_band == '2-5':
        rating_min, rating_max = 2.0, 5.0
    elif rating_band == '5-7':
        rating_min, rating_max = 5.0, 7.0
    elif rating_band == '7+':
        rating_min, rating_max = 7.0, None

    results = []
    if ctype == 'book':
        try:
            results = search_books(q, start_index=(page-1)*20, max_results=20)
        except Exception:
            results = []
    else:
        try:
            results = search_movies(q, page=page)
        except Exception:
            results = []

    # Apply simple filters on results list
    def matches_filters(item):
        if genre and genre not in ('', 'all'):
            g = item.get('raw', {})
            # for TMDb 'genre_ids' or for books categories
            if item.get('type') == 'movie':
                gids = g.get('genre_ids', [])
                # cannot match named genre reliably; skip strict check
            else:
                cats = item.get('categories', [])
                if genre.lower() not in [c.lower() for c in cats]:
                    return False
        
        # Apply year filter: item.year >= entered_year
        if year:
            try:
                year_int = int(year)
                item_year = item.get('year')
                if item_year:
                    # Extract year from string like "2020" or "2020-01-01"
                    year_str = str(item_year).strip()
                    if '-' in year_str:
                        year_str = year_str.split('-')[0]
                    year_str = ''.join(c for c in year_str if c.isdigit())
                    if year_str and len(year_str) == 4:
                        item_year_int = int(year_str)
                        if item_year_int < year_int:
                            return False
            except (ValueError, TypeError):
                pass
                
        # Apply rating band filter
        if rating_min is not None or rating_max is not None:
            item_rating = item.get('rating')
            if item_rating is None:
                return False  # exclude items without rating
            try:
                rating_val = float(item_rating)
                if rating_min is not None and rating_val < rating_min:
                    return False
                if rating_max is not None and rating_val > rating_max:
                    return False
            except (ValueError, TypeError):
                return False
                
        return True

    filtered = [r for r in results if matches_filters(r)]

    # paginate results server-side
    paginator = Paginator(filtered, 12)
    page_obj = paginator.get_page(page)

    # prepare response list
    items = []
    for it in page_obj:
        # normalize item fields for frontend
        if it.get('media_type') == 'movie' or it.get('type') == 'movie':
            items.append({
                'id': it.get('external_id') or it.get('id'),
                'type': 'movie',
                'title': it.get('title'),
                'year': it.get('year'),
                'poster': it.get('poster_url') or it.get('poster_path') or it.get('thumbnail'),
            })
        else:
            items.append({
                'id': it.get('external_id') or it.get('id'),
                'type': 'book',
                'title': it.get('title'),
                'year': it.get('year'),
                'poster': it.get('cover_url') or it.get('thumbnail'),
            })

    return JsonResponse({
        'results': items,
        'page': page_obj.number,
        'pages': paginator.num_pages,
        'total': paginator.count,
    })
