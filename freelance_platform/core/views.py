from django.shortcuts import render

def serve_sitemap_xml(request):
    """
    Отдача sitemap.xml
    """
    return render(request, 'sitemap.xml', content_type='text/xml')


# Обработчики HTTP ошибок
def error_400(request, exception=None):
    """
    Обработчик ошибки 400 Bad Request
    """
    return render(request, '400.html', status=400)


def error_403(request, exception=None):
    """
    Обработчик ошибки 403 Forbidden
    """
    return render(request, '403.html', status=403)


def error_404(request, exception=None):
    """
    Обработчик ошибки 404 Not Found
    """
    return render(request, '404.html', status=404)


def error_500(request):
    """
    Обработчик ошибки 500 Internal Server Error
    """
    return render(request, '500.html', status=500) 