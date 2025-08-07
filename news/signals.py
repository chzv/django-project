from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

def connect_signals():
    from allauth.account.signals import user_signed_up
    from django.contrib.auth.models import Group
    from django.core.mail import EmailMultiAlternatives, mail_managers
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from django.utils.timezone import now
    from .models import Post

    # 1. Добавление пользователя в группу + welcome письмо
    @receiver(user_signed_up)
    def add_user_to_common_group(request, user, **kwargs):
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name='common')
        user.groups.add(group)

        html_content = render_to_string('account/email/welcome.html', {
        'username': user.username,
        })
        msg = EmailMultiAlternatives(
            subject="Добро пожаловать в News Portal!",
            body=f"{user.username}, рады вас видеть!",
            from_email='your_email@yandex.ru',
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    # 2. Уведомление подписчиков при создании поста
    @receiver(post_save, sender=Post)
    def notify_subscribers(sender, instance, created, **kwargs):
        if not created:
            return

        # Ограничение: не более 3 постов в сутки
        today_posts = Post.objects.filter(
            author=instance.author,
            created_at__date=now().date()
        ).count()
        if today_posts > 3:
            return  # или log, или raise ValidationError — как нужно

        for category in instance.categories.all():
            for user in category.subscribers.all():
                html_content = render_to_string('account/email/post_created.html', {
                    'post': instance,
                    'username': user.username,
                })
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives(
                    subject=f'Новая НОВОСТЬ: {instance.title}',
                    body=text_content,
                    from_email='your_email@yandex.ru',
                    to=[user.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

    # 3. Уведомление менеджеров об удалении поста
    @receiver(post_delete, sender=Post)
    def notify_post_deleted(sender, instance, **kwargs):
        subject = f'Пост удалён: {instance.title}'
        message = f'Пост "{instance.title}" от автора {instance.author.user.username} был удалён.'
        mail_managers(subject=subject, message=message)
