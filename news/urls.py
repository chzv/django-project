from django.urls import path
from .views import (
    news_list, news_detail, news_search,
    NewsCreateView, ArticleCreateView,
    NewsUpdateView, ArticleUpdateView,
    NewsDeleteView, ArticleDeleteView,
    ProfileUpdateView, become_author
)

urlpatterns = [
    path('', news_list, name='news_list'),
    path('search/', news_search, name='news_search'),
    path('<int:pk>/', news_detail, name='news_detail'),

    path('news/create/', NewsCreateView.as_view(), name='news_create'),
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),

    path('news/<int:pk>/edit/', NewsUpdateView.as_view(), name='news_edit'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit'),

    path('news/<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),
    path('articles/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),

    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('become-author/', become_author, name='become_author'),
]
