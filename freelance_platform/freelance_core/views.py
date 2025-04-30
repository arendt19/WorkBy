from django.shortcuts import render
from django.http import HttpResponse
import os

def page_not_found(request, exception):
    """
    Обработчик ошибки 404 (страница не найдена)
    """
    return render(request, 'errors/404.html', status=404)

def server_error(request):
    """
    Обработчик ошибки 500 (внутренняя ошибка сервера)
    """
    return render(request, 'errors/500.html', status=500)

def permission_denied(request, exception):
    """
    Обработчик ошибки 403 (доступ запрещен)
    """
    return render(request, 'errors/403.html', status=403)

def bad_request(request, exception):
    """
    Обработчик ошибки 400 (плохой запрос)
    """
    return render(request, 'errors/400.html', status=400)

def serve_robots_txt(request):
    """
    Обслуживает файл robots.txt
    """
    from django.conf import settings
    
    robots_file = os.path.join(settings.STATIC_ROOT, 'robots.txt')
    if os.path.exists(robots_file):
        with open(robots_file, 'r') as f:
            content = f.read()
    else:
        content = "User-agent: *\nAllow: /\n\nSitemap: https://workby.onrender.com/sitemap.xml"
    
    return HttpResponse(content, content_type='text/plain')

def serve_sitemap_xml(request):
    """
    Обслуживает файл sitemap.xml
    """
    from django.conf import settings
    
    sitemap_file = os.path.join(settings.STATIC_ROOT, 'sitemap.xml')
    if os.path.exists(sitemap_file):
        with open(sitemap_file, 'r') as f:
            content = f.read()
    else:
        content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://workby.onrender.com/</loc>
        <lastmod>2024-04-30</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""
    
    return HttpResponse(content, content_type='application/xml') 