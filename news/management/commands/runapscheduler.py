import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from news.models import Post, Category

logger = logging.getLogger(__name__)


def weekly_digest():
    today = now()
    week_ago = today - timedelta(days=7)
    posts = Post.objects.filter(created_at__gte=week_ago)
    categories = Category.objects.all()

    for category in categories:
        category_posts = posts.filter(categories=category)
        if not category_posts.exists():
            continue

        subscribers = category.subscribers.all()
        for user in subscribers:
            html_content = render_to_string('email/weekly_digest.html', {
                'username': user.username,
                'category': category,
                'posts': category_posts,
            })

            msg = EmailMultiAlternatives(
                subject=f"Новые статьи в категории '{category.name}' за неделю",
                body="Смотрите подборку статей на сайте.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Запускает Apscheduler для рассылки"

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            weekly_digest,
            trigger=CronTrigger(day_of_week="fri", hour="18", minute="00"),
            id="weekly_digest",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Задача 'weekly_digest' добавлена.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )

        logger.info("Запускаем планировщик...")
        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
            logger.info("Планировщик остановлен.")
