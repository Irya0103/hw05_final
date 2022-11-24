from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reasone=''):
    return render(request, 'core/403csrf.html')


def page_not_found_403(request, exception):
    return render(request, 'core/403.html', {'path': request.path}, status=403)


def page_not_found_500(request):
    return render(request, 'core/500.html', {'path': request.path}, status=500)
