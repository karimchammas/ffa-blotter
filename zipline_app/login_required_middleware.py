from django.http import HttpResponseRedirect
from django.conf import settings
from re import compile

EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]

# Downloaded from
# http://stackoverflow.com/a/8378127/4126114
# http://onecreativeblog.com/post/59051248/django-login-required-middleware#code
# https://gist.github.com/ryanwitt/130583#file-login_required_middleware-py
#
# and
# https://docs.djangoproject.com/en/dev/topics/http/middleware/
class LoginRequiredMiddleware:
    def __init__(self, get_response):
      self.get_response = get_response

    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    """
    def __call__(self, request):
      assert hasattr(request, 'user'), "The Login Required middleware\
requires authentication middleware to be installed. Edit your\
MIDDLEWARE_CLASSES setting to insert\
'django.contrib.auth.middleware.AuthenticationMiddleware'. If that doesn't\
work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
'django.core.context_processors.auth'."
      if not request.user.is_authenticated():
        path = request.path_info.lstrip('/')
        if not any(m.match(path) for m in EXEMPT_URLS):
          request.session['next'] = request.path_info
          return HttpResponseRedirect(settings.LOGIN_URL)

      response = self.get_response(request)
      return response
