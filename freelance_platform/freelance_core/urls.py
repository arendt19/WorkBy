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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),  # Для переключения языков
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),  # Для переводов в JS
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
    
    prefix_default_language=True  
)

# Статические и медиа файлы в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
