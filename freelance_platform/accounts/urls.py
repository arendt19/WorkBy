from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'  # Определяем пространство имен приложения

urlpatterns = [
    # Аутентификация
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Пароль
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change_form.html',
        success_url='/accounts/password-change-done/'
    ), name='password_change'),
    path('password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url='/accounts/password-reset-done/'
    ), name='password_reset'),
    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/password-reset-complete/'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Профили
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('freelancer/<str:username>/', views.freelancer_detail_view, name='freelancer_detail'),
    path('client/<str:username>/', views.client_detail_view, name='client_detail'),
    path('client/edit/', views.profile_edit_view, name='client_edit'),
    
    # Портфолио
    path('portfolio/', views.portfolio_project_list_view, name='portfolio_list'),
    path('portfolio/create/', views.portfolio_project_create_view, name='portfolio_create'),
    path('portfolio/<int:pk>/', views.portfolio_project_detail_view, name='portfolio_detail'),
    path('portfolio/<int:pk>/edit/', views.portfolio_project_edit_view, name='portfolio_edit'),
    path('portfolio/<int:pk>/delete/', views.portfolio_project_delete_view, name='portfolio_delete'),
    
    # Отзывы
    path('freelancer/<int:freelancer_id>/review/<int:contract_id>/', views.create_review_view, name='create_review'),
    path('review/<int:review_id>/edit/', views.edit_review_view, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review_view, name='delete_review'),
    
    # Настройки
    path('change-language/<str:language_code>/', views.change_language_view, name='change_language'),
] 