from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:pk>/',
         views.post_detail,
         name='post_detail'),
    path('posts/create_post/',
         views.create_post,
         name='create_post'),
    path('posts/edit_post/<int:pk>/',
         views.edit_post,
         name='edit_post'),
    path('posts/delete_post/<int:pk>/',
         views.delete_post,
         name='delete_post'),
    path('posts/add_comment/<int:pk>/',
         views.add_comment,
         name='add_comment'),
    path('posts/edit_comment/<int:pk>/<int:comment_pk>/',
         views.edit_comment,
         name='edit_comment'),
    path('posts/delete_comment/<int:pk>/<int:comment_pk>/',
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
