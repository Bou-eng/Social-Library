from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from .models import Profile


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure required-message is Turkish and widgets have form-control class
        for fname, field in self.fields.items():
            # set concise Turkish required message
            field.error_messages['required'] = 'Bu alan zorunludur.'
            # ensure class exists on widget
            css = field.widget.attrs.get('class', '')
            if 'form-control' not in css:
                field.widget.attrs['class'] = (css + ' form-control').strip()
    class Meta:
        model = Profile
        fields = ['display_name', 'bio', 'avatar']
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'İsim veya kullanıcı adı'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Kısa biyografiniz...'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if not avatar:
            return avatar
        # limit size to ~2MB
        max_size = getattr(settings, 'PROFILE_AVATAR_MAX_SIZE', 2 * 1024 * 1024)
        if avatar.size > max_size:
            raise ValidationError('Avatar dosyası çok büyük (maksimum 2 MB).')
        return avatar


class DevPasswordChangeForm(PasswordChangeForm):
    # can customize labels/placeholders if needed
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to password inputs to match login/register styles
        for fname in ['old_password', 'new_password1', 'new_password2']:
            if fname in self.fields:
                # apply base classes and placeholders
                attrs = {'class': 'form-control', 'placeholder': self.fields[fname].label}
                # set minlength on new password fields for client-side enforcement
                if fname in ('new_password1', 'new_password2'):
                    attrs['minlength'] = '6'
                self.fields[fname].widget.attrs.update(attrs)
                # set Turkish required message for field
                self.fields[fname].error_messages['required'] = 'Bu alan zorunludur.'

    def clean_old_password(self):
        old = self.cleaned_data.get('old_password')
        # Use concise Turkish message for wrong current password
        if not self.user.check_password(old):
            raise ValidationError('Eski şifre yanlış.', code='invalid')
        return old

    def clean_new_password2(self):
        # Validate password confirmation and length (server-side minimum 6)
        pw1 = self.cleaned_data.get('new_password1')
        pw2 = self.cleaned_data.get('new_password2')
        if pw1 and pw2:
            if pw1 != pw2:
                raise ValidationError('Şifreler eşleşmiyor.', code='password_mismatch')
            if len(pw1) < 6:
                raise ValidationError('En az 6 karakter.', code='password_too_short')
        return pw2

    def clean(self):
        # Let the parent run its validations (this may add validator messages).
        cleaned = super().clean()

        # Replace common English validator messages with short Turkish equivalents.
        # This covers messages emitted by Django's password validators or default messages
        # so the UI consistently shows concise Turkish text.
        def translate_errors(err_list):
            new = []
            for msg in err_list:
                text = str(msg)
                # common patterns -> short Turkish messages
                if 'too short' in text or 'at least' in text or 'En az' in text:
                    new.append('En az 6 karakter.')
                elif 'didn' in text and 'match' in text:
                    new.append('Şifreler eşleşmiyor.')
                elif 'entirely numeric' in text or 'numeric' in text:
                    new.append('En az 6 karakter.')
                elif 'too common' in text or 'common' in text:
                    new.append('Daha güçlü bir şifre girin.')
                elif 'similar' in text or 'similarity' in text or 'too similar' in text:
                    new.append('Daha farklı bir şifre girin.')
                else:
                    # default fallback: use original text (but typically English)
                    new.append(text)
            return new

        # Translate field errors
        for field in list(self.errors.keys()):
            errs = self.errors.get(field)
            if not errs:
                continue
            new = translate_errors(errs)
            # replace with ErrorList so Django templates render correctly
            self._errors[field] = ErrorList(new)

        return cleaned
