from django.contrib.auth.views import LogoutView
from django.http import Http404


def logout_view(request):
    if request.method == 'POST':
        raise Http404()
    return LogoutView.as_view()(request)
