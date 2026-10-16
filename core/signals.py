from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Role, UserProfile, Session, Event


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """При создании нового пользователя автоматически создаём профиль с ролью 'оператор'."""
    if created:
        operator_role, _ = Role.objects.get_or_create(
            name='operator',
            defaults={'description': 'Оператор технологической установки'},
        )
        UserProfile.objects.create(
            user=instance,
            role=operator_role,
            full_name=instance.get_full_name() or instance.username,
        )

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone

from .session_utils import start_new_session


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    """При входе оператора — создаём новую сессию."""
    session = start_new_session(user)
    # Сохраняем ID сессии в сессии Django, чтобы JS мог её использовать
    request.session['current_session_id'] = session.id


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    """При выходе оператора — закрываем его активные сессии."""
    if user is None:
        return
    active_sessions = Session.objects.filter(operator=user, is_active=True)
    for session in active_sessions:
        session.is_active = False
        session.ended_at = timezone.now()
        session.save(update_fields=['is_active', 'ended_at'])

from django.db.models.signals import post_save

from .metrics import recalculate_session_metrics
from .models import Event


@receiver(post_save, sender=Event)
def on_event_created(sender, instance, created, **kwargs):
    """При создании нового события — пересчитываем метрики сессии."""
    if created:
        recalculate_session_metrics(instance.session)