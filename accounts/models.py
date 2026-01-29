from django.db import models
from django.utils import timezone


class PasswordResetCode(models.Model):
	email = models.EmailField()
	code = models.CharField(max_length=6)
	created_at = models.DateTimeField(default=timezone.now)
	used = models.BooleanField(default=False)

	def is_expired(self, minutes=15):
		return (timezone.now() - self.created_at).total_seconds() > minutes * 60

	def __str__(self):
		return f"PasswordResetCode({self.email}, {self.code}, used={self.used})"


class Follow(models.Model):
	follower = models.ForeignKey('auth.User', related_name='following_set', on_delete=models.CASCADE)
	following = models.ForeignKey('auth.User', related_name='followers_set', on_delete=models.CASCADE)

	class Meta:
		unique_together = ('follower', 'following')

	def __str__(self):
		return f"{self.follower} -> {self.following}"


class Activity(models.Model):
	CONTENT_CHOICES = (
		('movie', 'Movie'),
		('book', 'Book'),
	)
	TYPE_CHOICES = (
		('rating', 'Rating'),
		('review', 'Review'),
		('like', 'Like'),
		('comment', 'Comment'),
	)

	user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='activities')
	content_type = models.CharField(max_length=10, choices=CONTENT_CHOICES)
	content_id = models.CharField(max_length=64)
	type = models.CharField(max_length=10, choices=TYPE_CHOICES)
	rating = models.IntegerField(null=True, blank=True)
	review = models.TextField(null=True, blank=True)
	# additional display metadata to surface in profile activity feed
	title = models.CharField(max_length=400, blank=True)
	cover_url = models.CharField(max_length=1000, blank=True)
	year = models.CharField(max_length=10, blank=True)
	overview = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Activity({self.user}, {self.type}, {self.content_type}:{self.content_id})"

	def excerpt(self, length=180):
		if not self.review:
			return ''
		return (self.review[:length].rsplit(' ', 1)[0] + '...') if len(self.review) > length else self.review

# Create your models here.


class Profile(models.Model):
	user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
	avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
	display_name = models.CharField(max_length=100, blank=True)
	bio = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f'Profile({self.user.username})'


# Library models: prepared for later integration with the Explore page
class LibraryItem(models.Model):
	MEDIA_TYPES = (
		('movie', 'Movie'),
		('book', 'Book'),
	)
	STATUS_CHOICES = (
		('watched', 'Watched'),
		('to_watch', 'To Watch'),
		('read', 'Read'),
		('to_read', 'To Read'),
	)

	user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='library_items')
	media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
	status = models.CharField(max_length=12, choices=STATUS_CHOICES)
	item_id = models.CharField(max_length=128)
	title = models.CharField(max_length=400)
	cover_url = models.CharField(max_length=1000, blank=True)
	rating = models.PositiveSmallIntegerField(null=True, blank=True)
	added_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-added_at']

	def __str__(self):
		return f"LibraryItem({self.user.username}, {self.media_type}:{self.item_id})"


class CustomList(models.Model):
	user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='custom_lists')
	name = models.CharField(max_length=200)
	emoji = models.CharField(max_length=4, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"CustomList({self.user.username}, {self.name})"


class CustomListItem(models.Model):
	custom_list = models.ForeignKey(CustomList, on_delete=models.CASCADE, related_name='items')
	item_id = models.CharField(max_length=128)
	title = models.CharField(max_length=400)
	cover_url = models.CharField(max_length=1000, blank=True)
	media_type = models.CharField(max_length=10, choices=LibraryItem.MEDIA_TYPES)
	added_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-added_at']

	def __str__(self):
		return f"CustomListItem({self.custom_list.name}, {self.media_type}:{self.item_id})"


class ItemComment(models.Model):
	"""User comments attached to an item shown in Explore.

	Uses the same identification as LibraryItem / CustomListItem: media_type and item_id
	"""
	user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='item_comments')
	media_type = models.CharField(max_length=10)  # 'movie' or 'book'
	item_id = models.CharField(max_length=100)
	comment = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"ItemComment({self.user.username}, {self.media_type}:{self.item_id})"


class Like(models.Model):
	"""Likes on activity cards in the home feed."""
	user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='likes')
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='likes')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('user', 'activity')

	def __str__(self):
		return f"Like({self.user.username}, Activity#{self.activity.id})"


class ActivityComment(models.Model):
	"""Comments on activity cards in the home feed."""
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='comments')
	user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='activity_comments')
	comment = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['created_at']

	def __str__(self):
		return f"ActivityComment({self.user.username}, Activity#{self.activity.id})"


class Notification(models.Model):
	"""User notifications for follow, like, and comment actions."""
	NOTIF_TYPES = (
		('follow', 'Follow'),
		('like', 'Like'),
		('comment', 'Comment'),
	)

	user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='notifications')
	actor = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='actions')
	notif_type = models.CharField(max_length=20, choices=NOTIF_TYPES)
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True, blank=True)
	comment_text = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	is_seen = models.BooleanField(default=False)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Notification({self.user.username}, {self.notif_type}, from {self.actor.username})"

# Ensure a Profile is created for each new User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
	else:
		# ensure profile exists
		if not hasattr(instance, 'profile'):
			Profile.objects.create(user=instance)
