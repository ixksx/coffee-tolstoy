"""
Middleware для принудительной смены пароля.
Если пользователь авторизован и у него must_change_password=True,
он перенаправляется на страницу смены пароля.
Неавторизованные пользователи перенаправляются на страницу входа.
"""

from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    """
    Middleware, который:
    1. Неавторизованных — пускает только на login.
    2. Авторизованных с must_change_password — пускает только на force-change.
    """

    PUBLIC_URLS = [
        '/accounts/login/',
        '/accounts/logout/',
        '/django-admin/',
    ]

    PASSWORD_CHANGE_URLS = [
        '/accounts/force-change-password/',
        '/accounts/logout/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)

        if path.startswith('/api/'):
            return self.get_response(request)

        is_public = any(path.startswith(url) for url in self.PUBLIC_URLS)

        if not request.user.is_authenticated:
            if not is_public:
                return redirect('accounts:login')
        else:
            if (hasattr(request.user, 'must_change_password')
                    and request.user.must_change_password
                    and not request.user.is_admin):
                is_allowed = any(
                    path.startswith(url) for url in self.PASSWORD_CHANGE_URLS
                )
                if not is_allowed:
                    return redirect('accounts:force_change_password')

        return self.get_response(request)
    
class NoCacheMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response