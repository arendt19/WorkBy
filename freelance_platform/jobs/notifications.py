from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

def send_proposal_submitted_notification(proposal):
    """
    Отправляет уведомление клиенту о новом предложении на его проект
    """
    if not settings.EMAIL_ENABLED:
        return
    
    context = {
        'client_name': proposal.project.client.get_full_name() or proposal.project.client.username,
        'freelancer_name': proposal.freelancer.get_full_name() or proposal.freelancer.username,
        'project_title': proposal.project.title,
        'project_url': f"{settings.SITE_URL}/jobs/projects/{proposal.project.pk}/",
        'proposals_url': f"{settings.SITE_URL}/jobs/projects/{proposal.project.pk}/proposals/",
        'bid_amount': proposal.bid_amount,
        'delivery_time': proposal.delivery_time,
    }
    
    subject = _('New proposal for your project "{}"').format(proposal.project.title)
    html_message = render_to_string('emails/new_proposal_notification.html', context)
    plain_message = render_to_string('emails/new_proposal_notification.txt', context)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [proposal.project.client.email],
        html_message=html_message,
        fail_silently=True,
    )

def send_proposal_accepted_notification(proposal):
    """
    Отправляет уведомление фрилансеру о принятии его предложения
    """
    if not settings.EMAIL_ENABLED:
        return
    
    context = {
        'freelancer_name': proposal.freelancer.get_full_name() or proposal.freelancer.username,
        'client_name': proposal.project.client.get_full_name() or proposal.project.client.username,
        'project_title': proposal.project.title,
        'project_url': f"{settings.SITE_URL}/jobs/projects/{proposal.project.pk}/",
        'proposal_url': f"{settings.SITE_URL}/jobs/proposal/{proposal.pk}/",
    }
    
    subject = _('Your proposal for project "{}" has been accepted').format(proposal.project.title)
    html_message = render_to_string('emails/proposal_accepted_notification.html', context)
    plain_message = render_to_string('emails/proposal_accepted_notification.txt', context)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [proposal.freelancer.email],
        html_message=html_message,
        fail_silently=True,
    )

def send_proposal_rejected_notification(proposal, rejection_reason=None):
    """
    Отправляет уведомление фрилансеру об отклонении его предложения
    """
    if not settings.EMAIL_ENABLED:
        return
    
    context = {
        'freelancer_name': proposal.freelancer.get_full_name() or proposal.freelancer.username,
        'client_name': proposal.project.client.get_full_name() or proposal.project.client.username,
        'project_title': proposal.project.title,
        'project_url': f"{settings.SITE_URL}/jobs/projects/{proposal.project.pk}/",
        'rejection_reason': rejection_reason,
    }
    
    subject = _('Your proposal for project "{}" was not accepted').format(proposal.project.title)
    html_message = render_to_string('emails/proposal_rejected_notification.html', context)
    plain_message = render_to_string('emails/proposal_rejected_notification.txt', context)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [proposal.freelancer.email],
        html_message=html_message,
        fail_silently=True,
    ) 