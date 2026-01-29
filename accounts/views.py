from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
import random
from .models import PasswordResetCode
from datetime import timedelta
from django.db import OperationalError as DjangoOperationalError
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import PasswordResetCode
from .models import Profile, Activity, Follow, Notification
from .forms import ProfileForm, DevPasswordChangeForm
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth import get_user_model

@login_required
@require_POST
def follow_user(request):
    import json
    data = json.loads(request.body)
    user_id = data.get('user_id')
    if not user_id or int(user_id) == request.user.id:
        return JsonResponse({'success': False, 'error': 'Invalid user.'})
    User = get_user_model()
    try:
        target = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found.'})
    obj, created = Follow.objects.get_or_create(follower=request.user, following=target)
    
    # Create notification for the followed user
    if created:
        Notification.objects.create(
            user=target,
            actor=request.user,
            notif_type='follow'
        )
    
    return JsonResponse({'success': True, 'following': True})

@login_required
@require_POST
def unfollow_user(request):
    import json
    data = json.loads(request.body)
    user_id = data.get('user_id')
    if not user_id or int(user_id) == request.user.id:
        return JsonResponse({'success': False, 'error': 'Invalid user.'})
    User = get_user_model()
    try:
        target = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found.'})
    Follow.objects.filter(follower=request.user, following=target).delete()
    return JsonResponse({'success': True, 'following': False})
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
import random
from .models import PasswordResetCode
from datetime import timedelta
from django.db import OperationalError as DjangoOperationalError
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import PasswordResetCode
from .models import Profile, Activity, Follow
from .forms import ProfileForm, DevPasswordChangeForm


def login_view(request):
    # if already authenticated, send to home
    if request.user.is_authenticated:
        return redirect('home')                     

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        # Allow users to login using their email address: resolve username first
        try:
            user_obj = User.objects.get(email=email)
            username_to_auth = user_obj.username
        except User.DoesNotExist:
            username_to_auth = None

        user = authenticate(request, username=username_to_auth, password=password)

        if user is not None:
            login(request, user)

            if not remember:
                request.session.set_expiry(0)
            else:
                # Remember for 30 days
                request.session.set_expiry(60 * 60 * 24 * 30)

            # successful login: redirect to named home view
            return redirect('home')
        else:
            messages.error(request, 'Eposta veya Şifre hatalı.')

    return render(request, 'accounts/login.html')


def register_view(request):
    # prevent authenticated users from using the registration page
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        field_errors = {}
        form_values = {'first_name': first_name, 'email': email}

        # basic validations
        if not first_name:
            field_errors['first_name'] = 'İsim boş bırakılamaz.'

        if not email:
            field_errors['email'] = 'E-posta boş bırakılamaz.'

        if not password:
            field_errors['password'] = 'Şifre boş bırakılamaz.'

        if password and password2 and password != password2:
            field_errors['password2'] = 'Şifreler eşleşmiyor.'

        if email and User.objects.filter(email=email).exists():
            field_errors['email'] = 'Bu E-posta kullanımda.'
            duplicate_email = True

        if field_errors:
            # if the only problem is duplicate email, show a focused message
            if 'duplicate_email' in locals() and duplicate_email:
                messages.error(request, 'Bu E-posta kullanımda. Lütfen kontrol ediniz.')
            else:
                messages.error(request, 'Kayıt hatası. Lütfen alanları kontrol edin.')
            return render(request, 'accounts/register.html', {'field_errors': field_errors, 'form_values': form_values})

        # No validation errors — create the user
        base_username = first_name.strip() or email.split('@')[0]
        candidate = base_username
        suffix = 0
        while User.objects.filter(username=candidate).exists():
            suffix += 1
            candidate = f"{base_username}{suffix}"

        user = User.objects.create_user(username=candidate, email=email, password=password)
        user.first_name = first_name
        user.save()

        # create profile if it doesn't already exist (signals may auto-create)
        Profile.objects.get_or_create(user=user, defaults={'display_name': first_name})

        # Show success message on the registration page and stay here until user clicks login
        messages.success(request, 'Kayıt başarılı. Giriş yapmak için lütfen "Giriş Yap" bağlantısını kullanın.')
        # Clear form values for freshness
        form_values = {}
        return render(request, 'accounts/register.html', {'form_values': form_values})

    return render(request, 'accounts/register.html')


def logout_view(request):
    """Log the user out and redirect to login with a message."""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, 'Başarıyla çıkış yapıldı.')
    return redirect('login')


@login_required
def profile_view(request):
    """Redirect to the public profile page for the authenticated user.

    The template `accounts/profile.html` expects `profile_user` and related
    context variables — the public_profile_view builds those. To avoid
    duplicating logic here we redirect the logged-in user to their
    `/user/<username>/` page which will render the profile template with
    the correct context.
    """
    if request.user.is_authenticated:
        return redirect('public_profile', username=request.user.username)
    return redirect('login')


def public_profile_view(request, username):
    # public profile at /user/<username>/
    user = get_object_or_404(User, username=username)
    profile = getattr(user, 'profile', None)

    followers_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    activity_count = Activity.objects.filter(user=user).count()

    activities_qs = Activity.objects.filter(user=user).order_by('-created_at')[:20]
    activities = []
    for a in activities_qs:
        activities.append({
            'id': a.id,
            'activity_type': a.type,  # 'rating' or 'review'
            'media_type': a.content_type,
            'item_id': a.content_id,
            'title': getattr(a, 'title', '') or '',
            'cover_url': getattr(a, 'cover_url', '') or '',
            'year': getattr(a, 'year', '') or '',
            'rating': a.rating,
            'comment_text': a.review or '',
            'created_at': a.created_at,
        })

    is_owner = request.user.is_authenticated and request.user.username == user.username

    return render(request, 'accounts/profile.html', {
        'profile_user': user,
        'profile': profile,
        'followers_count': followers_count,
        'following_count': following_count,
        'activity_count': activity_count,
        'activities': activities,
        'is_owner': is_owner,
    })


@login_required
def library_view(request):
    """Render the user's library page with dummy data for each tab.

    This view prepares placeholder items so the frontend UI is ready.
    """
    user = request.user
    from .models import LibraryItem, CustomList
    try:
        # Query real items from DB and serialize minimal fields for template
        watched_qs = LibraryItem.objects.filter(user=user, media_type='movie', status='watched').order_by('-added_at')
        to_watch_qs = LibraryItem.objects.filter(user=user, media_type='movie', status='to_watch').order_by('-added_at')
        read_qs = LibraryItem.objects.filter(user=user, media_type='book', status='read').order_by('-added_at')
        to_read_qs = LibraryItem.objects.filter(user=user, media_type='book', status='to_read').order_by('-added_at')

        def serialize_li(li):
            return {
                'pk': li.pk,
                'external_id': li.item_id,
                'title': li.title,
                'year': getattr(li, 'year', '') or '',
                'poster_url': li.cover_url if li.media_type == 'movie' else '',
                'cover_url': li.cover_url if li.media_type == 'book' else '',
                'media_type': li.media_type,
                'rating': li.rating,
            }

        watched = [serialize_li(x) for x in watched_qs]
        to_watch = [serialize_li(x) for x in to_watch_qs]
        read = [serialize_li(x) for x in read_qs]
        to_read = [serialize_li(x) for x in to_read_qs]
        custom_lists = list(CustomList.objects.filter(user=user).prefetch_related('items').order_by('-created_at'))
    except DjangoOperationalError:
        # Migrations not applied or DB inaccessible — fall back to empty lists
        watched = []
        to_watch = []
        read = []
        to_read = []
        custom_lists = []

    return render(request, 'library.html', {
        'watched': watched,
        'to_watch': to_watch,
        'read': read,
        'to_read': to_read,
        'custom_lists': custom_lists,
    })


@login_required
def create_custom_list(request):
    from django.http import JsonResponse
    from .models import CustomList

    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required'}, status=405)

    name = request.POST.get('name', '').strip()
    emoji = request.POST.get('emoji', '').strip()
    if not name:
        return JsonResponse({'ok': False, 'error': 'name required'}, status=400)

    cl = CustomList.objects.create(user=request.user, name=name, emoji=emoji)
    return JsonResponse({'ok': True, 'id': cl.id, 'name': cl.name, 'emoji': cl.emoji})


@login_required
def delete_custom_list_item(request):
    from django.http import JsonResponse
    from .models import CustomListItem

    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required'}, status=405)
    item_pk = request.POST.get('item_pk')
    if not item_pk:
        return JsonResponse({'ok': False, 'error': 'item_pk required'}, status=400)
    try:
        cli = CustomListItem.objects.get(pk=item_pk, custom_list__user=request.user)
        cli.delete()
        return JsonResponse({'ok': True})
    except CustomListItem.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'not found'}, status=404)


@login_required
def delete_custom_list(request):
    from django.http import JsonResponse
    from .models import CustomList

    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required'}, status=405)
    list_pk = request.POST.get('list_pk')
    if not list_pk:
        return JsonResponse({'ok': False, 'error': 'list_pk required'}, status=400)
    try:
        cl = CustomList.objects.get(pk=list_pk, user=request.user)
        cl.delete()
        return JsonResponse({'ok': True})
    except CustomList.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'not found'}, status=404)


@login_required
def delete_library_item(request):
    from django.http import JsonResponse
    from .models import LibraryItem

    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required'}, status=405)
    item_pk = request.POST.get('item_pk')
    if not item_pk:
        return JsonResponse({'ok': False, 'error': 'item_pk required'}, status=400)
    try:
        li = LibraryItem.objects.get(pk=item_pk, user=request.user)
        li.delete()
        return JsonResponse({'ok': True})
    except LibraryItem.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'not found'}, status=404)


@login_required
def get_custom_list_items(request):
    from django.http import JsonResponse
    from .models import CustomList, CustomListItem

    list_id = request.GET.get('list_id')
    if not list_id:
        return JsonResponse({'ok': False, 'error': 'list_id required'}, status=400)
    try:
        cl = CustomList.objects.get(pk=list_id, user=request.user)
    except CustomList.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'not found'}, status=404)

    items = []
    for it in cl.items.all():
        items.append({
            'pk': it.pk,
            'item_id': it.item_id,
            'title': it.title,
            'cover_url': it.cover_url,
            'media_type': it.media_type,
        })
    return JsonResponse({'ok': True, 'items': items, 'name': cl.name, 'emoji': cl.emoji})



@login_required
def edit_profile_view(request, username):
    # only owner can edit
    if request.user.username != username:
        return render(request, '403.html', status=403)

    profile = getattr(request.user, 'profile', None)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Show success message on the edit page itself
            messages.success(request, 'Profil başarıyla güncellendi.')
            # re-render the edit page (do not redirect to profile)
            # ensure widget classes for rendered form
            for fname in ('display_name', 'bio', 'avatar'):
                if fname in form.fields:
                    w = form.fields[fname].widget
                    cls = w.attrs.get('class', '')
                    parts = cls.split() if cls else []
                    if 'form-control' not in parts:
                        parts.insert(0, 'form-control')
                    # no errors after successful save
                    parts = [p for p in parts if p != 'is-invalid']
                    w.attrs['class'] = ' '.join(parts)
            return render(request, 'accounts/profile_edit.html', {'form': form, 'profile_user': request.user})
    else:
        form = ProfileForm(instance=profile)

    # ensure widgets have base class and mark invalid fields
    for fname in ('display_name', 'bio', 'avatar'):
        if fname in form.fields:
            w = form.fields[fname].widget
            cls = w.attrs.get('class', '')
            parts = cls.split() if cls else []
            if 'form-control' not in parts:
                parts.insert(0, 'form-control')
            if form.errors.get(fname):
                if 'is-invalid' not in parts:
                    parts.append('is-invalid')
            else:
                parts = [p for p in parts if p != 'is-invalid']
            w.attrs['class'] = ' '.join(parts)

    return render(request, 'accounts/profile_edit.html', {'form': form, 'profile_user': request.user})


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = DevPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            # Show success message on the same page
            messages.success(request, 'Şifreniz başarıyla değiştirildi.')
            # prepare a new, empty form for the page
            form = DevPasswordChangeForm(user=request.user)
            # ensure widget classes exist on the new form
            for _fname in ('old_password', 'new_password1', 'new_password2'):
                if _fname in form.fields:
                    w = form.fields[_fname].widget
                    cls = w.attrs.get('class', '')
                    parts = cls.split() if cls else []
                    if 'form-control' not in parts:
                        parts.insert(0, 'form-control')
                    # no errors on a fresh form; ensure is-invalid removed
                    parts = [p for p in parts if p != 'is-invalid']
                    w.attrs['class'] = ' '.join(parts)
            return render(request, 'accounts/password_change.html', {'form': form})
    else:
        form = DevPasswordChangeForm(user=request.user)

    # Before rendering, ensure all password fields have the base 'form-control' class
    for fname in ('old_password', 'new_password1', 'new_password2'):
        if fname in form.fields:
            w = form.fields[fname].widget
            cls = w.attrs.get('class', '')
            parts = cls.split() if cls else []
            if 'form-control' not in parts:
                parts.insert(0, 'form-control')
            # add is-invalid when that particular field has errors
            if form.errors.get(fname):
                if 'is-invalid' not in parts:
                    parts.append('is-invalid')
            else:
                parts = [p for p in parts if p != 'is-invalid']
            w.attrs['class'] = ' '.join(parts)

    return render(request, 'accounts/password_change.html', {'form': form})


@login_required
def delete_account_view(request):
    if request.method != 'POST':
        return render(request, '403.html', status=403)

    # optional password confirmation
    pw = request.POST.get('password', '').strip()
    # require password for deletion
    if not pw:
        messages.error(request, 'Lütfen şifrenizi girin.', extra_tags='profile delete_error')
        return redirect('public_profile', username=request.user.username)

    if not request.user.check_password(pw):
        messages.error(request, 'Şifre yanlış.', extra_tags='profile delete_error')
        return redirect('public_profile', username=request.user.username)

    # Ensure we operate on the DB user object even after logout.
    user_to_delete = request.user

    # logout first to clear session, then delete the saved user object
    logout(request)

    try:
        # If for some reason the saved user is an AnonymousUser, avoid calling delete on it
        from django.contrib.auth.models import AnonymousUser
        if isinstance(user_to_delete, AnonymousUser):
            messages.error(request, 'Geçersiz işlem.')
            return redirect('login')

        user_to_delete.delete()
        messages.info(request, 'Hesap silindi.')
    except Exception:
        # If deletion fails, log user out (already done) and show a generic message
        messages.error(request, 'Hesap silinirken bir hata oluştu.')

    return redirect('login')


def _generate_code():
    return f"{random.randint(0, 999999):06d}"


def password_reset_request_view(request):
    """Request a password reset code be sent to the user's email."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, 'Lütfen bir e-posta girin.')
            return render(request, 'accounts/password_reset_request.html')

        # First, ensure the email belongs to a registered user
        if not User.objects.filter(email=email).exists():
            messages.error(request, 'Bu e-posta ile kayıtlı bir kullanıcı bulunamadı.')
            return render(request, 'accounts/password_reset_request.html')

        # generate code and save record
        code = _generate_code()
        try:
            pr = PasswordResetCode.objects.create(email=email, code=code)
        except DjangoOperationalError:
            # Likely migrations haven't been applied and the table doesn't exist
            messages.error(request, 'Sunucu yapılandırmasında eksik bir parça var (migrations uygulanmamış). Lütfen geliştiriciye çalıştırılacak `makemigrations`/`migrate` komutlarını çalıştırmasını söyleyin.')
            return render(request, 'accounts/password_reset_request.html')

        # Compose and send the email — uses Django's email settings
        subject = 'Sosyal Kütüphanem - Şifre Sıfırlama Kodu'
        message = f'Şifre sıfırlama kodunuz: {code}\n\nBu kod 15 dakika içinde geçerlidir.'
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')

        try:
            send_mail(subject, message, from_email, [email], fail_silently=False)
            messages.success(request, 'Eğer bu e-posta sistemimizde kayıtlıysa, kod gönderildi. Lütfen gelen kutunuzu kontrol edin.')
        except Exception as e:
            # don't expose mail errors; still tell user a code was sent
            messages.info(request, 'E-posta gönderimi sırasında bir şey oldu; kod oluşturuldu. Lütfen kontrol edin.')

        # Redirect user to verify page with their email prefilled
        return redirect(f"{settings.SITE_ROOT if hasattr(settings,'SITE_ROOT') else ''}/accounts/password-reset/verify/?email={email}")

    return render(request, 'accounts/password_reset_request.html')


def password_reset_verify_view(request):
    """Verify a code sent to an email. If correct, allow the user to continue to set a new password."""
    email = request.GET.get('email', request.POST.get('email', '')).strip()

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        code = request.POST.get('code', '').strip()

        if not email or not code:
            field_errors = {'code': 'E-posta ve kod gereklidir.'}
            return render(request, 'accounts/password_reset_verify.html', {'email': email, 'field_errors': field_errors})

        # find most recent matching code
        pr_qs = PasswordResetCode.objects.filter(email=email, code=code, used=False).order_by('-created_at')
        if not pr_qs.exists():
            field_errors = {'code': 'Geçersiz kod veya e-posta.'}
            return render(request, 'accounts/password_reset_verify.html', {'email': email, 'field_errors': field_errors})

        pr = pr_qs.first()
        if pr.is_expired(15):
            field_errors = {'code': 'Kod süresi dolmuş. Lütfen tekrar istekte bulunun.'}
            return render(request, 'accounts/password_reset_verify.html', {'email': email, 'field_errors': field_errors})

        # mark as used and allow password change step via session
        pr.used = True
        pr.save()
        request.session['password_reset_email'] = email
        request.session['password_reset_allowed'] = True
        return redirect('password_reset_confirm')

    return render(request, 'accounts/password_reset_verify.html', {'email': email})


def password_reset_confirm_view(request):
    """Allow the user to set a new password after verifying code."""
    allowed = request.session.get('password_reset_allowed')
    email = request.session.get('password_reset_email')

    if not allowed or not email:
        messages.error(request, 'Önce doğrulama kodunu girmeniz gerekir.');
        return redirect('password_reset')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not password or not password2:
            messages.error(request, 'Lütfen her iki şifre alanını da doldurun.')
            return render(request, 'accounts/password_reset_confirm.html')

        if password != password2:
            messages.error(request, 'Şifreler eşleşmiyor.')
            return render(request, 'accounts/password_reset_confirm.html')

        # find the user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Bu e-posta ile kayıtlı bir kullanıcı bulunamadı.')
            # clear session flags
            request.session.pop('password_reset_allowed', None)
            request.session.pop('password_reset_email', None)
            return redirect('login')

        user.set_password(password)
        user.save()

        # cleanup session
        request.session.pop('password_reset_allowed', None)
        request.session.pop('password_reset_email', None)

        messages.success(request, 'Şifre başarıyla değiştirildi. Yeni şifrenizle giriş yapabilirsiniz.')
        return redirect('login')

    return render(request, 'accounts/password_reset_confirm.html')
