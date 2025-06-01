from django.db import models
from django.db.models import Count, Q, F, Value, ExpressionWrapper, FloatField
from django.db.models.functions import Cast
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

from accounts.models import FreelancerProfile
from jobs.models import Project, Category, Tag, Proposal

User = get_user_model()

class ProjectRecommendation:
    """
    Класс для генерации рекомендаций проектов для фрилансеров.
    Использует гибридный подход, сочетающий рекомендации на основе:
    - Навыков фрилансера
    - Истории выполненных проектов
    - Коллаборативной фильтрации
    - Активности на платформе
    """
    
    def __init__(self, freelancer_user):
        """
        Инициализация с пользователем-фрилансером
        """
        self.user = freelancer_user
        self.freelancer_profile = FreelancerProfile.objects.filter(user=freelancer_user).first()
        
        # Проверка, что пользователь является фрилансером и имеет профиль
        if not self.freelancer_profile:
            raise ValueError("Пользователь не является фрилансером или профиль не найден")
    
    def get_recommendations(self, limit=10):
        """
        Получение рекомендованных проектов для фрилансера
        
        Args:
            limit (int): Максимальное количество рекомендаций
            
        Returns:
            QuerySet: Список рекомендованных проектов с оценкой релевантности
        """
        # Получаем доступные проекты (открытые, не принадлежащие пользователю)
        available_projects = Project.objects.filter(
            status='open'
        ).exclude(
            client=self.user
        ).exclude(
            id__in=Proposal.objects.filter(freelancer=self.user).values_list('project_id', flat=True)
        )
        
        if not available_projects.exists():
            return []
        
        # Получаем оценки по разным методам
        skill_scores = self._calculate_skill_based_scores(available_projects)
        history_scores = self._calculate_history_based_scores(available_projects)
        collab_scores = self._calculate_collaborative_scores(available_projects)
        activity_scores = self._calculate_activity_based_scores(available_projects)
        
        # Объединяем все оценки с весами
        # Настраиваем веса для каждого метода
        weights = {
            'skill': 0.4,
            'history': 0.25,
            'collab': 0.2,
            'activity': 0.15
        }
        
        # Получаем финальные оценки и сортируем проекты
        projects_with_scores = []
        
        for project in available_projects:
            total_score = (
                skill_scores.get(project.id, 0) * weights['skill'] +
                history_scores.get(project.id, 0) * weights['history'] +
                collab_scores.get(project.id, 0) * weights['collab'] +
                activity_scores.get(project.id, 0) * weights['activity']
            )
            
            if total_score > 0:
                projects_with_scores.append({
                    'project': project,
                    'score': total_score,
                    'match_percentage': min(int(total_score * 100), 100)
                })
        
        # Сортируем по убыванию оценки
        sorted_recommendations = sorted(
            projects_with_scores, 
            key=lambda x: x['score'], 
            reverse=True
        )[:limit]
        
        return sorted_recommendations
    
    def _calculate_skill_based_scores(self, projects):
        """
        Расчет оценок на основе совпадения навыков фрилансера с требованиями проектов
        """
        scores = {}
        
        # Получаем навыки фрилансера из текстового поля
        if not hasattr(self.user, 'skills') or not self.user.skills:
            return scores
            
        # Преобразуем строку навыков в множество
        freelancer_skills = set([skill.strip().lower() for skill in self.user.skills.split(',') if skill.strip()])
        
        if not freelancer_skills:
            return scores
            
        # Получаем категории, с которыми работал фрилансер
        freelancer_categories = set(
            Project.objects.filter(
                contract__freelancer=self.user,
                contract__status__in=['completed', 'in_progress']
            ).values_list('category_id', flat=True)
        )
        
        # Получаем теги проектов для сопоставления с навыками
        project_tags = {}
        for project in projects:
            project_tags[project.id] = set([tag.name.lower() for tag in project.tags.all()])
        
        for project in projects:
            score = 0
            
            # Совпадение по тегам проекта и навыкам фрилансера
            project_tag_set = project_tags.get(project.id, set())
            if project_tag_set:
                # Ищем совпадения между навыками фрилансера и тегами проекта
                matching_skills = freelancer_skills.intersection(project_tag_set)
                if matching_skills:
                    skill_match_ratio = len(matching_skills) / len(project_tag_set)
                    score += skill_match_ratio * 0.7  # 70% веса на совпадение навыков и тегов
            
            # Дополнительно проверяем совпадение навыков с описанием проекта
            description_words = set([word.strip().lower() for word in project.description.replace(',', ' ').replace('.', ' ').split() if len(word.strip()) > 3])
            matching_in_description = freelancer_skills.intersection(description_words)
            if matching_in_description:
                desc_match_ratio = len(matching_in_description) / len(freelancer_skills)
                score += desc_match_ratio * 0.3  # 30% веса на совпадение в описании
            
            # Совпадение по категории
            if project.category_id in freelancer_categories:
                score += 0.3  # 30% веса на совпадение категории
            
            scores[project.id] = score
            
        return scores
    
    def _calculate_history_based_scores(self, projects):
        """
        Расчет оценок на основе истории выполненных проектов и предложений
        """
        scores = {}
        
        # Получаем категории и теги успешно выполненных проектов
        completed_contracts = self.user.freelancer_contracts.filter(status='completed')
        
        if not completed_contracts.exists():
            return scores
            
        completed_categories = {}
        completed_tags = {}
        
        for contract in completed_contracts:
            # Подсчитываем частоту категорий
            category_id = contract.project.category_id
            if category_id in completed_categories:
                completed_categories[category_id] += 1
            else:
                completed_categories[category_id] = 1
                
            # Подсчитываем частоту тегов
            for tag in contract.project.tags.all():
                if tag.id in completed_tags:
                    completed_tags[tag.id] += 1
                else:
                    completed_tags[tag.id] = 1
        
        # Нормализуем частоты
        max_category_count = max(completed_categories.values()) if completed_categories else 1
        max_tag_count = max(completed_tags.values()) if completed_tags else 1
        
        for project in projects:
            score = 0
            
            # Совпадение по категории
            category_score = completed_categories.get(project.category_id, 0) / max_category_count if max_category_count > 0 else 0
            score += category_score * 0.6  # 60% веса на категорию
            
            # Совпадение по тегам
            tag_score = 0
            project_tag_ids = project.tags.values_list('id', flat=True)
            
            for tag_id in project_tag_ids:
                tag_score += completed_tags.get(tag_id, 0)
                
            if project_tag_ids and max_tag_count > 0:
                tag_score = tag_score / (len(project_tag_ids) * max_tag_count)
                score += tag_score * 0.4  # 40% веса на теги
            
            scores[project.id] = score
            
        return scores
    
    def _calculate_collaborative_scores(self, projects):
        """
        Расчет оценок на основе коллаборативной фильтрации
        (какие проекты выбирали фрилансеры с похожими навыками)
        """
        scores = {}
        
        # Находим похожих фрилансеров по навыкам
        freelancer_skills = set(self.freelancer_profile.skills.values_list('id', flat=True))
        
        if not freelancer_skills:
            return scores
            
        similar_freelancers = FreelancerProfile.objects.filter(
            skills__in=freelancer_skills
        ).exclude(
            user=self.user
        ).annotate(
            common_skills=Count('skills', filter=Q(skills__in=freelancer_skills))
        ).filter(
            common_skills__gt=0
        ).order_by('-common_skills')[:20]  # Берем топ-20 похожих фрилансеров
        
        if not similar_freelancers.exists():
            return scores
        
        # Получаем проекты, над которыми работали похожие фрилансеры
        similar_user_ids = [profile.user_id for profile in similar_freelancers]
        
        # Подсчитываем, сколько похожих фрилансеров работали над каждым проектом
        project_frequencies = {}
        
        for project in projects:
            # Проверяем, сколько похожих фрилансеров отправляли предложения на этот проект
            proposal_count = Proposal.objects.filter(
                project=project,
                freelancer__in=similar_user_ids
            ).count()
            
            # Проверяем, сколько похожих фрилансеров работали над похожими проектами (той же категории)
            similar_projects_count = Project.objects.filter(
                category=project.category,
                contract__freelancer__in=similar_user_ids,
                contract__status__in=['completed', 'in_progress']
            ).count()
            
            # Рассчитываем итоговую оценку
            if proposal_count > 0 or similar_projects_count > 0:
                score = (0.7 * proposal_count + 0.3 * similar_projects_count) / len(similar_user_ids)
                scores[project.id] = min(score, 1.0)  # Нормализуем до 1.0
            else:
                scores[project.id] = 0
                
        return scores
    
    def _calculate_activity_based_scores(self, projects):
        """
        Расчет оценок на основе активности фрилансера на платформе
        (просмотренные проекты, поисковые запросы)
        """
        scores = {}
        
        # В будущем здесь можно реализовать отслеживание активности пользователя
        # Для простоты пока используем только историю просмотров проектов
        
        # Предположим, у нас есть модель ProjectView для отслеживания просмотров проектов
        try:
            from jobs.models import ProjectView
            
            # Получаем недавно просмотренные проекты
            recent_views = ProjectView.objects.filter(
                user=self.user,
                timestamp__gte=timezone.now() - timedelta(days=30)  # За последние 30 дней
            ).select_related('project')
            
            # Собираем категории и теги просмотренных проектов
            viewed_categories = {}
            viewed_tags = {}
            
            for view in recent_views:
                # Подсчитываем частоту категорий
                category_id = view.project.category_id
                if category_id in viewed_categories:
                    viewed_categories[category_id] += 1
                else:
                    viewed_categories[category_id] = 1
                    
                # Подсчитываем частоту тегов
                for tag in view.project.tags.all():
                    if tag.id in viewed_tags:
                        viewed_tags[tag.id] += 1
                    else:
                        viewed_tags[tag.id] = 1
            
            # Нормализуем частоты
            max_category_count = max(viewed_categories.values()) if viewed_categories else 1
            max_tag_count = max(viewed_tags.values()) if viewed_tags else 1
            
            for project in projects:
                score = 0
                
                # Совпадение по категории
                category_score = viewed_categories.get(project.category_id, 0) / max_category_count if max_category_count > 0 else 0
                score += category_score * 0.7  # 70% веса на категорию
                
                # Совпадение по тегам
                tag_score = 0
                project_tag_ids = project.tags.values_list('id', flat=True)
                
                for tag_id in project_tag_ids:
                    tag_score += viewed_tags.get(tag_id, 0)
                    
                if project_tag_ids and max_tag_count > 0:
                    tag_score = tag_score / (len(project_tag_ids) * max_tag_count)
                    score += tag_score * 0.3  # 30% веса на теги
                
                scores[project.id] = score
                
        except ImportError:
            # Если модель ProjectView не существует, возвращаем пустой словарь
            pass
            
        return scores
