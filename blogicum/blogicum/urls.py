from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView


urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('admin/', admin.site.urls),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('login'),
        ),
        name='registration',
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'blog.views.page_not_found'
handler500 = 'blog.views.internal_error'
