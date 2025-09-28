from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .const import POSTS_PER_PAGE
from .forms import CreateComments, CreatePost, UserForm
from .models import Category, Comments, Post


def pagination(posts, request, posts_per_page=POSTS_PER_PAGE):
    return Paginator(posts, posts_per_page).get_page(
        request.GET.get('page')
    )


def select_posts(posts=Post.objects.all(),
                 filter_posts=True,
                 select_related_fields=True,
                 annotate_comments=True):
    if filter_posts:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )
    if select_related_fields:
        posts = posts.select_related('author', 'location', 'category')
    if annotate_comments:
        posts = posts.annotate(
            comment_count=Count('comments')).order_by(*Post._meta.ordering)
    return posts


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if author.username != request.user.username:
        filter_posts = True
    else:
        filter_posts = False
    posts = select_posts(author.posts, filter_posts=filter_posts)
    context = {
        'profile': author,
        'page_obj': pagination(posts, request),
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request, username):
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
    if post.author.username == request.user.username:
        post = post
    else:
        post = get_object_or_404(
            select_posts(),
            pk=post_pk
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
    if not form.is_valid():
        context = {'form': form}
        return render(request, 'blog/create.html', context)
    instance = form.save(commit=False)
    instance.author = request.user
    instance.save()
    return redirect('blog:profile', request.user.username)


@login_required
def edit_post(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if post.author.username != request.user.username:
        return redirect('blog:post_detail', post.pk)
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
