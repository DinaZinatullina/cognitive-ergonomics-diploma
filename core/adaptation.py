from datetime import timedelta

from django.utils import timezone

from .models import AdaptationLog, AdaptationRule, SessionMetrics

# Через сколько минут одно и то же правило может сработать повторно
COOLDOWN_MINUTES = 5


def apply_adaptation_rules(session):
    """Проверяет все активные правила адаптации и записывает сработавшие в лог.

    Возвращает список действий, которые нужно применить в интерфейсе.
    """
    try:
        metrics = session.sessionmetrics
    except SessionMetrics.DoesNotExist:
        return []

    rules = AdaptationRule.objects.filter(is_active=True)
    applied_actions = []
    cooldown_threshold = timezone.now() - timedelta(minutes=COOLDOWN_MINUTES)

    for rule in rules:
        metric_value = getattr(metrics, rule.condition_metric, None)
        if metric_value is None:
            continue

        # Проверяем условие
        triggered = False
        if rule.condition_operator == '>=' and metric_value >= rule.condition_value:
            triggered = True
        elif rule.condition_operator == '>' and metric_value > rule.condition_value:
            triggered = True
        elif rule.condition_operator == '<=' and metric_value <= rule.condition_value:
            triggered = True
        elif rule.condition_operator == '<' and metric_value < rule.condition_value:
            triggered = True
        elif rule.condition_operator == '==' and metric_value == rule.condition_value:
            triggered = True

        if not triggered:
            continue

        # Проверяем cooldown: не срабатывало ли это правило недавно
        recent_log = AdaptationLog.objects.filter(
            session=session,
            rule=rule,
            triggered_at__gte=cooldown_threshold,
        ).exists()

        if recent_log:
            continue

        # Записываем в лог
        AdaptationLog.objects.create(
            session=session,
            rule=rule,
            details={
                'metric': rule.condition_metric,
                'value': float(metric_value),
                'threshold': rule.condition_value,
                'operator': rule.condition_operator,
                'action': rule.action,
            },
        )
        applied_actions.append(rule.action)

    return applied_actions