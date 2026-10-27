from django.contrib.auth.models import User
from django.db import models


# ============================================================
# СЛОЙ 1. ПОЛЬЗОВАТЕЛИ И РОЛИ
# ============================================================

class Role(models.Model):
    """Роль пользователя в системе: оператор, администратор, исследователь."""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Расширение стандартной модели User: роль + данные оператора."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    full_name = models.CharField(max_length=200, blank=True)

    # Поля, актуальные для оператора
    department = models.CharField(max_length=200, blank=True)
    experience_years = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} ({self.role.name})"


# ============================================================
# СЛОЙ 2. КОНТЕНТ И ВАЛИДАЦИЯ
# ============================================================

class ContentType(models.Model):
    """Тип контента: сообщение, показание датчика, событие, тревога."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Content(models.Model):
    """Контент, который показывается оператору."""
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_auto_generated = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class HeavyWord(models.Model):
    """Слово или выражение, которое повышает когнитивную нагрузку."""
    word = models.CharField(max_length=100, unique=True)
    weight = models.PositiveIntegerField(default=1)
    suggestion = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.word


class ValidationRule(models.Model):
    """Правило валидации контента."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    rule_type = models.CharField(max_length=50)
    threshold = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ContentValidation(models.Model):
    """Результат проверки конкретного контента."""
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    validated_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField()
    is_passed = models.BooleanField()
    details = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.content.title}: {self.score}"


# ============================================================
# СЛОЙ 3. ПОВЕДЕНИЕ И АДАПТАЦИЯ
# ============================================================

class Session(models.Model):
    """Сеанс работы оператора в системе."""
    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.operator.username} @ {self.started_at}"


class Event(models.Model):
    """Отдельное событие в рамках сеанса: клик, просмотр, ошибка."""
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    target = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    reaction_time_ms = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.event_type} @ {self.timestamp}"


class SessionMetrics(models.Model):
    """Итоговые метрики сеанса."""
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    total_events = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    avg_reaction_time_ms = models.FloatField(default=0)
    idle_time_seconds = models.PositiveIntegerField(default=0)
    back_count = models.PositiveIntegerField(default=0)
    cognitive_load_score = models.FloatField(default=0)

    def __str__(self):
        return f"Metrics for session {self.session.id}"


class AdaptationRule(models.Model):
    """Правило адаптации интерфейса."""
    name = models.CharField(max_length=100)
    condition_metric = models.CharField(max_length=50)
    condition_operator = models.CharField(max_length=5)
    condition_value = models.FloatField()
    action = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AdaptationLog(models.Model):
    """Лог сработавших правил адаптации."""
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    rule = models.ForeignKey(AdaptationRule, on_delete=models.PROTECT)
    triggered_at = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.rule.name} @ {self.triggered_at}"

class EquipmentState(models.Model):
    """Текущее состояние технологической установки."""
    updated_at = models.DateTimeField(auto_now=True)
    
    # Температура (норма 70-85, авария > 95)
    temperature = models.FloatField(default=78.0)
    
    # Давление (норма 2.0-2.5, авария > 3.0)
    pressure = models.FloatField(default=2.4)
    
    # Уровень жидкости в резервуаре (норма 40-60%)
    tank_level = models.FloatField(default=50.0)
    
    # Флаги аварий
    is_temperature_critical = models.BooleanField(default=False)
    is_pressure_critical = models.BooleanField(default=False)

    def __str__(self):
        return f"Т: {self.temperature}°C, Д: {self.pressure} атм, Уровень: {self.tank_level}%"