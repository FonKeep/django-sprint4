from django.contrib import admin

from .models import Category, Location, Post, Comments


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'description',
        'slug',
        'created_at',
        'is_published',
    ]
    search_fields = [
        'title',
        'description',
        'slug',
        'created_at',
        'is_published',
    ]
    list_filter = ['created_at', 'is_published']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_published', 'created_at']
    search_fields = ['name', 'is_published', 'created_at']
    list_filter = ['name', 'is_published', 'created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
    ]
    search_fields = [
        'title',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
    ]
    list_filter = ['author', 'location', 'category', 'is_published']


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = [
        'text',
        'post',
        'author',
        'created_at',
    ]
    search_fields = [
        'text',
        'post',
        'author',
        'created_at',
    ]
    list_filter = ['author', 'created_at', ]