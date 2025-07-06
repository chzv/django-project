from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from datetime import datetime

from .models import Post, Author
from .forms import PostForm

# ——— Список всех постов (новости + статьи) ———
def news_list(request):
    news_list = Post.objects.order_by('-created_at')
    paginator = Paginator(news_list, 10)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "news_list.html", {"page_obj": page_obj})


# ——— Детали одного поста ———
def news_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "news_detail.html", {"post": post})


# ——— Поиск ———
def news_search(request):
    title_query = request.GET.get('title', '')
    author_query = request.GET.get('author', '')
    date_query = request.GET.get('date', '')

    news_list = Post.objects.all()

    if title_query:
        news_list = news_list.filter(title__icontains=title_query)

    if author_query:
        news_list = news_list.filter(author__user__username__icontains=author_query)

    if date_query:
        try:
            date_obj = datetime.strptime(date_query, '%Y-%m-%d')
            news_list = news_list.filter(created_at__gte=date_obj)
        except ValueError:
            pass

    paginator = Paginator(news_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title_query': title_query,
        'author_query': author_query,
        'date_query': date_query,
    }
    return render(request, 'news_search.html', context)


class NewsCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'NW'

        user = self.request.user
        # создаём автора, если его ещё нет
        author, created = Author.objects.get_or_create(user=user)
        post.author = author

        return super().form_valid(form)


class ArticleCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'AR'

        user = self.request.user
        author, created = Author.objects.get_or_create(user=user)
        post.author = author

        return super().form_valid(form)


class NewsUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = reverse_lazy('news_list')


class ArticleUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = reverse_lazy('news_list')


class NewsDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')


class ArticleDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')