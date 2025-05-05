from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Главная и общие страницы
    path('', views.home_view, name='home'),
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/<int:pk>/', views.project_detail_view, name='project_detail'),
    path('about/', views.about_view, name='about'),
    path('categories/', views.category_list_view, name='categories'),
    path('tips-for-freelancers/', views.tips_for_freelancers_view, name='tips_for_freelancers'),
    
    # Управление проектами для клиентов
    path('projects/create/', views.project_create_view, name='project_create'),
    path('projects/<int:pk>/edit/', views.project_edit_view, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete_view, name='project_delete'),
    path('projects/<int:pk>/proposals/', views.project_proposals_view, name='project_proposals'),
    path('my-projects/', views.my_projects_view, name='my_projects'),
    
    # Управление предложениями для фрилансеров
    path('projects/<int:pk>/propose/', views.proposal_create_view, name='proposal_create'),
    path('proposals/<int:pk>/edit/', views.proposal_edit_view, name='proposal_edit'),
    path('proposals/<int:pk>/withdraw/', views.proposal_withdraw_view, name='proposal_withdraw'),
    path('proposals/<int:pk>/', views.proposal_detail_view, name='proposal_detail'),
    path('my-proposals/', views.my_proposals_view, name='my_proposals'),
    
    # Принятие предложений и создание контрактов
    path('proposals/<int:pk>/accept/', views.proposal_accept_view, name='proposal_accept'),
    path('proposals/<int:pk>/reject/', views.proposal_reject_view, name='proposal_reject'),
    path('contracts/create/', views.contract_create_view, name='contract_create'),
    path('contracts/<int:pk>/', views.contract_detail_view, name='contract_detail'),
    path('contracts/', views.contract_list_view, name='contract_list'),
    path('contracts/<int:pk>/complete/', views.contract_complete_view, name='contract_complete'),
    path('contracts/<int:pk>/review/', views.leave_review_view, name='leave_review'),
    
    # Управление вехами
    path('contracts/<int:pk>/milestones/create/', views.milestone_create_view, name='milestone_create'),
    path('milestones/<int:pk>/submit/', views.milestone_submit_view, name='milestone_submit'),
    path('milestones/<int:pk>/approve/', views.milestone_approve_view, name='milestone_approve'),
    path('milestones/<int:pk>/reject/', views.milestone_reject_view, name='milestone_reject'),
    
    # Завершение контракта и оплата
    path('milestones/<int:pk>/complete/', views.milestone_complete_view, name='milestone_complete'),
    
    # Категории
    path('categories/<slug:slug>/', views.category_detail_view, name='category_detail'),
    
    # Фрилансеры
    path('freelancers/', views.freelancer_list_view, name='freelancer_list'),
    
    # URL для обратной совместимости (единственное число)
    path('project/<int:pk>/propose/', views.proposal_create_view, name='proposal_create_singular'),
] 