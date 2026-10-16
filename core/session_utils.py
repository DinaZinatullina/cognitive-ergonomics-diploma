from datetime import timedelta

from django.utils import timezone

from .models import Session

# Через сколько минут бездействия сессия считается завершённой
IDLE_TIMEOUT_MINUTES = 15


def close_stale_sessions(operator):
    """Закрывает все активные сессии оператора, которые простаивают дольше таймаута."""
    threshold = timezone.now() - timedelta(minutes=IDLE_TIMEOUT_MINUTES)
    stale_sessions = Session.objects.filter(
        operator=operator,
        is_active=True,
        started_at__lt=threshold,
    )
    for session in stale_sessions:
        # Проверяем, было ли что-то в сессии за последние 15 минут
        last_event = session.event_set.order_by('-timestamp').first()
        last_activity = last_event.timestamp if last_event else session.started_at
        if last_activity < threshold:
            session.is_active = False
            session.ended_at = last_activity
            session.save(update_fields=['is_active', 'ended_at'])


def start_new_session(operator):
    """Создаёт новую сессию для оператора, предварительно закрыв старые."""
    close_stale_sessions(operator)
    return Session.objects.create(operator=operator)