from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.http import Http404
from django.db.models import Count

from .models import Post, Category, Comments
from .forms import UserForm, CreatePost, CreateComments
from .const import POSTS_PER_PAGE


def profile(request, username):
    author = get_object_or_404(User, username=username)
    template = 'blog/profile.html'
    if username == request.user.username:
        posts = select_posts(
            author.posts, self=True).annotate(
            comment_count=Count('comments')).order_by('-pub_date')
    else:
        posts = select_posts(
            author.posts).annotate(
            comment_count=Count('comments')).order_by('-pub_date')
    context = {
        'profile': author,
        'page_obj': pagination(posts, request),
    }
    return render(request, template, context)


@login_required
def edit_profile(request):
    form = UserForm(request.POST or None, instance=request.user)
    template = 'blog/user.html'
    context = {'profile': request.user.username, 'form': form}
    if form.is_valid():
        form.save()
    return render(request, template, context)


def index(request):
    template = 'blog/index.html'
    posts = select_posts(
        Post.objects.all()).annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    context = {'page_obj': pagination(posts, request), }
    return render(request, template, context)


def post_detail(request, pk):
    template = 'blog/detail.html'
    post = get_object_or_404(Post, pk=pk)
    if request.user == post.author:
        context = {
            'post': post,
            'form': CreateComments(),
            'comments': post.comments.all(),
        }
    else:
        context = {
            'post': get_object_or_404(
                select_posts(Post.objects.all()), pk=pk),
            'form': CreateComments(),
            'comments': get_object_or_404(
                select_posts(Post.objects.all()), pk=pk).comments.all(),
        }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = (
        get_object_or_404(
            Category,
            slug=category_slug,
            is_published__exact=True))
    context = {
        'category': category,
        'page_obj': pagination(category.posts.filter(
            is_published__exact=True,
            pub_date__lte=timezone.now()), request)}
    return render(request, template, context)


@login_required
def create_post(request):
    form = CreatePost(request.POST or None, request.FILES or None)
    template = 'blog/create.html'
    context = {'form': form}
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect('blog:profile', request.user.username)
    return render(request, template, context)


def edit_post(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if not request.user.is_authenticated:
        return redirect('blog:post_detail', post.pk)
    if post.author != request.user:
        return redirect('blog:post_detail', post.pk)
    form = CreatePost(
        request.POST or None,
        request.FILES or None,
        instance=post
    )
    template = 'blog/create.html'
    context = {'form': form, 'post': post}
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        return redirect('blog:post_detail', instance.pk)
    return render(request, template, context)


@login_required
def delete_post(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk, author=request.user)
    if request.method == "POST":
        post.delete()
        return redirect("blog:index")
    return render(
        request,
        "blog/post_confirm_delete.html",
        {"post": post})


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
    comment = get_object_or_404(Comments, pk=comment_pk, author=request.user)
    form = CreateComments(request.POST or None, instance=comment)
    template = 'blog/comment.html'
    context = {'form': form, 'comment': comment}
    if form.is_valid():
        comment = form.save(commit=False)
        comment.save()
        return redirect('blog:post_detail', post_pk)
    return render(request, template, context)


@login_required
def delete_comment(request, post_pk, comment_pk):
    comment = get_object_or_404(Comments, pk=comment_pk, author=request.user)
    post = get_object_or_404(Post, pk=post_pk)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', pk=post_pk)
    return render(request, 'blog/comment_confirm_delete.html', {
        'comment': comment,
        'post': post,
    })


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


def pagination(posts, request):
    return Paginator(posts, POSTS_PER_PAGE).get_page(request.GET.get('page'))


def select_posts(posts, self=False):
    if self:
        selected_posts = posts.select_related('location', 'category')
    else:
        selected_posts = posts.select_related('location', 'category').filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True)
    return selected_posts
