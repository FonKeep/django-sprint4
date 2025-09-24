from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:pk>/',
         views.post_detail,
         name='post_detail'),
    path('posts/create/',
         views.create_post,
         name='create_post'),
    path('posts/<int:post_pk>/edit/',
         views.edit_post,
         name='edit_post'),
    path('posts/<int:post_pk>/delete/',
         views.delete_post,
         name='delete_post'),
    path('posts/<int:post_pk>/add_comment/',
         views.add_comment,
         name='add_comment'),
    path('posts/<int:post_pk>/<int:comment_pk>/edit_comment/',
         views.edit_comment,
         name='edit_comment'),
    path('posts/<int:post_pk>/<int:comment_pk>/delete_comment/',
         views.delete_comment,
         name='delete_comment'),
    path('category/<slug:category_slug>/',
         views.category_posts,
         name='category_posts'),
    path('profile/edit_profile/',
         views.edit_profile,
         name='edit_profile'),
    path('profile/<str:username>/',
         views.profile,
         name='profile'),
]
