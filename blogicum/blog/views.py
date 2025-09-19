from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.http import Http404

from .models import Post, Category, Comments

from .forms import UserForm, CreatePost, CreateComments


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    template = 'blog/profile.html'
    post_list = Post.objects.select_related().filter(
        author=user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(user.get_full_name)
    context = {'profile': user, 'page_obj': page_obj}
    return render(request, template, context)


@login_required
def edit_profile(request):
    user = get_object_or_404(User, username=request.user.username)
    form = UserForm(request.POST or None, instance=user)
    template = 'blog/user.html'
    context = {'profile': user, 'form': form}
    if form.is_valid():
        form.save()
    return render(request, template, context)


def index(request):
    template = 'blog/index.html'
    post_list = (
        Post.objects.select_related().
        filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True))
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def post_detail(request, pk):
    template = 'blog/detail.html'
    context = {
        'post': get_object_or_404(
            Post,
            pk=pk,
            is_published__exact=True,
            category__is_published__exact=True,
            pub_date__lte=timezone.now(),
        ),
        'form': CreateComments(),
        'comments':
        Comments.objects.select_related('author')
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = (
        get_object_or_404(
            Category,
            slug=category_slug,
            is_published__exact=True))
    paginator = Paginator(category.posts.filter(
        is_published__exact=True,
        pub_date__lte=timezone.now(),), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, template, context)


@login_required
def create_post(request):
    form = CreatePost(request.POST or None, request.FILES or None)
    user = get_object_or_404(User, username=request.user.username)
    template = 'blog/create.html'
    context = {'form': form}
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect('blog:profile', user)
    return render(request, template, context)



def edit_post(request, pk):
    instance = get_object_or_404(Post, pk=pk)

    if not request.user.is_authenticated:
        return redirect('blog:post_detail', pk=instance.pk)

    if instance.author != request.user:
        return redirect('blog:post_detail', pk=instance.pk)

    form = CreatePost(
        request.POST or None,
        request.FILES or None,
        instance=instance
    )
    template = 'blog/create.html'
    context = {'form': form, 'post': instance}

    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect('blog:post_detail', pk=instance.pk)

    return render(request, template, context)


@login_required
def delete_post(request, pk):
    instance = get_object_or_404(Post, pk=pk, author=request.user)
    instance.delete()
    return redirect('blog:index')


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CreateComments(request.POST)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.post = post
        post.comment_count = Comments.objects.select_related().count() + 1
        post.save()
        instance.save()
    return redirect('blog:post_detail', pk)


@login_required
def edit_comment(request, pk, comment_pk):
    instance = get_object_or_404(Comments, pk=comment_pk, author=request.user)
    form = CreateComments(request.POST or None, instance=instance)
    template = 'blog/comment.html'
    context = {'form': form, 'comment': instance}
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect('blog:post_detail', pk)
    return render(request, template, context)


@login_required
def delete_comment(request, pk, comment_pk):
    instance = get_object_or_404(Comments, pk=comment_pk, author=request.user)
    post = get_object_or_404(Post, pk=pk)
    post.comment_count = Comments.objects.select_related().count() - 1
    post.save()
    instance.delete()
    return redirect('blog:post_detail', pk)


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
