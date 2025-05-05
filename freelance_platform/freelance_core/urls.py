"""
URL configuration for freelance_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _
from django.views.i18n import JavaScriptCatalog
from accounts import views as accounts_views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from .views import serve_robots_txt, serve_sitemap_xml
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Обработчики ошибок для production
handler404 = 'freelance_core.views.page_not_found'
handler500 = 'freelance_core.views.server_error'
handler403 = 'freelance_core.views.permission_denied'
handler400 = 'freelance_core.views.bad_request'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),  # Для переключения языков
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),  # Для переводов в JS
    
    # SEO файлы
    path('robots.txt', serve_robots_txt),
    path('sitemap.xml', serve_sitemap_xml),
]

# Маршруты с поддержкой языка в URL
urlpatterns += i18n_patterns(
    path('', include('jobs.urls')),  # Jobs приложение используется для главной страницы
    
    # Наши приложения (должны иметь приоритет над allauth)
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chat.urls')),
    path('payments/', include('payments.urls')),
    
    # Django allauth (размещаем после наших URLs)
    path('accounts/', include('allauth.urls')),
    
    # Legal pages
    path('about/', TemplateView.as_view(template_name='core/about.html'), name='about'),
    path('terms/', TemplateView.as_view(template_name='core/terms.html'), name='terms'),
    path('privacy/', TemplateView.as_view(template_name='core/privacy.html'), name='privacy'),
    
    # Error pages for testing
    path('400/', TemplateView.as_view(template_name='400.html'), name='error_400'),
    path('403/', TemplateView.as_view(template_name='403.html'), name='error_403'),
    path('404/', TemplateView.as_view(template_name='404.html'), name='error_404'),
    path('500/', TemplateView.as_view(template_name='500.html'), name='error_500'),
    
    prefix_default_language=True  
)

# Статические и медиа файлы в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
else:
    # В production режиме добавляем настройки для обслуживания медиа файлов
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
    
    # Add custom error handlers
    handler400 = 'core.views.error_400'
    handler403 = 'core.views.error_403'
    handler404 = 'core.views.error_404'
    handler500 = 'core.views.error_500'
