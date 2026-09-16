from django.conf import settings
from django.http import HttpResponseRedirect

from .i18n import translate_html


class SiteLanguageMiddleware:
    """Keep the existing Turkish UI and translate rendered pages when English is selected."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        selected_language = request.GET.get('lang')
        if selected_language in {'tr', 'en'}:
            request.session['site_language'] = selected_language
            clean_path = request.path
            query = request.GET.copy()
            query.pop('lang', None)
            query_string = query.urlencode()
            target = clean_path + (f'?{query_string}' if query_string else '')
            return HttpResponseRedirect(target)

        response = self.get_response(request)
        if request.session.get('site_language') == 'en' and response.get('Content-Type', '').startswith('text/html'):
            response.content = translate_html(response.content.decode(response.charset or settings.DEFAULT_CHARSET)).encode(response.charset or settings.DEFAULT_CHARSET)
            response.headers['Content-Length'] = str(len(response.content))
        return response