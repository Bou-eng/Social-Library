import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import (
    Activity,
    ActivityComment,
    CustomList,
    Follow,
    LibraryItem,
    Like,
    Notification,
)


class RouteSmokeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='smoke',
            email='smoke@example.com',
            password='password123',
        )

    def test_public_login_page_and_protected_redirects(self):
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)
        self.assertEqual(self.client.get(reverse('home')).status_code, 302)
        self.assertEqual(self.client.get(reverse('library')).status_code, 302)
        self.assertEqual(self.client.get(reverse('explore:explore')).status_code, 302)

    def test_authenticated_pages_render(self):
        self.client.force_login(self.user)

        self.assertEqual(self.client.get(reverse('home')).status_code, 200)
        self.assertEqual(self.client.get(reverse('library')).status_code, 200)

        with patch('explore.views.get_top_rated_movies', return_value=[]), \
             patch('explore.views.get_popular_movies', return_value=[]), \
             patch('explore.views.get_popular_books', return_value=[]):
            response = self.client.get(reverse('explore:explore'))

        self.assertEqual(response.status_code, 200)


class MainFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='noname1',
            email='noname1@example.com',
            password='password123',
            first_name='No Name 1',
        )
        self.followed = User.objects.create_user(
            username='noname2',
            email='noname2@example.com',
            password='password123',
            first_name='No Name 2',
        )
        self.suggested = User.objects.create_user(
            username='noname3',
            email='noname3@example.com',
            password='password123',
            first_name='No Name 3',
        )
        self.user.profile.display_name = 'No Name 1'
        self.user.profile.save()
        self.followed.profile.display_name = 'No Name 2'
        self.followed.profile.save()
        self.suggested.profile.display_name = 'No Name 3'
        self.suggested.profile.save()
        Follow.objects.create(follower=self.user, following=self.followed)
        self.followed_activity = Activity.objects.create(
            user=self.followed,
            content_type='movie',
            content_id='603',
            type='rating',
            rating=9,
            title='The Matrix',
            cover_url='https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg',
            year='1999',
            overview='A clean sci-fi classic.',
        )
        Activity.objects.create(
            user=self.suggested,
            content_type='movie',
            content_id='157336',
            type='rating',
            rating=10,
            title='Interstellar',
            cover_url='https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
            year='2014',
            overview='Space and time.',
        )
        self.client.force_login(self.user)

    def post_json(self, name, payload):
        return self.client.post(
            reverse(name),
            data=json.dumps(payload),
            content_type='application/json',
        )

    def test_home_feed_uses_followed_users_and_recommends_unfollowed_active_user(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Name 1')
        self.assertEqual([a['title'] for a in response.context['activities']], ['The Matrix'])
        self.assertEqual(response.context['suggested_user']['id'], self.suggested.id)
        self.assertFalse(response.context['suggested_user']['is_following'])

    def test_follow_and_unfollow_endpoints(self):
        follow_response = self.post_json('follow_user', {'user_id': self.suggested.id})

        self.assertEqual(follow_response.status_code, 200)
        self.assertTrue(follow_response.json()['following'])
        self.assertTrue(Follow.objects.filter(follower=self.user, following=self.suggested).exists())
        self.assertTrue(Notification.objects.filter(user=self.suggested, actor=self.user, notif_type='follow').exists())

        unfollow_response = self.post_json('unfollow_user', {'user_id': self.suggested.id})

        self.assertEqual(unfollow_response.status_code, 200)
        self.assertFalse(unfollow_response.json()['following'])
        self.assertFalse(Follow.objects.filter(follower=self.user, following=self.suggested).exists())

    def test_follow_endpoint_rejects_invalid_and_self_follow_requests(self):
        invalid_response = self.client.post(
            reverse('follow_user'),
            data='not json',
            content_type='application/json',
        )
        self_follow_response = self.post_json('follow_user', {'user_id': self.user.id})

        self.assertFalse(invalid_response.json()['success'])
        self.assertFalse(self_follow_response.json()['success'])

    def test_feed_json_endpoints_handle_bad_payloads_cleanly(self):
        bad_like_response = self.client.post(
            reverse('toggle_like'),
            data='not json',
            content_type='application/json',
        )
        bad_comment_response = self.client.post(
            reverse('add_activity_comment'),
            data='not json',
            content_type='application/json',
        )
        bad_delete_response = self.client.post(
            reverse('delete_activity_comment'),
            data='not json',
            content_type='application/json',
        )
        load_more_response = self.client.get(reverse('home_load_more'), {'page': 'bad'})

        self.assertEqual(bad_like_response.status_code, 200)
        self.assertEqual(bad_comment_response.status_code, 200)
        self.assertEqual(bad_delete_response.status_code, 200)
        self.assertEqual(load_more_response.status_code, 200)
        self.assertFalse(bad_like_response.json()['success'])
        self.assertFalse(bad_comment_response.json()['success'])
        self.assertFalse(bad_delete_response.json()['success'])

    def test_activity_like_and_comment_flows(self):
        like_response = self.post_json('toggle_like', {'activity_id': self.followed_activity.id})
        comment_response = self.post_json(
            'add_activity_comment',
            {'activity_id': self.followed_activity.id, 'comment': 'Nice pick'},
        )

        self.assertTrue(like_response.json()['liked'])
        self.assertTrue(Like.objects.filter(user=self.user, activity=self.followed_activity).exists())
        self.assertTrue(comment_response.json()['success'])
        self.assertTrue(ActivityComment.objects.filter(user=self.user, activity=self.followed_activity).exists())
        self.assertEqual(
            Notification.objects.filter(user=self.followed, actor=self.user, activity=self.followed_activity).count(),
            2,
        )

    def test_library_custom_list_endpoints(self):
        create_response = self.client.post(
            reverse('create_custom_list'),
            {'name': 'Favorites', 'emoji': '*'},
        )
        list_id = create_response.json()['id']
        list_response = self.client.get(reverse('get_custom_list_items'), {'list_id': list_id})
        delete_response = self.client.post(reverse('delete_custom_list'), {'list_pk': list_id})

        self.assertTrue(create_response.json()['ok'])
        self.assertTrue(list_response.json()['ok'])
        self.assertTrue(delete_response.json()['ok'])
        self.assertFalse(CustomList.objects.filter(id=list_id).exists())

    def test_explore_filters_movie_results_and_disables_book_rating_filter(self):
        movie_old = {
            'media_type': 'movie',
            'external_id': 'old',
            'title': 'Old Movie',
            'year': '1995',
            'poster_url': '',
            'rating': 8.0,
        }
        movie_low = {
            'media_type': 'movie',
            'external_id': 'low',
            'title': 'Low Movie',
            'year': '2020',
            'poster_url': '',
            'rating': 5.0,
        }
        movie_match = {
            'media_type': 'movie',
            'external_id': 'match',
            'title': 'Match Movie',
            'year': '2020',
            'poster_url': '',
            'rating': 8.5,
        }
        book = {
            'media_type': 'book',
            'external_id': '/works/book',
            'title': 'Book',
            'year': '2010',
            'cover_url': '',
        }

        with patch('explore.views.get_top_rated_movies', return_value=[movie_old, movie_low, movie_match]), \
             patch('explore.views.get_popular_movies', return_value=[movie_old, movie_low, movie_match]), \
             patch('explore.views.get_popular_books', return_value=[book]):
            movie_response = self.client.get(
                reverse('explore:explore'),
                {'type': 'movie', 'year_from': '2000', 'rating_band': '7+'},
            )
            book_response = self.client.get(reverse('explore:explore'), {'type': 'book'})

        self.assertEqual([m['title'] for m in movie_response.context['popular_movies']], ['Match Movie'])
        self.assertEqual(movie_response.context['popular_books'], [])
        self.assertTrue(book_response.context['rating_disabled'])
        self.assertEqual([b['title'] for b in book_response.context['popular_books']], ['Book'])

    def test_save_item_preferences_and_comment_create_expected_records(self):
        save_response = self.client.post(reverse('explore:save_item_preferences'), {
            'media_type': 'movie',
            'item_id': '603',
            'status': 'watched',
            'rating': '9',
            'title': 'The Matrix',
            'cover_url': 'https://example.com/matrix.jpg',
            'year': '1999',
        })
        comment_response = self.client.post(
            reverse('explore:save_comment'),
            data=json.dumps({
                'media_type': 'movie',
                'item_id': '603',
                'comment': 'Still works.',
                'title': 'The Matrix',
                'cover_url': 'https://example.com/matrix.jpg',
                'year': '1999',
            }),
            content_type='application/json',
        )
        json_save_response = self.client.post(
            reverse('explore:save_item_preferences'),
            data=json.dumps({
                'media_type': 'movie',
                'item_id': '604',
                'status': 'to_watch',
                'rating': '8',
                'title': 'The Matrix Reloaded',
                'cover_url': 'https://example.com/matrix-reloaded.jpg',
                'year': '2003',
            }),
            content_type='application/json',
        )

        self.assertTrue(save_response.json()['ok'])
        self.assertTrue(comment_response.json()['success'])
        self.assertTrue(json_save_response.json()['ok'])
        self.assertTrue(LibraryItem.objects.filter(user=self.user, item_id='603', status='watched').exists())
        self.assertTrue(LibraryItem.objects.filter(user=self.user, item_id='604', status='to_watch').exists())
        self.assertTrue(Activity.objects.filter(user=self.user, content_id='603', type='rating').exists())
        self.assertTrue(Activity.objects.filter(user=self.user, content_id='603', type='review').exists())
