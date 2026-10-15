from django.shortcuts import render


def dashboard(request):
    """Главный экран оператора."""
    return render(request, 'operator/dashboard.html')