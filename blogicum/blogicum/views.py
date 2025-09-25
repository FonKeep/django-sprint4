from django.shortcuts import render
from django.contrib.auth.views import LogoutView
from django.http import Http404


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)

def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def internal_error(request):
    return render(request, 'pages/500.html', status=500)


def logout_view(request):
    if request.method == 'POST':
        raise Http404()
    return LogoutView.as_view()(request)
