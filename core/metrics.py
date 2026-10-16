from .models import Event, SessionMetrics


def recalculate_session_metrics(session):
    """Пересчитывает метрики сессии на основе всех её событий."""
    events = session.event_set.all()

    total_events = events.count()
    error_count = events.filter(event_type='error').count()

    # Среднее время реакции (только по событиям, где оно указано)
    reactions = [e.reaction_time_ms for e in events if e.reaction_time_ms]
    avg_reaction = sum(reactions) / len(reactions) if reactions else 0

    # Простой: сколько секунд оператор не делал ничего
    # Считаем как разницу между первым и последним событием минус «активное время»
    idle_events = events.filter(event_type='idle')
    idle_time_seconds = 0
    if idle_events.exists():
        # Берём максимальное значение из target, например idle_60s → 60
        for e in idle_events:
            try:
                sec = int(e.target.replace('idle_', '').replace('s', ''))
                if sec > idle_time_seconds:
                    idle_time_seconds = sec
            except (ValueError, AttributeError):
                pass

    # cognitive_load_score — формула
    # 0.4 * (ошибки / 10) + 0.3 * (простой / 120) + 0.3 * (время реакции / 5000)
    score = (
        0.4 * min(error_count / 10, 1.0)
        + 0.3 * min(idle_time_seconds / 120, 1.0)
        + 0.3 * min(avg_reaction / 5000, 1.0)
    )
    score = round(score, 3)

    metrics, _ = SessionMetrics.objects.get_or_create(session=session)
    metrics.total_events = total_events
    metrics.error_count = error_count
    metrics.avg_reaction_time_ms = round(avg_reaction, 1)
    metrics.idle_time_seconds = idle_time_seconds
    metrics.cognitive_load_score = score
    metrics.save()

    apply_adaptation_rules(session)

    return metrics

from .adaptation import apply_adaptation_rules