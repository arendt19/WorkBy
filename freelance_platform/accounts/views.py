from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.db.models import Avg
from .forms import (
    UserProfileForm, FreelancerProfileForm, FreelancerUserForm,
    ClientProfileForm, ClientUserForm, ReviewForm, PortfolioProjectForm, PortfolioImageFormSet,
    UserRegistrationForm, UserUpdateForm
)
from .models import User, FreelancerProfile, ClientProfile, Review, PortfolioProject, PortfolioImage
from jobs.models import Contract, Project, Category

def register_view(request):
    """
    Регистрация нового пользователя
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, _('Your account has been created! You can now log in.'))
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    """
    Просмотр профиля пользователя
    """
    user = request.user
    
    if user.user_type == 'freelancer':
        profile, created = FreelancerProfile.objects.get_or_create(user=user)
        portfolio_projects = PortfolioProject.objects.filter(freelancer=user)
        reviews = Review.objects.filter(freelancer=user)
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        context = {
            'user': user,
            'profile': profile,
            'portfolio_projects': portfolio_projects,
            'reviews': reviews,
            'avg_rating': avg_rating
        }
        return render(request, 'accounts/freelancer_profile.html', context)
    
    elif user.user_type == 'client':
        profile, created = ClientProfile.objects.get_or_create(user=user)
        context = {
            'user': user,
            'profile': profile
        }
        return render(request, 'accounts/client_profile.html', context)
    
    # Если тип пользователя не определен или это админ
    return render(request, 'accounts/profile.html', {'user': user})

@login_required
def profile_edit_view(request):
    """
    Редактирование профиля пользователя
    """
    user = request.user
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        
        if user.user_type == 'freelancer':
            profile, created = FreelancerProfile.objects.get_or_create(user=user)
            profile_form = FreelancerProfileForm(request.POST, instance=profile)
            freelancer_form = FreelancerUserForm(request.POST, instance=user)
            valid_forms = user_form.is_valid() and profile_form.is_valid() and freelancer_form.is_valid()
        else:
            profile, created = ClientProfile.objects.get_or_create(user=user)
            profile_form = ClientProfileForm(request.POST, instance=profile)
            client_form = ClientUserForm(request.POST, instance=user)
            valid_forms = user_form.is_valid() and profile_form.is_valid() and client_form.is_valid()
        
        if valid_forms:
            user_form.save()
            profile_form.save()
            
            if user.user_type == 'freelancer':
                freelancer_form.save()
            else:
                client_form.save()
                
            messages.success(request, _('Your profile has been updated!'))
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        
        if user.user_type == 'freelancer':
            profile, created = FreelancerProfile.objects.get_or_create(user=user)
            profile_form = FreelancerProfileForm(instance=profile)
            freelancer_form = FreelancerUserForm(instance=user)
        else:
            profile, created = ClientProfile.objects.get_or_create(user=user)
            profile_form = ClientProfileForm(instance=profile)
            client_form = ClientUserForm(instance=user)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    if user.user_type == 'freelancer':
        context['freelancer_form'] = freelancer_form
    else:
        context['client_form'] = client_form
    
    return render(request, 'accounts/profile_edit.html', context)

def freelancer_detail_view(request, username):
    """
    Просмотр профиля фрилансера другими пользователями
    """
    freelancer = get_object_or_404(User, username=username, user_type='freelancer')
    profile = get_object_or_404(FreelancerProfile, user=freelancer)
    portfolio_projects = PortfolioProject.objects.filter(freelancer=freelancer)
    reviews = Review.objects.filter(freelancer=freelancer)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Убедимся, что avg_rating - это число, а не None
    if avg_rating is None:
        avg_rating = 0
    
    # Собираем статистику для фрилансера
    completed_contracts = Contract.objects.filter(freelancer=freelancer, status='completed')
    total_contracts = Contract.objects.filter(freelancer=freelancer).exclude(status='cancelled')
    
    stats = {
        'completed_projects': completed_contracts.count(),
        'success_rate': int(completed_contracts.count() / max(total_contracts.count(), 1) * 100),
        'on_time': 95,  # Заглушка, в реальном проекте нужно рассчитывать
        'on_budget': 90,  # Заглушка, в реальном проекте нужно рассчитывать
    }
    
    context = {
        'freelancer': freelancer,
        'profile': profile,
        'portfolio_projects': portfolio_projects,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'stats': stats
    }
    
    return render(request, 'accounts/freelancer_detail.html', context)

def client_detail_view(request, username):
    """
    Просмотр профиля клиента другими пользователями
    """
    client = get_object_or_404(User, username=username, user_type='client')
    profile = ClientProfile.objects.get(user=client)
    
    # Получаем публичные проекты клиента
    recent_projects = Project.objects.filter(client=client, is_private=False).order_by('-created_at')[:5]
    
    context = {
        'client': client,
        'profile': profile,
        'recent_projects': recent_projects,
    }
    
    return render(request, 'accounts/client_detail.html', context)

@login_required
def change_language_view(request, language_code):
    """
    Изменение предпочитаемого языка для пользователя
    """
    user = request.user
    
    # Проверка, что язык входит в список доступных
    if language_code in dict(User.LANGUAGE_CHOICES):
        user.preferred_language = language_code
        user.save()
    
    # Возвращаемся на страницу, с которой был сделан запрос
    next_url = request.GET.get('next', reverse('accounts:profile'))
    return redirect(next_url)

@login_required
def create_review_view(request, freelancer_id, contract_id):
    """
    Создание отзыва о фрилансере
    """
    # Проверяем, что пользователь является клиентом
    if request.user.user_type != 'client':
        messages.error(request, _('Only clients can leave reviews'))
        return redirect('home')
    
    freelancer = get_object_or_404(User, pk=freelancer_id, user_type='freelancer')
    contract = get_object_or_404(Contract, pk=contract_id, client=request.user, freelancer=freelancer, status='completed')
    
    # Проверяем, есть ли уже отзыв для этого контракта
    existing_review = Review.objects.filter(
        client=request.user, 
        freelancer=freelancer,
        project=contract.project
    ).first()
    
    if existing_review:
        messages.error(request, _('You have already reviewed this freelancer for this project'))
        return redirect('accounts:freelancer_detail', username=freelancer.username)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Сохраняем основной отзыв
                review = form.save(commit=False)
                review.client = request.user
                review.freelancer = freelancer
                review.project = contract.project
                review.save()
                
                # Сохраняем детальные оценки
                quality_rating = request.POST.get('quality_rating')
                communication_rating = request.POST.get('communication_rating')
                deadline_rating = request.POST.get('deadline_rating')
                cost_rating = request.POST.get('cost_rating')
                
                # Создаем объект детальных оценок
                from .models import ReviewDetail
                ReviewDetail.objects.create(
                    review=review,
                    quality_rating=quality_rating,
                    communication_rating=communication_rating,
                    deadline_rating=deadline_rating,
                    cost_rating=cost_rating
                )
                
                # Обновляем детальные рейтинги в профиле фрилансера
                freelancer_profile = freelancer.freelancer_profile
                freelancer_profile.update_detailed_ratings()
            
            messages.success(request, _('Thank you for your review!'))
            return redirect('accounts:freelancer_detail', username=freelancer.username)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'freelancer': freelancer,
        'contract': contract,
    }
    
    return render(request, 'accounts/create_review.html', context)

@login_required
def edit_review_view(request, review_id):
    """
    Редактирование отзыва
    """
    review = get_object_or_404(Review, pk=review_id, client=request.user)
    
    # Получаем или создаем детальные оценки
    try:
        review_detail = review.details
    except:
        from .models import ReviewDetail
        review_detail = ReviewDetail.objects.create(
            review=review,
            quality_rating=review.rating,
            communication_rating=review.rating,
            deadline_rating=review.rating,
            cost_rating=review.rating
        )
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            with transaction.atomic():
                # Сохраняем основной отзыв
                form.save()
                
                # Обновляем детальные оценки
                review_detail.quality_rating = request.POST.get('quality_rating')
                review_detail.communication_rating = request.POST.get('communication_rating')
                review_detail.deadline_rating = request.POST.get('deadline_rating')
                review_detail.cost_rating = request.POST.get('cost_rating')
                review_detail.save()
                
                # Обновляем детальные рейтинги в профиле фрилансера
                freelancer_profile = review.freelancer.freelancer_profile
                freelancer_profile.update_detailed_ratings()
            
            messages.success(request, _('Review updated successfully'))
            return redirect('accounts:freelancer_detail', username=review.freelancer.username)
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
        'review_detail': review_detail,
        'freelancer': review.freelancer,
    }
    
    return render(request, 'accounts/edit_review.html', context)

@login_required
def delete_review_view(request, review_id):
    """
    Удаление отзыва
    """
    review = get_object_or_404(Review, pk=review_id, client=request.user)
    freelancer = review.freelancer
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, _('Review deleted successfully'))
        return redirect('accounts:freelancer_detail', username=freelancer.username)
    
    context = {
        'review': review,
        'freelancer': freelancer,
    }
    
    return render(request, 'accounts/delete_review.html', context)

@login_required
def portfolio_project_list_view(request):
    """
    Список проектов в портфолио фрилансера
    """
    # Проверяем, что пользователь является фрилансером
    if request.user.user_type != 'freelancer':
        messages.error(request, _('Only freelancers can manage portfolio'))
        return redirect('profile')
    
    projects = PortfolioProject.objects.filter(freelancer=request.user)
    
    context = {
        'projects': projects,
    }
    
    return render(request, 'accounts/portfolio_list.html', context)

@login_required
def portfolio_project_create_view(request):
    """
    Создание нового проекта в портфолио
    """
    # Проверяем, что пользователь является фрилансером
    if request.user.user_type != 'freelancer':
        messages.error(request, _('Only freelancers can manage portfolio'))
        return redirect('profile')
    
    if request.method == 'POST':
        form = PortfolioProjectForm(request.POST)
        formset = PortfolioImageFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # Сохраняем проект
                project = form.save(commit=False)
                project.freelancer = request.user
                project.save()
                form.save_m2m()  # Сохраняем связанные категории
                
                # Сохраняем изображения
                formset.instance = project
                formset.save()
            
            messages.success(request, _('Portfolio project created successfully'))
            return redirect('portfolio_detail', pk=project.pk)
    else:
        form = PortfolioProjectForm()
        formset = PortfolioImageFormSet()
        
        # Получаем все доступные категории для выбора
        form.fields['categories'].queryset = Category.objects.all()
    
    context = {
        'form': form,
        'formset': formset,
        'is_creating': True,
    }
    
    return render(request, 'accounts/portfolio_form.html', context)

@login_required
def portfolio_project_edit_view(request, pk):
    """
    Редактирование проекта в портфолио
    """
    project = get_object_or_404(PortfolioProject, pk=pk, freelancer=request.user)
    
    if request.method == 'POST':
        form = PortfolioProjectForm(request.POST, instance=project)
        formset = PortfolioImageFormSet(request.POST, request.FILES, instance=project)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            
            messages.success(request, _('Portfolio project updated successfully'))
            return redirect('portfolio_detail', pk=project.pk)
    else:
        form = PortfolioProjectForm(instance=project)
        formset = PortfolioImageFormSet(instance=project)
        
        # Получаем все доступные категории для выбора
        form.fields['categories'].queryset = Category.objects.all()
    
    context = {
        'form': form,
        'formset': formset,
        'project': project,
        'is_creating': False,
    }
    
    return render(request, 'accounts/portfolio_form.html', context)

@login_required
def portfolio_project_delete_view(request, pk):
    """
    Удаление проекта из портфолио
    """
    project = get_object_or_404(PortfolioProject, pk=pk, freelancer=request.user)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, _('Portfolio project deleted successfully'))
        return redirect('portfolio_list')
    
    context = {
        'project': project,
    }
    
    return render(request, 'accounts/portfolio_delete.html', context)

def portfolio_project_detail_view(request, pk):
    """
    Детальный просмотр проекта из портфолио
    """
    project = get_object_or_404(PortfolioProject, pk=pk)
    images = project.images.all()
    
    context = {
        'project': project,
        'images': images,
        'can_edit': request.user == project.freelancer,
    }
    
    return render(request, 'accounts/portfolio_detail.html', context)

def logout_view(request):
    """
    Пользовательское представление для выхода из системы.
    Поддерживает как GET, так и POST запросы.
    """
    if request.method == 'POST':
        logout(request)
        messages.success(request, _('You have been successfully logged out.'))
        return redirect('jobs:home')
    else:
        # Для GET-запросов отображаем страницу подтверждения выхода
        return render(request, 'accounts/logout.html')
