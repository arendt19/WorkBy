from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Case, When, Value, IntegerField, Count, Avg
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseForbidden, JsonResponse
from django.forms import inlineformset_factory
from django.utils import timezone
from django.urls import reverse
from django.db import transaction
from decimal import Decimal
from django.db import models
from django.utils.functional import wraps
from django.utils.safestring import mark_safe
from accounts.models import Review
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Project, Category, Proposal, Contract, Milestone, Tag, ProjectView
from .recommendations import ProjectRecommendation
from .forms import (
    ProjectForm, ProposalForm, ContractForm, MilestoneForm, 
    MilestoneFormSet, ProjectSearchForm
)
from accounts.models import User, Review
from .notifications import (
    send_proposal_submitted_notification,
    send_proposal_accepted_notification,
    send_proposal_rejected_notification,
    send_contract_created_notification
)

def check_pending_reviews(view_func):
    """
    Декоратор, который проверяет наличие завершенных контрактов без отзывов
    и добавляет эту информацию в контекст
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Получаем ответ от исходного представления
        response = view_func(request, *args, **kwargs)
        
        # Проверяем, что пользователь авторизован и это объект TemplateResponse
        if hasattr(response, 'context_data') and request.user.is_authenticated:
            # Только для клиентов
            if request.user.is_client:
                # Находим завершенные контракты пользователя без отзывов
                completed_contracts = Contract.objects.filter(
                    client=request.user,
                    status='completed'
                )
                
                # Исключаем контракты, для которых уже оставлены отзывы
                contract_ids_with_reviews = Review.objects.filter(
                    client=request.user,
                    project__contracts__in=completed_contracts
                ).values_list('project__contracts__id', flat=True)
                
                contracts_without_reviews = completed_contracts.exclude(
                    id__in=contract_ids_with_reviews
                )
                
                # Добавляем информацию в контекст
                if contracts_without_reviews.exists():
                    response.context_data['pending_reviews'] = contracts_without_reviews
                    response.context_data['pending_reviews_count'] = contracts_without_reviews.count()
        
        return response
    
    return wrapper

def home_view(request):
    """
    Отображение главной страницы с последними проектами
    """
    # Активируем язык из запроса
    from django.utils import translation
    from django.conf import settings
    
    # Получаем язык из сессии, cookie или заголовка HTTP_ACCEPT_LANGUAGE
    if hasattr(request, 'LANGUAGE_CODE') and request.LANGUAGE_CODE:
        user_language = request.LANGUAGE_CODE
    else:
        # Язык из cookie
        lang_code = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if lang_code and lang_code in [lang[0] for lang in settings.LANGUAGES]:
            user_language = lang_code
        else:
            # Используем язык по умолчанию
            user_language = settings.LANGUAGE_CODE
            
    # Принудительно активируем язык
    translation.activate(user_language)
    request.LANGUAGE_CODE = user_language
    # Устанавливаем язык в ответ
    response = None
    # Получаем открытые проекты, отсортированные по дате создания
    projects = Project.objects.filter(status='open').order_by('-created_at')[:8]
    categories = Category.objects.all()
    
    # Счетчики для статистики
    projects_count = Project.objects.count()
    freelancers_count = User.objects.filter(user_type='freelancer').count()
    clients_count = User.objects.filter(user_type='client').count()
    
    # Получаем топовых фрилансеров с высоким рейтингом
    top_freelancers = User.objects.filter(
        user_type='freelancer',
        freelancer_profile__rating__gt=0  # Только с рейтингом больше 0
    ).annotate(
        reviews_count=Count('reviews_received')
    ).filter(
        reviews_count__gt=0  # Только с отзывами
    ).order_by(
        '-freelancer_profile__rating',  # Сортировка по рейтингу (высокий сначала)
        '-reviews_count'  # При одинаковом рейтинге - по количеству отзывов
    )[:8]  # Ограничиваем 8 фрилансерами
    
    context = {
        'projects': projects,
        'categories': categories,
        'projects_count': projects_count,
        'freelancers_count': freelancers_count,
        'clients_count': clients_count,
        'top_freelancers': top_freelancers,
    }
    
    # Создаем ответ с языковыми настройками
    response = render(request, 'jobs/home.html', context)
    
    # Устанавливаем cookie языка, если он отличается от того, что уже установлен
    if response and user_language:
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME, 
            user_language,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )
    
    return response

def project_list_view(request):
    """
    Отображение списка проектов с фильтрацией
    """
    form = ProjectSearchForm(request.GET)
    projects = Project.objects.filter(status='open')
    
    if form.is_valid():
        # Фильтрация по поисковому запросу
        query = form.cleaned_data.get('query')
        if query:
            projects = projects.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            ).distinct()
        
        # Фильтрация по категории
        category = form.cleaned_data.get('category')
        if category:
            projects = projects.filter(category=category)
        
        # Фильтрация по тегам/навыкам
        tags = form.cleaned_data.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            for tag in tag_list:
                projects = projects.filter(tags__name__icontains=tag).distinct()
        
        # Фильтрация по бюджету
        min_budget = form.cleaned_data.get('min_budget')
        if min_budget:
            projects = projects.filter(budget_min__gte=min_budget)
        
        max_budget = form.cleaned_data.get('max_budget')
        if max_budget:
            projects = projects.filter(budget_max__lte=max_budget)
        
        # Фильтрация по типу бюджета
        budget_type = form.cleaned_data.get('budget_type')
        if budget_type:
            projects = projects.filter(budget_type=budget_type)
        
        # Фильтрация по удаленной работе
        is_remote = form.cleaned_data.get('is_remote')
        if is_remote:
            projects = projects.filter(is_remote=True)
        
        # Фильтрация по местоположению
        location = form.cleaned_data.get('location')
        if location:
            projects = projects.filter(location_required__icontains=location)
        
        # Фильтрация по опыту
        experience_level = form.cleaned_data.get('experience_level')
        if experience_level:
            if experience_level == 'entry':
                # Начальный уровень обычно подразумевает опыт < 1-2 года
                projects = projects.filter(
                    Q(experience_required__icontains='entry') | 
                    Q(experience_required__icontains='begin') |
                    Q(experience_required__icontains='junior') |
                    Q(experience_required__icontains='starter')
                )
            elif experience_level == 'intermediate':
                projects = projects.filter(
                    Q(experience_required__icontains='intermediate') | 
                    Q(experience_required__icontains='middle') |
                    Q(experience_required__icontains='mid')
                )
            elif experience_level == 'expert':
                projects = projects.filter(
                    Q(experience_required__icontains='expert') | 
                    Q(experience_required__icontains='senior') |
                    Q(experience_required__icontains='advanced')
                )
        
        # Сортировка результатов
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by:
            if sort_by == 'recent':
                projects = projects.order_by('-created_at')
            elif sort_by == 'budget_high':
                projects = projects.order_by('-budget_max')
            elif sort_by == 'budget_low':
                projects = projects.order_by('budget_min')
            elif sort_by == 'deadline':
                # Проекты без дедлайна будут в конце списка
                projects = projects.annotate(
                    has_deadline=Case(
                        When(deadline__isnull=False, then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ).order_by('-has_deadline', 'deadline')
    else:
        # По умолчанию сортируем по дате создания (новые вверху)
        projects = projects.order_by('-created_at')
    
    # Получаем список популярных тегов для отображения
    popular_tags = Tag.objects.annotate(
        project_count=Count('projects')
    ).order_by('-project_count')[:10]
    
    # Проверяем, на какие проекты текущий пользователь уже подал заявки
    user_proposals = {}
    if request.user.is_authenticated and request.user.user_type == 'freelancer':
        # Получаем ID всех проектов, на которые пользователь подал предложения
        user_proposal_projects = Proposal.objects.filter(
            freelancer=request.user,
            project__in=projects
        ).values_list('project_id', flat=True)
        
        # Создаем словарь для быстрой проверки
        for project_id in user_proposal_projects:
            user_proposals[project_id] = True
    
    context = {
        'projects': projects,
        'form': form,
        'popular_tags': popular_tags,
        'total_count': projects.count(),
        'user_proposals': user_proposals,
    }
    
    return render(request, 'jobs/project_list.html', context)

def project_detail_view(request, pk):
    """
    Отображение детальной информации о проекте
    """
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем, подавал ли текущий пользователь (если фрилансер) предложение на этот проект
    user_proposal = None
    if request.user.is_authenticated and request.user.user_type == 'freelancer':
        user_proposal = Proposal.objects.filter(project=project, freelancer=request.user).first()
    
    # Получаем похожие проекты (в той же категории)
    similar_projects = Project.objects.filter(
        category=project.category, 
        status='open'
    ).exclude(pk=project.pk).order_by('-created_at')[:5]
    
    context = {
        'project': project,
        'user_proposal': user_proposal,
        'similar_projects': similar_projects,
    }
    
    return render(request, 'jobs/project_detail.html', context)

@login_required
def project_create_view(request):
    """
    Создание нового проекта (доступно всем пользователям)
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            # Проверяем, был ли уже создан проект с таким же названием от этого пользователя за последний час
            # Это поможет избежать дублирования при случайном повторном отправлении формы
            from django.utils import timezone
            import datetime
            recent_time = timezone.now() - datetime.timedelta(hours=1)
            
            if Project.objects.filter(
                client=request.user,
                title=form.cleaned_data['title'],
                created_at__gte=recent_time
            ).exists():
                # Если проект уже существует, просто перенаправляем на страницу успеха
                # и показываем сообщение пользователю
                messages.info(request, _('This project has already been created recently'))
                # Получаем последний созданный проект пользователя
                project = Project.objects.filter(
                    client=request.user,
                    title=form.cleaned_data['title']
                ).order_by('-created_at').first()
                return redirect('jobs:project_detail', pk=project.pk)
            
            # Создаем новый проект
            project = form.save(commit=False)
            project.client = request.user
            project.status = 'open'  # Автоматически делаем проект открытым
            project.save()
            
            # Для сохранения тегов
            form.save_m2m()
            
            messages.success(request, _('Project created successfully'))
            return redirect('jobs:project_create_success', pk=project.pk)
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'title': _('Post New Project'),
    }
    
    return render(request, 'jobs/project_form.html', context)

@login_required
def project_create_success_view(request, pk):
    """
    Отображение страницы успешного создания проекта
    """
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем, что проект принадлежит текущему пользователю
    if project.client != request.user:
        return HttpResponseForbidden(_('You do not have permission to view this page'))
    
    return render(request, 'jobs/project_create_success.html', {'project': project})

@login_required
def project_edit_view(request, pk):
    """
    Редактирование проекта (только владелец проекта)
    """
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем, что пользователь является владельцем проекта
    if project.client != request.user:
        return HttpResponseForbidden(_('You do not have permission to edit this project'))
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, _('Project updated successfully'))
            return redirect('jobs:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'title': _('Edit Project'),
        'project': project,
    }
    
    return render(request, 'jobs/project_form.html', context)

@login_required
def project_delete_view(request, pk):
    """
    Удаление проекта (только владелец проекта)
    """
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем, что пользователь является владельцем проекта
    if project.client != request.user:
        return HttpResponseForbidden(_('You do not have permission to delete this project'))
    
    if request.method == 'POST':
        project.status = 'cancelled'  # Мягкое удаление - меняем статус на отмененный
        project.save()
        messages.success(request, _('Project cancelled successfully'))
        return redirect('jobs:my_projects')
    
    context = {
        'project': project,
    }
    
    return render(request, 'jobs/project_confirm_delete.html', context)

@login_required
def proposal_create_view(request, pk):
    """
    Создание предложения по проекту
    """
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем, что проект открыт
    if project.status != 'open':
        messages.error(request, _('This project is not open for proposals'))
        return redirect('jobs:project_detail', pk=pk)
    
    # Проверяем, не является ли пользователь создателем проекта
    if project.client == request.user:
        messages.error(request, _('You cannot submit proposals to your own projects'))
        return redirect('jobs:project_detail', pk=pk)
    
    # Проверяем, не отправлял ли пользователь уже предложение
    existing_proposal = Proposal.objects.filter(project=project, freelancer=request.user).first()
    
    if existing_proposal:
        messages.info(request, _('You have already submitted a proposal for this project'))
        return redirect('jobs:proposal_detail', pk=existing_proposal.pk)
    
    if request.method == 'POST':
        form = ProposalForm(project, request.POST, request.FILES)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.freelancer = request.user
            proposal.project = project
            proposal.save()
            
            # Отправляем уведомление клиенту
            send_proposal_submitted_notification(proposal)
            
            # Возвращаем JSON-ответ для AJAX-запросов
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': _('Your proposal has been submitted successfully'),
                    'redirect_url': reverse('jobs:project_detail', kwargs={'pk': project.pk}) + '?proposal_submitted=1'
                })
            
            # Добавляем сообщение об успешной отправке
            messages.success(request, _('Your proposal has been submitted successfully'))
            
            # Реализация паттерна PRG: перенаправляем на страницу деталей проекта
            return redirect('jobs:project_detail', pk=project.pk)
        elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Возвращаем ошибки для AJAX-запросов
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data()
            }, status=400)
    else:
        form = ProposalForm(project)
    
    context = {
        'form': form,
        'project': project,
    }
    
    return render(request, 'jobs/proposal_form.html', context)

@login_required
def proposal_edit_view(request, pk):
    """
    Редактирование предложения (только владелец предложения)
    """
    proposal = get_object_or_404(Proposal, pk=pk)
    
    # Проверяем, что пользователь является владельцем предложения
    if proposal.freelancer != request.user:
        return HttpResponseForbidden(_('You do not have permission to edit this proposal'))
    
    # Проверяем, что предложение все еще в статусе ожидания
    if proposal.status != 'pending':
        messages.error(request, _('This proposal can no longer be edited'))
        return redirect('jobs:proposal_detail', pk=proposal.pk)
    
    if request.method == 'POST':
        form = ProposalForm(proposal.project, request.POST, request.FILES, instance=proposal)
        if form.is_valid():
            form.save()
            messages.success(request, _('Proposal updated successfully'))
            
            # Возвращаем JSON-ответ для AJAX-запросов
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': _('Your proposal has been updated successfully'),
                    'redirect_url': reverse('jobs:proposal_detail', kwargs={'pk': proposal.pk})
                })
            
            return redirect('jobs:proposal_detail', pk=proposal.pk)
        elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Возвращаем ошибки для AJAX-запросов
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data()
            }, status=400)
    else:
        form = ProposalForm(proposal.project, instance=proposal)
    
    context = {
        'form': form,
        'proposal': proposal,
        'project': proposal.project,
    }
    
    return render(request, 'jobs/proposal_form.html', context)

@login_required
def proposal_withdraw_view(request, pk):
    """
    Отзыв предложения (только владелец предложения)
    """
    proposal = get_object_or_404(Proposal, pk=pk)
    
    # Проверяем, что пользователь является владельцем предложения
    if proposal.freelancer != request.user:
        return HttpResponseForbidden(_('You do not have permission to withdraw this proposal'))
    
    # Проверяем, что предложение может быть отозвано
    if proposal.status not in ['pending', 'accepted']:
        messages.error(request, _('This proposal cannot be withdrawn'))
        return redirect('jobs:proposal_detail', pk=proposal.pk)
    
    if request.method == 'POST':
        proposal.status = 'withdrawn'
        proposal.save()
        messages.success(request, _('Proposal withdrawn successfully'))
        return redirect('jobs:my_proposals')
    
    context = {
        'proposal': proposal,
    }
    
    return render(request, 'jobs/proposal_confirm_withdraw.html', context)

@login_required
def proposal_detail_view(request, pk):
    """
    Просмотр деталей предложения
    """
    proposal = get_object_or_404(Proposal, pk=pk)
    
    # Проверяем, что пользователь имеет право просматривать предложение
    if proposal.freelancer != request.user and proposal.project.client != request.user:
        return HttpResponseForbidden(_('You do not have permission to view this proposal'))
    
    context = {
        'proposal': proposal,
        'project': proposal.project,
    }
    
    return render(request, 'jobs/proposal_detail.html', context)

@login_required
def my_projects_view(request):
    """
    Список проектов текущего пользователя (доступно всем пользователям)
    """
    # Для клиентов показываем их проекты
    if request.user.user_type == 'client':
        projects = Project.objects.filter(client=request.user)
    else:
        # Для фрилансеров показываем проекты, по которым у них есть принятые предложения
        accepted_proposals = Proposal.objects.filter(
            freelancer=request.user, 
            status='accepted'
        ).values_list('project_id', flat=True)
        projects = Project.objects.filter(id__in=accepted_proposals)
    
    # Фильтрация по статусу
    status = request.GET.get('status')
    if status:
        projects = projects.filter(status=status)
    
    context = {
        'projects': projects,
    }
    
    return render(request, 'jobs/my_projects.html', context)

@login_required
def my_proposals_view(request):
    """
    Список предложений пользователя (доступно всем пользователям)
    """
    if request.user.user_type == 'freelancer':
        # Для фрилансеров показываем их предложения
        proposals = Proposal.objects.filter(freelancer=request.user)
        
        # Подсчитываем количество предложений по статусам
        pending_count = proposals.filter(status='pending').count()
        accepted_count = proposals.filter(status='accepted').count()
        rejected_count = proposals.filter(status='rejected').count()
        withdrawn_count = proposals.filter(status='withdrawn').count()
    else:
        # Для клиентов показываем предложения на их проекты
        projects = Project.objects.filter(client=request.user).values_list('id', flat=True)
        proposals = Proposal.objects.filter(project_id__in=projects)
        
        # Подсчитываем количество предложений по статусам
        pending_count = proposals.filter(status='pending').count()
        accepted_count = proposals.filter(status='accepted').count()
        rejected_count = proposals.filter(status='rejected').count()
        withdrawn_count = proposals.filter(status='withdrawn').count()
    
    # Фильтрация по статусу
    status = request.GET.get('status')
    if status:
        proposals = proposals.filter(status=status)
    
    context = {
        'proposals': proposals,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'rejected_count': rejected_count,
        'withdrawn_count': withdrawn_count,
    }
    
    return render(request, 'jobs/my_proposals.html', context)

@login_required
def proposal_accept_view(request, pk):
    """
    Принятие предложения (только для клиента, владельца проекта)
    """
    proposal = get_object_or_404(Proposal, pk=pk)
    
    # Проверяем, что пользователь является владельцем проекта
    if proposal.project.client != request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': _('You do not have permission to accept this proposal')
            }, status=403)
        return HttpResponseForbidden(_('You do not have permission to accept this proposal'))
    
    # Проверяем, что предложение в статусе ожидания
    if proposal.status != 'pending':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': _('This proposal is not pending and cannot be accepted')
            }, status=400)
        messages.error(request, _('This proposal is not pending and cannot be accepted'))
        return redirect('jobs:proposal_detail', pk=proposal.pk)
    
    # Проверяем, что проект открыт
    if proposal.project.status != 'open':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': _('This project is not open and proposals cannot be accepted')
            }, status=400)
        messages.error(request, _('This project is not open and proposals cannot be accepted'))
        return redirect('jobs:proposal_detail', pk=proposal.pk)
    
    if request.method == 'POST':
        with transaction.atomic():
            # Обновляем статус предложения
            proposal.status = 'accepted'
            proposal.save()
            
            # Обновляем статус проекта
            proposal.project.status = 'in_progress'
            proposal.project.save()
            
            # Отклоняем остальные предложения
            Proposal.objects.filter(project=proposal.project).exclude(pk=proposal.pk).update(status='rejected')
            
            # Автоматически создаем контракт
            contract = Contract.objects.create(
                client=request.user,
                freelancer=proposal.freelancer,
                project=proposal.project,
                proposal=proposal,
                title=proposal.project.title,
                description=proposal.project.description,
                amount=proposal.bid_amount,
                deadline=timezone.now() + timezone.timedelta(days=proposal.delivery_time)
            )
            
            # Автоматически создаем первую веху для контракта
            from .models import Milestone
            milestone_title = _('Initial milestone')
            milestone_description = _('First milestone for the project "{0}". Please discuss with the client to define deliverables and requirements.').format(proposal.project.title)
            
            # Устанавливаем дату для первой вехи - половина срока контракта
            milestone_due_date = timezone.now() + timezone.timedelta(days=proposal.delivery_time // 2)
            
            # Первая веха - половина суммы контракта
            milestone_amount = proposal.bid_amount / 2
            
            Milestone.objects.create(
                contract=contract,
                title=milestone_title,
                description=milestone_description,
                amount=milestone_amount,
                due_date=milestone_due_date,
                status='pending',
                payment_status='not_paid'
            )
            
            # Отправляем уведомление фрилансеру о принятии предложения
            send_proposal_accepted_notification(proposal)
            
            # Отправляем уведомления о создании контракта
            send_contract_created_notification(contract)
            
            # Формируем сообщение с кнопкой перехода к контракту
            project_title = proposal.project.title
            contract_url = reverse('jobs:contract_detail', kwargs={'pk': contract.pk})
            success_message = f'''
            <div class="d-flex align-items-center justify-content-between flex-wrap">
                <span>{_('Proposal accepted! Contract for project "' + project_title + '" has been created.')}</span>
                <a href="{contract_url}" class="btn btn-primary btn-sm ms-3 mt-2 mt-md-0">
                    <i class="fas fa-file-contract me-1"></i> {_('View Contract')}
                </a>
            </div>
            '''
            
            # Для AJAX запросов
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': _('Proposal accepted successfully and contract created'),
                    'redirect_url': reverse('jobs:contract_detail', kwargs={'pk': contract.pk})
                })
            
            messages.success(request, mark_safe(success_message))
            return redirect('jobs:contract_detail', pk=contract.pk)
    
    # Для AJAX запросов в случае, если это не POST
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'message': _('Invalid request method')
        }, status=400)
    
    context = {
        'proposal': proposal,
    }
    
    return render(request, 'jobs/proposal_confirm_accept.html', context)

@login_required
def contract_create_view(request):
    """
    Создание контракта после принятия предложения
    """
    proposal_pk = request.GET.get('proposal')
    if not proposal_pk:
        messages.error(request, _('No proposal specified'))
        return redirect('jobs:my_projects')
    
    proposal = get_object_or_404(Proposal, pk=proposal_pk)
    
    # Проверяем, что пользователь является владельцем проекта
    if proposal.project.client != request.user:
        return HttpResponseForbidden(_('You do not have permission to create a contract for this proposal'))
    
    # Проверяем, что предложение принято
    if proposal.status != 'accepted':
        messages.error(request, _('You can only create contracts for accepted proposals'))
        return redirect('jobs:proposal_detail', pk=proposal.pk)
    
    # Проверяем, не создан ли уже контракт для этого предложения
    existing_contract = Contract.objects.filter(proposal=proposal).first()
    if existing_contract:
        messages.info(request, _('A contract already exists for this proposal'))
        return redirect('jobs:contract_detail', pk=existing_contract.pk)
    
    if request.method == 'POST':
        contract_form = ContractForm(request.POST)
        
        if contract_form.is_valid():
            contract = contract_form.save(commit=False)
            contract.client = request.user
            contract.freelancer = proposal.freelancer
            contract.project = proposal.project
            contract.proposal = proposal
            contract.save()
            
            # Создаём одну веху автоматически (если выбрана полная оплата)
            payment_option = request.POST.get('payment_option', 'full')
            if payment_option == 'full':
                # Создаем одну веху для полной оплаты
                milestone = Milestone.objects.create(
                    contract=contract,
                    title=_('Complete Project'),
                    description=_('Full payment upon completion of all work'),
                    amount=contract.amount,
                    due_date=contract.deadline,
                    status='pending'
                )
            
            messages.success(request, _('Contract created successfully! You can now communicate with the freelancer to get started.'))
            return redirect('jobs:contract_detail', pk=contract.pk)
    else:
        # Предзаполняем форму контракта данными из предложения и проекта
        initial = {
            'title': proposal.project.title,
            'description': proposal.project.description,
            'amount': proposal.bid_amount,
            'deadline': timezone.now() + timezone.timedelta(days=proposal.delivery_time)
        }
        contract_form = ContractForm(initial=initial)
    
    context = {
        'contract_form': contract_form,
        'proposal': proposal,
        'project': proposal.project,
    }
    
    return render(request, 'jobs/contract_form.html', context)

@login_required
def contract_detail_view(request, pk):
    """
    Просмотр деталей контракта
    """
    contract = get_object_or_404(Contract, pk=pk)
    
    # Проверяем, что пользователь является стороной контракта
    if contract.client != request.user and contract.freelancer != request.user:
        return HttpResponseForbidden(_('You do not have permission to view this contract'))
    
    milestones = contract.milestones.all()
    
    context = {
        'contract': contract,
        'milestones': milestones,
    }
    
    return render(request, 'jobs/contract_detail.html', context)

@login_required
def contract_list_view(request):
    """
    Список контрактов пользователя с расширенными фильтрами и сортировкой
    """
    if request.user.user_type == 'client':
        contracts = Contract.objects.filter(client=request.user)
    else:
        contracts = Contract.objects.filter(freelancer=request.user)
    
    # Получаем количество контрактов для каждого статуса
    all_count = contracts.count()
    active_count = contracts.filter(status='active').count()
    completed_count = contracts.filter(status='completed').count()
    paused_count = contracts.filter(status='paused').count()
    cancelled_count = contracts.filter(status='cancelled').count()
    disputed_count = contracts.filter(status='disputed').count()
    
    # Фильтрация по вкладке (статусу)
    active_tab = request.GET.get('tab', 'all')
    
    if active_tab == 'active':
        contracts = contracts.filter(status='active')
    elif active_tab == 'completed':
        contracts = contracts.filter(status='completed')
    elif active_tab == 'paused':
        contracts = contracts.filter(status='paused')
    elif active_tab == 'cancelled':
        contracts = contracts.filter(status='cancelled')
    elif active_tab == 'disputed':
        contracts = contracts.filter(status='disputed')
    
    # Поиск по названию или ID
    search_query = request.GET.get('search', '')
    if search_query:
        contracts = contracts.filter(
            Q(title__icontains=search_query) | 
            Q(contract_id__icontains=search_query) |
            Q(project__title__icontains=search_query)
        )
    
    # Фильтрация по дате создания
    date_from = request.GET.get('date_from')
    if date_from:
        try:
            date_from = timezone.datetime.strptime(date_from, "%Y-%m-%d").date()
            contracts = contracts.filter(created_at__date__gte=date_from)
        except ValueError:
            pass
    
    date_to = request.GET.get('date_to')
    if date_to:
        try:
            date_to = timezone.datetime.strptime(date_to, "%Y-%m-%d").date()
            contracts = contracts.filter(created_at__date__lte=date_to)
        except ValueError:
            pass
    
    # Фильтрация по сумме контракта
    min_amount = request.GET.get('min_amount')
    if min_amount and min_amount.isdigit():
        contracts = contracts.filter(amount__gte=Decimal(min_amount))
    
    max_amount = request.GET.get('max_amount')
    if max_amount and max_amount.isdigit():
        contracts = contracts.filter(amount__lte=Decimal(max_amount))
    
    # Сортировка результатов
    sort_by = request.GET.get('sort', '-created_at')
    valid_sort_fields = ['created_at', '-created_at', 'deadline', '-deadline', 'amount', '-amount']
    
    if sort_by in valid_sort_fields:
        contracts = contracts.order_by(sort_by)
    else:
        contracts = contracts.order_by('-created_at')  # По умолчанию сортируем по дате создания (новые вначале)
    
    # Пагинация
    contracts_per_page = int(request.GET.get('per_page', 10))  # Позволяем выбирать количество записей на странице
    paginator = Paginator(contracts, contracts_per_page)
    page = request.GET.get('page')
    
    try:
        contracts_page = paginator.page(page)
    except PageNotAnInteger:
        contracts_page = paginator.page(1)
    except EmptyPage:
        contracts_page = paginator.page(paginator.num_pages)
    
    # Сохраняем параметры фильтрации для URL пагинации
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    
    context = {
        'contracts': contracts_page,
        'active_tab': active_tab,
        'all_count': all_count,
        'active_count': active_count,
        'completed_count': completed_count,
        'paused_count': paused_count,
        'cancelled_count': cancelled_count,
        'disputed_count': disputed_count,
        'search_query': search_query,
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'min_amount': min_amount,
        'max_amount': max_amount,
        'sort_by': sort_by,
        'per_page': contracts_per_page,
        'query_params': query_params.urlencode(),
    }
    
    return render(request, 'jobs/contract_list.html', context)

@login_required
def milestone_submit_view(request, pk):
    """
    Отправка вехи на проверку (для фрилансера)
    """
    milestone = get_object_or_404(Milestone, pk=pk)
    
    # Проверяем, что пользователь является фрилансером контракта
    if milestone.contract.freelancer != request.user:
        return HttpResponseForbidden(_('You do not have permission to submit this milestone'))
    
    # Проверяем, что веха находится в работе
    if milestone.status != 'in_progress':
        messages.error(request, _('This milestone is not in progress and cannot be submitted'))
        return redirect('jobs:contract_detail', pk=milestone.contract.pk)
    
    if request.method == 'POST':
        milestone.status = 'submitted'
        milestone.save()
        
        messages.success(request, _('Milestone submitted for approval'))
        return redirect('jobs:contract_detail', pk=milestone.contract.pk)
    
    context = {
        'milestone': milestone,
    }
    
    return render(request, 'jobs/milestone_submit.html', context)

@login_required
def milestone_approve_view(request, pk):
    """
    Подтверждение выполнения вехи (для клиента)
    """
    milestone = get_object_or_404(Milestone, pk=pk)
    
    # Проверяем, что пользователь является клиентом контракта
    if milestone.contract.client != request.user:
        return HttpResponseForbidden(_('You do not have permission to approve this milestone'))
    
    # Проверяем, что веха отправлена на проверку
    if milestone.status != 'submitted':
        messages.error(request, _('This milestone is not submitted and cannot be approved'))
        return redirect('jobs:contract_detail', pk=milestone.contract.pk)
    
    if request.method == 'POST':
        milestone.status = 'approved'
        milestone.save()
        
        # Проверяем, все ли вехи выполнены
        all_milestones_completed = all(
            m.status == 'approved' for m in milestone.contract.milestones.all()
        )
        
        # Если все вехи выполнены, завершаем контракт
        if all_milestones_completed:
            milestone.contract.status = 'completed'
            milestone.contract.save()
            
            # Завершаем проект
            milestone.contract.project.status = 'completed'
            milestone.contract.project.save()
        
        messages.success(request, _('Milestone approved successfully'))
        return redirect('jobs:contract_detail', pk=milestone.contract.pk)
    
    context = {
        'milestone': milestone,
    }
    
    return render(request, 'jobs/milestone_approve.html', context)

@login_required
def milestone_reject_view(request, pk):
    """
    Отклонение вехи (для клиента)
    """
    milestone = get_object_or_404(Milestone, pk=pk)
    
    # Проверяем, что пользователь является клиентом контракта
    if milestone.contract.client != request.user:
        return HttpResponseForbidden(_('You do not have permission to reject this milestone'))
    
    # Проверяем, что веха отправлена на проверку
    if milestone.status != 'submitted':
        messages.error(request, _('This milestone is not submitted and cannot be rejected'))
        return redirect('jobs:contract_detail', pk=milestone.contract.pk)
    
    if request.method == 'POST':
        milestone.status = 'in_progress'  # Возвращаем в работу
        milestone.save()
        
        messages.success(request, _('Milestone rejected and returned for revision'))
        return redirect('jobs:contract_detail', pk=milestone.contract.pk)
    
    context = {
        'milestone': milestone,
    }
    
    return render(request, 'jobs/milestone_reject.html', context)

@login_required
@transaction.atomic
def contract_complete_view(request, pk):
    """
    Завершение контракта и перевод средств фрилансеру (для клиента)
    """
    contract = get_object_or_404(Contract, pk=pk)
    
    # Проверяем, что пользователь является клиентом контракта
    if contract.client != request.user:
        return HttpResponseForbidden(_('You do not have permission to complete this contract'))
    
    # Проверяем, что контракт в активном статусе
    if contract.status != 'active':
        messages.error(request, _('This contract cannot be completed because it is not active'))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    if request.method == 'POST':
        try:
            # Получаем кошельки клиента и фрилансера
            from payments.models import Wallet
            
            client_wallet = Wallet.objects.get(user=contract.client)
            freelancer_wallet = Wallet.objects.get(user=contract.freelancer)
            
            # Проверяем, достаточно ли средств на счету клиента
            if client_wallet.balance < contract.amount:
                messages.error(request, _('Insufficient funds to complete this contract. Please top up your wallet.'))
                return redirect('payments:wallet')
            
            # Расчет комиссии сервиса (5%)
            service_fee = contract.amount * Decimal('0.05')
            freelancer_amount = contract.amount - service_fee
            
            # Снимаем средства с кошелька клиента
            client_wallet.withdraw(
                contract.amount,
                description=_(f'Payment for contract "{contract.title}" (#{contract.contract_id})'),
                contract=contract
            )
            
            # Пополняем кошелек фрилансера (за вычетом комиссии)
            freelancer_wallet.deposit(
                freelancer_amount,
                description=_(f'Payment received for contract "{contract.title}" (#{contract.contract_id})'),
                contract=contract
            )
            
            # Обновляем статус контракта и проекта
            contract.status = 'completed'
            contract.save()
            
            contract.project.status = 'completed'
            contract.project.save()
            
            messages.success(request, _('Contract completed successfully. Payment has been sent to the freelancer.'))
            # Перенаправляем на страницу оставления отзыва
            return redirect('jobs:leave_review', pk=contract.pk)
            
        except Exception as e:
            messages.error(request, _(f'Error processing payment: {str(e)}'))
            return redirect('jobs:contract_detail', pk=contract.pk)
    
    context = {
        'contract': contract,
    }
    
    return render(request, 'jobs/contract_complete.html', context)

@login_required
@transaction.atomic
def milestone_complete_view(request, pk):
    """
    Завершение отдельной вехи с переводом средств (для клиента)
    """
    milestone = get_object_or_404(Milestone, pk=pk)
    
    # Проверяем, что пользователь является клиентом контракта
    if milestone.contract.client != request.user:
        return HttpResponseForbidden(_('You do not have permission to complete this milestone'))
    
    # Проверяем, что веха в статусе submitted (отправлена на проверку)
    if milestone.status != 'submitted':
        messages.error(request, _('This milestone cannot be completed because it is not submitted for review'))
        return redirect('jobs:contract_detail', pk=milestone.contract.pk)
    
    if request.method == 'POST':
        try:
            # Получаем кошельки клиента и фрилансера
            from payments.models import Wallet
            from decimal import Decimal
            
            client_wallet = Wallet.objects.get(user=milestone.contract.client)
            freelancer_wallet = Wallet.objects.get(user=milestone.contract.freelancer)
            
            # Проверяем, достаточно ли средств на счету клиента
            if client_wallet.balance < milestone.amount:
                messages.error(request, _('Insufficient funds to complete this milestone. Please top up your wallet.'))
                return redirect('payments:wallet')
            
            # Расчет комиссии сервиса (5%)
            service_fee = milestone.amount * Decimal('0.05')
            freelancer_amount = milestone.amount - service_fee
            
            # Снимаем средства с кошелька клиента
            client_wallet.withdraw(
                milestone.amount,
                description=_(f'Payment for milestone "{milestone.title}" in contract #{milestone.contract.contract_id}'),
                contract=milestone.contract,
                milestone=milestone
            )
            
            # Пополняем кошелек фрилансера (за вычетом комиссии)
            freelancer_wallet.deposit(
                freelancer_amount,
                description=_(f'Payment received for milestone "{milestone.title}" in contract #{milestone.contract.contract_id}'),
                contract=milestone.contract,
                milestone=milestone
            )
            
            # Обновляем статус вехи
            milestone.status = 'approved'
            milestone.save()
            
            # Проверяем, все ли вехи выполнены
            all_milestones_completed = all(
                m.status == 'approved' for m in milestone.contract.milestones.all()
            )
            
            # Если все вехи выполнены, завершаем контракт
            if all_milestones_completed:
                milestone.contract.status = 'completed'
                milestone.contract.save()
                
                # Завершаем проект
                milestone.contract.project.status = 'completed'
                milestone.contract.project.save()
                
                messages.success(request, _('All milestones completed. Contract has been marked as completed.'))
                # Перенаправляем на страницу оставления отзыва
                return redirect('jobs:leave_review', pk=milestone.contract.pk)
            
            messages.success(request, _('Milestone completed successfully. Payment has been sent to the freelancer.'))
            return redirect('jobs:contract_detail', pk=milestone.contract.pk)
            
        except Exception as e:
            messages.error(request, _(f'Error processing payment: {str(e)}'))
            return redirect('jobs:contract_detail', pk=milestone.contract.pk)
    
    context = {
        'milestone': milestone,
    }
    
    return render(request, 'jobs/milestone_complete.html', context)

def about_view(request):
    """View for the About Us page"""
    return render(request, 'jobs/about.html')

def tips_for_freelancers_view(request):
    """View for the Tips for Freelancers page"""
    return render(request, 'jobs/tips_for_freelancers.html')

def category_list_view(request):
    """
    Отображает список всех категорий
    """
    categories = Category.objects.all()
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'jobs/category_list.html', context)

def category_detail_view(request, slug):
    """
    Отображение проектов определенной категории
    """
    category = get_object_or_404(Category, slug=slug)
    projects = Project.objects.filter(category=category, status='open')
    
    context = {
        'category': category,
        'projects': projects,
    }
    
    return render(request, 'jobs/category_detail.html', context)

def freelancer_list_view(request):
    """
    Отображение списка фрилансеров с поиском и фильтрацией
    """
    # Получаем всех пользователей типа freelancer
    freelancers = User.objects.filter(user_type='freelancer')
    
    # Поиск по имени или навыкам
    query = request.GET.get('query')
    if query:
        freelancers = freelancers.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(skills__icontains=query)
        ).distinct()
    
    # Фильтрация по категории
    category_id = request.GET.get('category')
    if category_id:
        try:
            # Находим фрилансеров, у которых в портфолио есть проекты в указанной категории
            freelancers = freelancers.filter(
                portfolio_projects__categories__id=category_id
            ).distinct()
        except (ValueError, TypeError):
            pass
    
    # Фильтрация по рейтингу
    min_rating = request.GET.get('min_rating')
    if min_rating:
        try:
            rating = float(min_rating)
            freelancers = freelancers.filter(
                freelancer_profile__rating__gte=rating
            )
        except (ValueError, TypeError):
            pass
    
    # Фильтрация по доступности
    is_available = request.GET.get('is_available')
    if is_available == 'true':
        freelancers = freelancers.filter(freelancer_profile__is_available=True)
    
    # Получаем список категорий для фильтрации
    categories = Category.objects.all()
    
    context = {
        'freelancers': freelancers,
        'categories': categories,
        'query': query,
        'category_id': category_id,
        'min_rating': min_rating,
        'is_available': is_available,
    }
    
    return render(request, 'jobs/freelancer_list.html', context)

@login_required
def proposal_reject_view(request, pk):
    """
    Отклонение предложения (только для клиента, владельца проекта)
    """
    proposal = get_object_or_404(Proposal, pk=pk)
    
    # Проверяем, что пользователь является владельцем проекта
    if proposal.project.client != request.user:
        return HttpResponseForbidden(_('You do not have permission to reject this proposal'))
    
    # Проверяем, что предложение в статусе ожидания
    if proposal.status != 'pending':
        messages.error(request, _('This proposal is not pending and cannot be rejected'))
        return redirect('jobs:proposal_detail', pk=proposal.pk)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        
        proposal.status = 'rejected'
        proposal.save()
        
        # Отправляем уведомление фрилансеру об отклонении предложения
        send_proposal_rejected_notification(proposal, rejection_reason)
        
        messages.success(request, _('Proposal rejected successfully'))
        return redirect('jobs:project_detail', pk=proposal.project.pk)
    
    context = {
        'proposal': proposal,
    }
    
    return render(request, 'jobs/proposal_confirm_reject.html', context)

@login_required
def project_proposals_view(request, pk):
    """
    Отображение списка предложений для конкретного проекта (только для владельца проекта)
    """
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем, что пользователь является владельцем проекта
    if project.client != request.user:
        return HttpResponseForbidden(_('You do not have permission to view proposals for this project'))
    
    # Получаем предложения для проекта
    proposals = Proposal.objects.filter(project=project)
    
    # Сортировка предложений
    sort = request.GET.get('sort', 'recent')
    if sort == 'recent':
        proposals = proposals.order_by('-created_at')
    elif sort == 'oldest':
        proposals = proposals.order_by('created_at')
    elif sort == 'bid-low':
        proposals = proposals.order_by('bid_amount')
    elif sort == 'bid-high':
        proposals = proposals.order_by('-bid_amount')
    elif sort == 'delivery-short':
        proposals = proposals.order_by('delivery_time')
    
    context = {
        'project': project,
        'proposals': proposals,
        'proposals_count': proposals.count(),
        'sort': sort,
    }
    
    return render(request, 'jobs/project_proposals.html', context)

@login_required
def leave_review_view(request, pk):
    """
    Оставление отзыва о фрилансере после завершения контракта
    """
    contract = get_object_or_404(Contract, pk=pk)
    
    # Проверяем, что пользователь является клиентом контракта
    if contract.client != request.user:
        return HttpResponseForbidden(_('You do not have permission to leave a review'))
    
    # Проверяем, что контракт завершен
    if contract.status != 'completed':
        messages.error(request, _('You can only leave reviews for completed contracts'))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    # Проверяем, что отзыв еще не оставлен
    existing_review = Review.objects.filter(
        project=contract.project,
        client=contract.client,
        freelancer=contract.freelancer
    ).first()
    
    if existing_review:
        messages.error(request, _('You have already left a review for this contract'))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            rating = int(request.POST.get('rating', 0))
            text = request.POST.get('text', '')
            
            if not (1 <= rating <= 5):
                messages.error(request, _('Rating must be between 1 and 5'))
                return redirect('jobs:leave_review', pk=contract.pk)
            
            # Создаем отзыв
            review = Review.objects.create(
                freelancer=contract.freelancer,
                client=request.user,
                project=contract.project,
                rating=rating,
                comment=text
            )
            
            # Обновляем рейтинг фрилансера
            freelancer_profile = contract.freelancer.freelancer_profile
            
            # Получаем все отзывы о фрилансере
            all_reviews = Review.objects.filter(freelancer=contract.freelancer)
            avg_rating = all_reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
            
            freelancer_profile.rating = avg_rating
            freelancer_profile.save()
            
            messages.success(request, _('Thank you for your review!'))
            return redirect('jobs:contract_detail', pk=contract.pk)
            
        except Exception as e:
            messages.error(request, _(f'Error creating review: {str(e)}'))
            return redirect('jobs:leave_review', pk=contract.pk)
    
    # Для GET запроса показываем форму для оставления отзыва
    context = {
        'contract': contract
    }
    
    return render(request, 'jobs/review_form.html', context)

@login_required
def milestone_create_view(request, pk):
    """
    Создание вехи для контракта (только для клиента)
    """
    contract = get_object_or_404(Contract, pk=pk)
    
    # Проверяем, что пользователь является владельцем контракта
    if contract.client != request.user:
        return HttpResponseForbidden(_('You do not have permission to create milestones for this contract'))
    
    # Проверяем, что контракт активен
    if contract.status != 'active':
        messages.error(request, _('You can only add milestones to active contracts'))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.contract = contract
            milestone.save()
            
            messages.success(request, _('Milestone added successfully'))
            return redirect('jobs:contract_detail', pk=contract.pk)
    else:
        # Предварительно заполняем форму с дедлайном контракта
        initial = {
            'due_date': contract.deadline,
        }
        form = MilestoneForm(initial=initial)
    
    context = {
        'form': form,
        'contract': contract,
    }
    
    return render(request, 'jobs/milestone_form.html', context)

# API эндпоинты
def api_project_proposals_count(request, pk):
    """
    API эндпоинт для получения количества предложений по проекту
    """
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем, что пользователь имеет право на просмотр этой информации
    if not request.user.is_authenticated or (request.user != project.client and not project.is_public()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Получаем количество предложений
    proposals_count = Proposal.objects.filter(project=project).count()
    
    return JsonResponse({
        'count': proposals_count,
        'project_id': project.id
    })

@login_required
def recommended_projects_view(request):
    """
    Отображение рекомендованных проектов для фрилансера
    на основе его навыков, истории и активности
    """
    user = request.user
    
    # Проверяем, что пользователь является фрилансером
    if not hasattr(user, 'freelancer_profile'):
        messages.error(request, _('Эта страница доступна только для фрилансеров'))
        return redirect('jobs:home')
    
    try:
        # Получаем рекомендации для пользователя
        recommender = ProjectRecommendation(user)
        recommended_projects = recommender.get_recommendations(limit=20)
        
        # Если нет рекомендаций, отображаем общие популярные проекты
        if not recommended_projects:
            popular_projects = Project.objects.filter(status='open').order_by('-views__count')[:10]
            context = {
                'recommended_projects': [],
                'popular_projects': popular_projects,
                'no_recommendations': True
            }
        else:
            context = {
                'recommended_projects': recommended_projects,
                'no_recommendations': False
            }
            
        return render(request, 'jobs/recommended_projects.html', context)
    
    except Exception as e:
        messages.warning(request, _(f'Произошла ошибка при получении рекомендаций: {str(e)}'))
        # Вместо перенаправления, показываем популярные проекты с информацией об ошибке
        popular_projects = Project.objects.filter(status='open').order_by('-views__count')[:10]
        context = {
            'recommended_projects': [],
            'popular_projects': popular_projects,
            'no_recommendations': True,
            'recommendation_error': True
        }
        return render(request, 'jobs/recommended_projects.html', context)


def record_project_view(request, project_id):
    """
    API-представление для записи просмотра проекта
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        
    try:
        project = get_object_or_404(Project, id=project_id)
        duration = request.GET.get('duration', 0)
        
        try:
            duration = int(duration)
        except ValueError:
            duration = 0
            
        view = ProjectView.record_view(request.user, project, duration)
        
        return JsonResponse({
            'status': 'success', 
            'message': 'View recorded'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=400)


# Применяем декоратор к представлениям, которые используют базовый шаблон
home_view = check_pending_reviews(home_view)
project_list_view = check_pending_reviews(project_list_view)
project_detail_view = check_pending_reviews(project_detail_view)
recommended_projects_view = check_pending_reviews(recommended_projects_view)
contract_detail_view = check_pending_reviews(contract_detail_view)
contract_list_view = check_pending_reviews(contract_list_view)
