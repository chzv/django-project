# news/tasks.py

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from .models import Post, Category

@shared_task
def notify_subscribers(post_id):
    from .models import Post  # импорт внутрь таска для избежания circular import
    post = Post.objects.get(pk=post_id)
    category = post.category
    subscribers = category.subscribers.all()

    for user in subscribers:
        html_content = render_to_string(
            'post_created_email.html',
            {'post': post, 'user': user}
        )

        msg = EmailMultiAlternatives(
            subject=f'Новая публикация в категории "{category.name}"',
            body='',
            from_email='noreply@newsportal.com',
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()


@shared_task
def send_weekly_digest():
    today = timezone.now()
    last_week = today - timezone.timedelta(days=7)
    posts = Post.objects.filter(created_at__gte=last_week)

    for category in Category.objects.all():
        category_posts = posts.filter(category=category)
        if not category_posts.exists():
            continue

        for user in category.subscribers.all():
            html_content = render_to_string(
                'weekly_digest_email.html',
                {'posts': category_posts, 'user': user, 'category': category}
            )

            msg = EmailMultiAlternatives(
                subject=f'Еженедельная рассылка: {category.name}',
                body='',
                from_email='noreply@newsportal.com',
                to=[user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
