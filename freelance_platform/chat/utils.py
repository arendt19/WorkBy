from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string

def send_notification_email(notification):
    """
    Отправляет email-уведомление пользователю в зависимости от типа уведомления
    """
    if notification.email_sent:
        return False  # Email уже был отправлен
    
    # Получаем пользователя
    user = notification.user
    
    # Базовый контекст для шаблона
    context = {
        'user': user,
        'notification': notification,
        'site_name': 'FreelanceKZ',
        'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
    }
    
    # Выбираем шаблон и тему письма в зависимости от типа уведомления
    template_name = None
    subject = None
    
    if notification.notification_type == 'message':
        template_name = 'email/message_notification.html'
        subject = _('New Message on FreelanceKZ')
        
        # Добавляем ссылку на беседу
        context['action_url'] = context['site_url'] + reverse('chat:conversation_detail', args=[notification.related_object_id])
        context['action_text'] = _('View Message')
    
    elif notification.notification_type == 'proposal':
        template_name = 'email/proposal_notification.html'
        subject = _('New Proposal for Your Project')
        
        # Добавляем ссылку на предложение
        context['action_url'] = context['site_url'] + reverse('jobs:proposal_detail', args=[notification.related_object_id])
        context['action_text'] = _('View Proposal')
    
    elif notification.notification_type == 'contract':
        template_name = 'email/contract_notification.html'
        subject = _('Contract Update on FreelanceKZ')
        
        # Добавляем ссылку на контракт
        context['action_url'] = context['site_url'] + reverse('jobs:contract_detail', args=[notification.related_object_id])
        context['action_text'] = _('View Contract')
    
    elif notification.notification_type == 'milestone':
        template_name = 'email/milestone_notification.html'
        subject = _('Milestone Update on FreelanceKZ')
        
        # В этом случае related_object_id указывает на milestone
        from jobs.models import Milestone
        try:
            milestone = Milestone.objects.get(pk=notification.related_object_id)
            context['milestone'] = milestone
            context['action_url'] = context['site_url'] + reverse('jobs:contract_detail', args=[milestone.contract.pk])
            context['action_text'] = _('View Contract Details')
        except Milestone.DoesNotExist:
            pass
    
    elif notification.notification_type == 'review':
        template_name = 'email/review_notification.html'
        subject = _('New Review on FreelanceKZ')
        
        # В этом случае related_object_id указывает на пользователя-фрилансера
        context['action_url'] = context['site_url'] + reverse('freelancer_detail', args=[notification.related_object_id])
        context['action_text'] = _('View Review')
    
    # Если не удалось определить тип уведомления, не отправляем email
    if not template_name or not subject:
        return False
    
    # Формируем HTML-контент письма
    html_message = render_to_string(template_name, context)
    
    # Отправляем письмо
    try:
        send_mail(
            subject=subject,
            message=notification.content,  # Текстовая версия
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        # Отмечаем, что email был отправлен
        notification.email_sent = True
        notification.save(update_fields=['email_sent'])
        
        return True
    except Exception as e:
        # В случае ошибки возвращаем False
        print(f"Error sending email: {e}")
        return False 