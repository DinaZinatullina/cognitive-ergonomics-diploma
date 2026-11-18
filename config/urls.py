from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

# Вот здесь мы импортируем send_message, чтобы Django его видел
from core.views import (
    dashboard, 
    log_event, 
    get_adaptation, 
    api_equipment_status, 
    api_equipment_control, 
    stats_view,
    send_message
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('api/event/', log_event, name='log_event'),
    path('api/adaptation/', get_adaptation, name='get_adaptation'),
    path('api/equipment/', api_equipment_status, name='api_equipment'),
    path('api/equipment/control/', api_equipment_control, name='api_equipment_control'),
    path('stats/', stats_view, name='stats'),
    path('send-message/', send_message, name='send_message'), # <--- НАШ НОВЫЙ ПУТЬ
    path('', dashboard, name='dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')