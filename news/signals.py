
def connect_signals():
    from django.dispatch import receiver
    from allauth.account.signals import user_signed_up
    from django.contrib.auth.models import Group

    @receiver(user_signed_up)
    def add_user_to_common_group(request, user, **kwargs):
        group, _ = Group.objects.get_or_create(name='common')
        user.groups.add(group)
