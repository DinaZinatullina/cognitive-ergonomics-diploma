from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from core.models import (
    Role, UserProfile, ContentType, ValidationRule, HeavyWord, AdaptationRule,
)


class Command(BaseCommand):
    help = "Заполняет базу начальными данными: роли, типы контента, правила, слова."

    def handle(self, *args, **options):
        self.stdout.write("Заполняем базу начальными данными...")

        # --- Роли ---
        roles = [
            ("operator", "Оператор технологической установки"),
            ("admin", "Администратор системы"),
            ("researcher", "Исследователь поведения операторов"),
        ]
        for name, description in roles:
            Role.objects.get_or_create(name=name, defaults={"description": description})
        self.stdout.write(f"  Роли: {Role.objects.count()}")

        # --- Типы контента ---
        content_types = ["message", "sensor_reading", "event", "alert"]
        for name in content_types:
            ContentType.objects.get_or_create(name=name)
        self.stdout.write(f"  Типы контента: {ContentType.objects.count()}")

        # --- Правила валидации ---
        rules = [
            {
                "name": "Максимальная длина предложения",
                "description": "Предложение не должно содержать больше 20 слов.",
                "rule_type": "sentence_length",
                "threshold": 20,
            },
            {
                "name": "Наличие тяжёлых слов",
                "description": "Текст не должен содержать канцеляризмов и абстракций.",
                "rule_type": "heavy_word",
                "threshold": 0,
            },
            {
                "name": "Пассивный залог",
                "description": "Избегать пассивных конструкций там, где возможен активный залог.",
                "rule_type": "passive_voice",
                "threshold": 0,
            },
        ]
        for rule in rules:
            ValidationRule.objects.get_or_create(
                name=rule["name"], defaults=rule
            )
        self.stdout.write(f"  Правила валидации: {ValidationRule.objects.count()}")

        # --- Словарь тяжёлых слов ---
        heavy_words = [
            ("осуществление", 3, "выполнение", "канцеляризм"),
            ("произведение", 3, "выполнение", "канцеляризм"),
            ("является", 2, "это", "канцеляризм"),
            ("обеспечение", 2, "поддержка", "канцеляризм"),
            ("функционирование", 3, "работа", "канцеляризм"),
            ("оптимизация", 2, "улучшение", "абстракция"),
            ("реализация", 2, "внедрение", "абстракция"),
            ("имплементация", 4, "внедрение", "термин"),
            ("верификация", 3, "проверка", "термин"),
            ("валидация", 3, "проверка", "термин"),
            ("концептуальный", 3, "общий", "термин"),
            ("парадигма", 4, "подход", "термин"),
            ("идентификация", 3, "определение", "канцеляризм"),
            ("дифференциация", 4, "разделение", "термин"),
            ("трансформация", 3, "изменение", "канцеляризм"),
        ]
        for word, weight, suggestion, category in heavy_words:
            HeavyWord.objects.get_or_create(
                word=word,
                defaults={
                    "weight": weight,
                    "suggestion": suggestion,
                    "category": category,
                },
            )
        self.stdout.write(f"  Тяжёлых слов: {HeavyWord.objects.count()}")

        # --- Правила адаптации ---
        adaptation_rules = [
            {
                "name": "Упрощение при высокой когнитивной нагрузке",
                "condition_metric": "cognitive_load_score",
                "condition_operator": ">=",
                "condition_value": 0.7,
                "action": "simplify_ui",
            },
            {
                "name": "Подсказки при частых ошибках",
                "condition_metric": "error_count",
                "condition_operator": ">=",
                "condition_value": 3,
                "action": "show_hint",
            },
            {
                "name": "Увеличение шрифта при долгом простое",
                "condition_metric": "idle_time_seconds",
                "condition_operator": ">=",
                "condition_value": 30,
                "action": "increase_font",
            },
        ]
        for rule in adaptation_rules:
            AdaptationRule.objects.get_or_create(
                name=rule["name"], defaults=rule
            )
        self.stdout.write(f"  Правил адаптации: {AdaptationRule.objects.count()}")

        self.stdout.write(self.style.SUCCESS("Готово. База заполнена начальными данными."))