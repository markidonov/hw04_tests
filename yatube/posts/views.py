from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect

from .forms import PostForm

from .models import Post, Group, User

LIMIT_POSTS: int = 10


def post_paginator(request, post_list):
    paginator = Paginator(post_list, LIMIT_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    post_list = Post.objects.all()
    page_obj = post_paginator(request, post_list)
    text = 'Главная страница'
    title = 'Последние обновления на сайте'
    context = {
        'text': text,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    title = group.title
    page_obj = post_paginator(request, post_list)
    context = {
        'group': group,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = User.objects.get(username=username)
    post_list = author.posts.all()
    page_obj = post_paginator(request, post_list)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    author = User.objects.get(posts=post)
    post_list = author.posts.all()
    posts_count = post_list.count()
    context = {
        'post': post,
        'author': author,
        'posts_count': posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)
    form = PostForm(request.POST or None)
    return render(request, 'posts/post_create.html',
                  {'form': form, })


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    template = 'posts/post_create.html'
    group = Group.objects.all()
    is_edit = True
    form = PostForm(request.POST or None, instance=post)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id)
    return render(request, template, {"form": form,
                  'post': post, 'group': group, 'is_edit': is_edit, })
