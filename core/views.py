import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import Event, Session
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .validation import validate_text


@login_required
def dashboard(request):
    """Главный экран оператора."""
    # Тестовый текст, который мы выводим в лог
    test_event_text = "Осуществление процесса функционирования системы является важным этапом."
    
    # Валидируем его
    validation_result = validate_text(test_event_text)

    context = {
        'validation': validation_result,
        'log_text': test_event_text,
    }
    return render(request, 'operator/dashboard.html', context)


@require_POST
@login_required
def log_event(request):
    """Принимает событие от оператора и сохраняет в БД."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'invalid json'}, status=400)

    event_type = data.get('event_type')
    target = data.get('target', '')
    reaction_time_ms = data.get('reaction_time_ms')

    if not event_type:
        return JsonResponse({'ok': False, 'error': 'event_type required'}, status=400)

    # Находим активную сессию оператора
    session = Session.objects.filter(operator=request.user, is_active=True).first()
    if session is None:
        return JsonResponse({'ok': False, 'error': 'no active session'}, status=400)

    Event.objects.create(
        session=session,
        event_type=event_type,
        target=target,
        reaction_time_ms=reaction_time_ms,
    )
    return JsonResponse({'ok': True})


from datetime import timedelta

from django.utils import timezone

from .models import AdaptationLog


@login_required
def get_adaptation(request):
    """Возвращает действия адаптации, сработавшие за последние 10 секунд."""
    session = Session.objects.filter(operator=request.user, is_active=True).first()
    if session is None:
        return JsonResponse({'actions': []})

    threshold = timezone.now() - timedelta(seconds=10)
    logs = AdaptationLog.objects.filter(
        session=session,
        triggered_at__gte=threshold,
    ).select_related('rule')

    actions = [log.rule.action for log in logs]
    return JsonResponse({'actions': actions})