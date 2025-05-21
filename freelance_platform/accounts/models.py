from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Расширенная модель пользователя с дополнительными полями
    """
    USER_TYPE_CHOICES = (
        ('client', _('Client')),
        ('freelancer', _('Freelancer')),
    )
    
    LANGUAGE_CHOICES = (
        ('en', _('English')),
        ('ru', _('Russian')),
        ('kk', _('Kazakh')),
    )
    
    user_type = models.CharField(_('User Type'), max_length=10, choices=USER_TYPE_CHOICES, default='client')
    bio = models.TextField(_('Biography'), blank=True)
    avatar = models.ImageField(_('Avatar'), upload_to='avatars/', blank=True, null=True)
    phone_number = models.CharField(_('Phone Number'), max_length=15, blank=True)
    preferred_language = models.CharField(_('Preferred Language'), max_length=2, choices=LANGUAGE_CHOICES, default='en')
    dark_mode = models.BooleanField(_('Dark Mode'), default=False)
    
    # Дополнительные поля для фрилансеров
    skills = models.TextField(_('Skills'), blank=True)
    hourly_rate = models.DecimalField(_('Hourly Rate'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Дополнительные поля для клиентов
    company_name = models.CharField(_('Company Name'), max_length=100, blank=True)
    
    def __str__(self):
        return self.username
    
    def get_initials(self):
        """Возвращает инициалы пользователя (первые буквы имени и фамилии)"""
        initials = ""
        if self.first_name:
            initials += self.first_name[0].upper()
        if self.last_name:
            initials += self.last_name[0].upper()
        if not initials:
            initials = self.username[0].upper()
        return initials
        
    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username
        
    @property
    def is_client(self):
        """Проверка, является ли пользователь клиентом"""
        return self.user_type == 'client'
        
    @property
    def is_freelancer(self):
        """Проверка, является ли пользователь фрилансером"""
        return self.user_type == 'freelancer'

class FreelancerProfile(models.Model):
    """
    Дополнительная информация для профиля фрилансера
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile')
    portfolio_website = models.URLField(_('Portfolio Website'), blank=True)
    rating = models.DecimalField(_('Rating'), max_digits=3, decimal_places=2, default=0)
    is_available = models.BooleanField(_('Available for Hire'), default=True)
    experience_years = models.PositiveIntegerField(_('Years of Experience'), default=0)
    education = models.TextField(_('Education'), blank=True)
    certifications = models.TextField(_('Certifications'), blank=True)
    
    # Дополнительные поля
    resume = models.FileField(_('Resume/CV'), upload_to='resumes/', blank=True, null=True)
    specialization = models.CharField(_('Specialization'), max_length=100, blank=True)
    languages = models.CharField(_('Languages'), max_length=200, blank=True, help_text=_('Languages you speak (comma separated)'))
    
    # Детальные рейтинги
    quality_rating = models.DecimalField(_('Quality Rating'), max_digits=3, decimal_places=2, default=0)
    communication_rating = models.DecimalField(_('Communication Rating'), max_digits=3, decimal_places=2, default=0)
    deadline_rating = models.DecimalField(_('Deadline Adherence Rating'), max_digits=3, decimal_places=2, default=0)
    cost_rating = models.DecimalField(_('Value for Money Rating'), max_digits=3, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.user.username}'s Freelancer Profile"
    
    def update_detailed_ratings(self):
        """
        Обновляет детальные рейтинги фрилансера на основе всех отзывов
        """
        from django.db.models import Avg
        
        # Получаем все отзывы для этого фрилансера
        reviews = Review.objects.filter(freelancer=self.user)
        
        if reviews.exists():
            # Получаем средние значения для каждого типа рейтинга
            review_details = ReviewDetail.objects.filter(review__freelancer=self.user)
            
            if review_details.exists():
                # Обновляем детальные рейтинги
                avg_quality = review_details.aggregate(Avg('quality_rating'))['quality_rating__avg'] or 0
                avg_communication = review_details.aggregate(Avg('communication_rating'))['communication_rating__avg'] or 0
                avg_deadline = review_details.aggregate(Avg('deadline_rating'))['deadline_rating__avg'] or 0
                avg_cost = review_details.aggregate(Avg('cost_rating'))['cost_rating__avg'] or 0
                
                self.quality_rating = avg_quality
                self.communication_rating = avg_communication
                self.deadline_rating = avg_deadline
                self.cost_rating = avg_cost
                
                # Обновляем общий рейтинг как среднее из всех детальных рейтингов
                self.rating = (avg_quality + avg_communication + avg_deadline + avg_cost) / 4
            else:
                # Если нет детальных рейтингов, используем общий рейтинг
                avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
                self.rating = avg_rating
                self.quality_rating = avg_rating
                self.communication_rating = avg_rating
                self.deadline_rating = avg_rating
                self.cost_rating = avg_rating
            
            self.save(update_fields=['rating', 'quality_rating', 'communication_rating', 'deadline_rating', 'cost_rating'])

class ClientProfile(models.Model):
    """
    Дополнительная информация для профиля клиента
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    company_website = models.URLField(_('Company Website'), blank=True)
    industry = models.CharField(_('Industry'), max_length=100, blank=True)
    company_size = models.PositiveIntegerField(_('Company Size (employees)'), null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Client Profile"

class PortfolioProject(models.Model):
    """
    Проект в портфолио фрилансера
    """
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolio_projects')
    title = models.CharField(_('Title'), max_length=100)
    description = models.TextField(_('Description'))
    completed_date = models.DateField(_('Completion Date'), null=True, blank=True)
    client_name = models.CharField(_('Client Name'), max_length=100, blank=True)
    url = models.URLField(_('Project URL'), blank=True)
    
    # Категории проекта
    categories = models.ManyToManyField('jobs.Category', blank=True, related_name='portfolio_projects')
    
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Portfolio Project')
        verbose_name_plural = _('Portfolio Projects')
        ordering = ['-completed_date', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_first_image(self):
        """Возвращает первое изображение проекта для использования в качестве обложки"""
        return self.images.first()

class PortfolioImage(models.Model):
    """
    Изображения для проектов в портфолио
    """
    project = models.ForeignKey(PortfolioProject, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(_('Image'), upload_to='portfolio/')
    caption = models.CharField(_('Caption'), max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=0)
    
    class Meta:
        verbose_name = _('Portfolio Image')
        verbose_name_plural = _('Portfolio Images')
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.project.title}"

class Review(models.Model):
    """
    Отзывы на фрилансеров
    """
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    project = models.ForeignKey('jobs.Project', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.PositiveSmallIntegerField(_('Rating'), choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(_('Comment'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('freelancer', 'client', 'project')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Review for {self.freelancer.username} by {self.client.username}"
    
    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        
        # Обновляем рейтинг фрилансера при добавлении/изменении отзыва
        freelancer_profile = self.freelancer.freelancer_profile
        reviews = Review.objects.filter(freelancer=self.freelancer)
        avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
        if avg_rating:
            freelancer_profile.rating = avg_rating
            freelancer_profile.save(update_fields=['rating'])
            
        # Если это новый отзыв и нет детальных оценок, создаем их
        if is_new and not hasattr(self, 'details'):
            ReviewDetail.objects.create(
                review=self,
                quality_rating=self.rating,
                communication_rating=self.rating,
                deadline_rating=self.rating,
                cost_rating=self.rating
            )
            
        # Обновляем детальные рейтинги фрилансера
        freelancer_profile.update_detailed_ratings()

class ReviewDetail(models.Model):
    """
    Детальные оценки для отзывов по разным критериям
    """
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='details')
    quality_rating = models.PositiveSmallIntegerField(_('Quality Rating'), choices=[(i, i) for i in range(1, 6)])
    communication_rating = models.PositiveSmallIntegerField(_('Communication Rating'), choices=[(i, i) for i in range(1, 6)])
    deadline_rating = models.PositiveSmallIntegerField(_('Deadline Adherence Rating'), choices=[(i, i) for i in range(1, 6)])
    cost_rating = models.PositiveSmallIntegerField(_('Value for Money Rating'), choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Detailed ratings for {self.review}"
    
    @property
    def average_rating(self):
        """Возвращает среднюю оценку по всем критериям"""
        ratings = [self.quality_rating, self.communication_rating, self.deadline_rating, self.cost_rating]
        return sum(ratings) / len(ratings)
