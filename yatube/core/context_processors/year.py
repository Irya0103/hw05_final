from django.utils import timezone


def year(request):
    """Добавлям переменную с текущим годом."""
    return {'year': timezone.now().year}
