from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.utils.translation import get_language
import uuid

class Category(models.Model):
    """
    Категории проектов
    """
    name = models.CharField(_('Name'), max_length=100)
    name_en = models.CharField(_('Name (English)'), max_length=100, blank=True)
    name_ru = models.CharField(_('Name (Russian)'), max_length=100, blank=True)
    name_kk = models.CharField(_('Name (Kazakh)'), max_length=100, blank=True)
    slug = models.SlugField(_('Slug'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('jobs:category_detail', args=[self.slug])
    
    def get_translated_name(self):
        """
        Возвращает переведенное название категории в зависимости от текущего языка
        """
        current_lang = get_language()
        
        # Получаем имя на указанном языке
        translated_field = f"name_{current_lang}"
        
        # Проверяем, есть ли соответствующее поле и заполнено ли оно
        if hasattr(self, translated_field) and getattr(self, translated_field):
            return getattr(self, translated_field)
        
        # Если перевода нет на текущем языке, проверяем name_en, затем name
        if current_lang != 'en' and self.name_en:
            return self.name_en
            
        # Возвращаем основное name в качестве запасного варианта
        return self.name

class Tag(models.Model):
    """
    Теги для проектов
    """
    name = models.CharField(_('Name'), max_length=50, unique=True)
    name_en = models.CharField(_('Name (English)'), max_length=50, blank=True)
    name_ru = models.CharField(_('Name (Russian)'), max_length=50, blank=True)
    name_kk = models.CharField(_('Name (Kazakh)'), max_length=50, blank=True)
    slug = models.SlugField(_('Slug'), max_length=50, unique=True)
    
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_translated_name(self):
        """
        Возвращает переведенное название тега в зависимости от текущего языка
        """
        current_lang = get_language()
        
        # Получаем имя на указанном языке
        translated_field = f"name_{current_lang}"
        
        # Проверяем, есть ли соответствующее поле и заполнено ли оно
        if hasattr(self, translated_field) and getattr(self, translated_field):
            return getattr(self, translated_field)
        
        # Если перевода нет на текущем языке, проверяем name_en, затем name
        if current_lang != 'en' and self.name_en:
            return self.name_en
            
        # Возвращаем основное name в качестве запасного варианта
        return self.name

class Project(models.Model):
    """
    Проектная работа, размещаемая клиентами
    """
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('open', _('Open')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    BUDGET_TYPE_CHOICES = (
        ('fixed', _('Fixed Price')),
        ('hourly', _('Hourly Rate')),
    )
    
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='client_projects'
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='projects'
    )
    tags = models.ManyToManyField(
        Tag, 
        blank=True, 
        related_name='projects'
    )
    budget_type = models.CharField(
        _('Budget Type'), 
        max_length=10, 
        choices=BUDGET_TYPE_CHOICES
    )
    budget_min = models.DecimalField(
        _('Minimum Budget'), 
        max_digits=10, 
        decimal_places=2
    )
    budget_max = models.DecimalField(
        _('Maximum Budget'), 
        max_digits=10, 
        decimal_places=2
    )
    deadline = models.DateTimeField(_('Deadline'), null=True, blank=True)
    status = models.CharField(
        _('Status'), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    # Регион для которого предназначен проект
    location_required = models.CharField(_('Location Required'), max_length=100, blank=True)
    is_remote = models.BooleanField(_('Remote Job'), default=True)
    
    # Опыт работы
    experience_required = models.CharField(_('Experience Required'), max_length=100, blank=True)
    
    # Видимость проекта
    is_private = models.BooleanField(_('Private Project'), default=False, help_text=_('Private projects are only visible to invited freelancers'))
    
    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('jobs:project_detail', args=[self.pk])
    
    @property
    def is_open(self):
        return self.status == 'open'
    
    @property
    def is_expired(self):
        if self.deadline:
            return self.deadline < timezone.now()
        return False
    
    def get_status_class(self):
        """
        Возвращает CSS-класс для отображения статуса проекта
        """
        status_classes = {
            'draft': 'secondary',
            'open': 'success',
            'in_progress': 'info',
            'completed': 'primary',
            'cancelled': 'danger'
        }
        return status_classes.get(self.status, 'secondary')

class Proposal(models.Model):
    """
    Предложение от фрилансера на проект
    """
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('withdrawn', _('Withdrawn')),
    )
    
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='freelancer_proposals'
    )
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='proposals'
    )
    cover_letter = models.TextField(_('Cover Letter'))
    bid_amount = models.DecimalField(_('Bid Amount'), max_digits=10, decimal_places=2)
    delivery_time = models.PositiveIntegerField(_('Delivery Time (days)'))
    status = models.CharField(
        _('Status'), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Proposal')
        verbose_name_plural = _('Proposals')
        ordering = ['-created_at']
        unique_together = ['freelancer', 'project']
        
    def __str__(self):
        return f"Proposal for {self.project.title} by {self.freelancer.username}"
    
    def get_status_class(self):
        """
        Возвращает CSS-класс для отображения статуса предложения
        """
        status_classes = {
            'pending': 'warning',
            'accepted': 'success',
            'rejected': 'danger',
            'withdrawn': 'secondary'
        }
        return status_classes.get(self.status, 'secondary')

class Contract(models.Model):
    """
    Модель контракта между клиентом и фрилансером
    """
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('paused', _('Paused')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('disputed', _('Disputed')),
    )
    
    contract_id = models.CharField(_('Contract ID'), max_length=20, unique=True, editable=False)
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_contracts'
    )
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='freelancer_contracts'
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contracts')
    proposal = models.OneToOneField(Proposal, on_delete=models.SET_NULL, null=True, related_name='contract')
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)
    deadline = models.DateTimeField(_('Deadline'))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Contract')
        verbose_name_plural = _('Contracts')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.contract_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Генерируем уникальный ID контракта, если его нет
        if not self.contract_id:
            uid = str(uuid.uuid4()).replace('-', '')[:8]
            self.contract_id = f"CT-{uid}"
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def is_completed(self):
        return self.status == 'completed'
        
    @property
    def review(self):
        """
        Возвращает отзыв, связанный с контрактом (если есть)
        """
        from accounts.models import Review
        return Review.objects.filter(
            project=self.project,
            client=self.client,
            freelancer=self.freelancer
        ).first()

class Milestone(models.Model):
    """
    Этапы в контракте
    """
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('submitted', _('Submitted')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    )
    
    contract = models.ForeignKey(
        Contract, 
        on_delete=models.CASCADE, 
        related_name='milestones'
    )
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)
    due_date = models.DateTimeField(_('Due Date'))
    
    status = models.CharField(
        _('Status'), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    payment_status = models.CharField(
        _('Payment Status'),
        max_length=20,
        choices=(
            ('not_paid', _('Not Paid')),
            ('paid', _('Paid')),
            ('escrow', _('In Escrow')),
        ),
        default='not_paid'
    )
    
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        ordering = ['due_date']
        verbose_name = _('Milestone')
        verbose_name_plural = _('Milestones')
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    @property
    def is_escrow_funded(self):
        """Проверяет, имеет ли веха пополненный эскроу-платеж"""
        try:
            return hasattr(self, 'escrow_payment') and self.escrow_payment.status == 'funded'
        except:
            return False
