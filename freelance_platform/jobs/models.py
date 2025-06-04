from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.utils.translation import get_language
import uuid
from django.db.models import Count, Q, F

class Category(models.Model):
    """
    Project categories
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
        """Returns translated category name based on current language"""
        current_lang = get_language()
        
        if current_lang == 'en':
            return self.name_en if self.name_en else self.name
            
        translated_field = f"name_{current_lang}"
        
        if hasattr(self, translated_field) and getattr(self, translated_field):
            return getattr(self, translated_field)
            
        return self.name_en if self.name_en else self.name

class Tag(models.Model):
    """
    Project tags
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
        """Returns translated tag name"""
        current_lang = get_language()
        
        if current_lang == 'en':
            return self.name_en if self.name_en else self.name
            
        translated_field = f"name_{current_lang}"
        
        if hasattr(self, translated_field) and getattr(self, translated_field):
            return getattr(self, translated_field)
            
        return self.name_en if self.name_en else self.name

class Project(models.Model):
    """
    Project work posted by clients
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
        """Returns CSS class for project status"""
        status_classes = {
            'draft': 'badge-secondary',
            'open': 'badge-success',
            'in_progress': 'badge-primary',
            'completed': 'badge-info',
            'cancelled': 'badge-danger',
        }
        return status_classes.get(self.status, 'badge-secondary')

class Proposal(models.Model):
    """
    Freelancer proposal for a project
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
        """Returns CSS class for proposal status"""
        status_classes = {
            'pending': 'badge-warning',
            'accepted': 'badge-success',
            'rejected': 'badge-danger',
            'withdrawn': 'badge-secondary',
        }
        return status_classes.get(self.status, 'badge-secondary')

class Contract(models.Model):
    """
    Contract model between client and freelancer
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
        # Generate unique ID for contract if it doesn't exist
        if not self.contract_id:
            uid = str(uuid.uuid4()).replace('-', '')[:8]
            self.contract_id = f"CT-{uid}"
        super().save(*args, **kwargs)
    
    @property
    def is_completed(self):
        return self.status == 'completed'
        
    @property
    def review(self):
        """Returns review associated with this contract using project/client/freelancer linkage (no Review.contract FK)"""
        from accounts.models import Review
        try:
            return Review.objects.get(
                project=self.project,
                client=self.client,
                freelancer=self.freelancer,
            )
        except Review.DoesNotExist:
            return None

class Milestone(models.Model):
    """
    Contract milestones
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
        # Checks if milestone has funded escrow payment
        try:
            from payments.models import EscrowPayment
            return EscrowPayment.objects.filter(
                milestone=self,
                status='funded'
            ).exists()
        except ImportError:
            return False


class ProjectView(models.Model):
    """
    Модель для отслеживания просмотров проектов пользователями.
    Используется для аналитики и рекомендаций проектов.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_views'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='views'
    )
    timestamp = models.DateTimeField(_('Timestamp'), auto_now_add=True)
    view_duration = models.PositiveIntegerField(_('View Duration (seconds)'), default=0)
    
    class Meta:
        verbose_name = _('Project View')
        verbose_name_plural = _('Project Views')
        ordering = ['-timestamp']
        # Уникальность по пользователю и проекту
        unique_together = ['user', 'project']
    
    def __str__(self):
        return f"{self.user.username} просмотрел {self.project.title} в {self.timestamp.strftime('%Y-%m-%d')}"

    @classmethod
    def record_view(cls, user, project, duration=None):
        """
        Записывает просмотр проекта пользователем.
        Если просмотр уже существует, обновляет длительность просмотра.
        """
        if not user.is_authenticated or user == project.client:
            return None
            
        view, created = cls.objects.get_or_create(
            user=user,
            project=project,
            defaults={'timestamp': timezone.now()}
        )
        
        if not created and duration:
            view.view_duration += duration
            view.save()
        elif created and duration:
            view.view_duration = duration
            view.save()
            
        return view
