from django.contrib import admin
from .models import (
    Role, UserProfile,
    ContentType, Content, HeavyWord, ValidationRule, ContentValidation,
    Session, Event, SessionMetrics, AdaptationRule, AdaptationLog,
)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'full_name', 'department')
    list_filter = ('role',)


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'created_by', 'created_at', 'is_auto_generated')
    list_filter = ('content_type', 'is_auto_generated')


@admin.register(HeavyWord)
class HeavyWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'weight', 'category', 'suggestion')
    list_filter = ('category',)
    search_fields = ('word',)


@admin.register(ValidationRule)
class ValidationRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule_type', 'threshold', 'is_active')
    list_filter = ('rule_type', 'is_active')


@admin.register(ContentValidation)
class ContentValidationAdmin(admin.ModelAdmin):
    list_display = ('content', 'score', 'is_passed', 'validated_at')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('operator', 'started_at', 'ended_at', 'is_active')
    list_filter = ('is_active',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('session', 'event_type', 'target', 'timestamp')
    list_filter = ('event_type',)


@admin.register(SessionMetrics)
class SessionMetricsAdmin(admin.ModelAdmin):
    list_display = ('session', 'total_events', 'error_count', 'cognitive_load_score')


@admin.register(AdaptationRule)
class AdaptationRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'condition_metric', 'condition_operator', 'condition_value', 'action', 'is_active')
    list_filter = ('is_active',)


@admin.register(AdaptationLog)
class AdaptationLogAdmin(admin.ModelAdmin):
    list_display = ('session', 'rule', 'triggered_at')