from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Post, Author
from .forms import PostForm

from django.contrib.auth.models import User
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.shortcuts import redirect

from django.http import HttpResponseRedirect
from .models import Category


# ——— Список всех постов (новости + статьи) ———
@login_required
def news_list(request):
    news_list = Post.objects.order_by('-created_at')
    paginator = Paginator(news_list, 10)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "news_list.html", {"page_obj": page_obj})


# ——— Детали одного поста ———
@login_required
def news_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "news_detail.html", {"post": post})


# ——— Поиск ———
@login_required
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

@login_required
def become_author(request):
    authors_group, _ = Group.objects.get_or_create(name='authors')
    request.user.groups.add(authors_group)
    return redirect('/')


class NewsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = reverse_lazy('news_list')
    login_url = '/accounts/login/'
    permission_required = 'news.add_post'

    def form_valid(self, form):
        user = self.request.user
        author, created = Author.objects.get_or_create(user=user)

        # Проверяем количество постов за сегодня
        today_posts = Post.objects.filter(
            author=author,
            created_at__date=now().date()
        ).count()

        if today_posts >= 3:
            messages.error(self.request, "Вы не можете публиковать более 3 постов в день.")
            return redirect('news_list')  # или другой шаблон

        post = form.save(commit=False)
        post.type = 'NW'
        post.author = author
        return super().form_valid(form)

    
@login_required
def subscribe_to_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.subscribers.add(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class ArticleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = reverse_lazy('news_list')
    login_url = '/accounts/login/'
    permission_required = 'news.add_post'

    def form_valid(self, form):
        user = self.request.user
        author, created = Author.objects.get_or_create(user=user)

        # Лимит на посты
        today_posts = Post.objects.filter(
            author=author,
            created_at__date=now().date()
        ).count()

        if today_posts >= 3:
            messages.error(self.request, "Вы не можете публиковать более 3 постов в день.")
            return redirect('news_list')

        post = form.save(commit=False)
        post.type = 'AR'
        post.author = author
        return super().form_valid(form)



class NewsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = reverse_lazy('news_list')
    login_url = '/accounts/login/' 
    permission_required = 'news.change_post'


class ArticleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = reverse_lazy('news_list')
    login_url = '/accounts/login/'
    permission_required = 'news.change_post'


class NewsDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')
    login_url = '/accounts/login/'


class ArticleDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')
    login_url = '/accounts/login/'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'account/profile_edit.html'
    success_url = '/'

    def get_object(self):
        return self.request.user


