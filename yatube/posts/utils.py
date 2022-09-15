from django.core.paginator import Paginator

LIMIT_POSTS: int = 10


def post_paginator(request, post_list):
    paginator = Paginator(post_list, LIMIT_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
