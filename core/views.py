from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    """Главный экран оператора. Доступен только авторизованным."""
    return render(request, 'operator/dashboard.html')