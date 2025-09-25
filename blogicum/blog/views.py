from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .const import POSTS_PER_PAGE
from .forms import CreateComments, CreatePost, UserForm
from .models import Category, Comments, Post


def pagination(posts, request):
    return Paginator(posts, POSTS_PER_PAGE).get_page(
        request.GET.get('page')
    )


def select_post(posts, request_username=None, username=None):
    if request_username and username and username == request_username:
        return posts
    return get_object_or_404(
        Post,
        pk=posts.pk,
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )


def select_posts(posts=Post.objects.all(),
                 request_username=None,
                 username=None):
    if request_username and username and username == request_username:
        return posts.select_related('location', 'category').annotate(
            comment_count=Count('comments')
        ).order_by(Post._meta.ordering[0])
    return posts.select_related('location', 'category').filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    ).annotate(
        comment_count=Count('comments')
    ).order_by(Post._meta.ordering[0])


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = select_posts(
        author.posts,
        request.user.username,
        author.username
    )
    context = {
        'profile': author,
        'page_obj': pagination(posts, request),
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    form = UserForm(request.POST or None, instance=request.user)
    context = {
        'profile': request.user.username,
        'form': form,
    }
    if form.is_valid():
        form.save()
    return render(request, 'blog/user.html', context)


def index(request):
    posts = select_posts()
    context = {'page_obj': pagination(posts, request)}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    post = select_post(
        post,
        request.user.username,
        post.author.username
    )
    context = {
        'post': post,
        'form': CreateComments(),
        'comments': post.comments.all(),
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    context = {
        'category': category,
        'page_obj': pagination(select_posts(category.posts), request),
    }
    return render(request, 'blog/category.html', context)


@login_required
def create_post(request):
    form = CreatePost(request.POST or None, request.FILES or None)
    context = {'form': form}
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect('blog:profile', request.user.username)
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if post.author.username != request.user.username:
        return redirect('login', post.pk)
    form = CreatePost(
        request.POST or None,
        request.FILES or None,
        instance=post,
    )
    context = {'form': form, 'post': post}
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post.pk)
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if request.user != post.author:
        return redirect('blog:post_detail', post_pk)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    return render(
        request,
        'blog/post_confirm_delete.html',
        {'post': post},
    )


@login_required
def add_comment(request, post_pk):
    form = CreateComments(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=post_pk)
        comment.save()
    return redirect('blog:post_detail', post_pk)


@login_required
def edit_comment(request, post_pk, comment_pk):
    comment = get_object_or_404(Comments, pk=comment_pk)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_pk)
    form = CreateComments(request.POST or None, instance=comment)
    context = {'form': form, 'comment': comment}
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_pk)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_pk, comment_pk):
    comment = get_object_or_404(Comments, pk=comment_pk)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_pk)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_pk)
    return render(
        request,
        'blog/comment_confirm_delete.html',
        {
            'comment': comment,
            'post': comment.post,
        },
    )
