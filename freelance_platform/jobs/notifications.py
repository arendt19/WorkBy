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

def send_contract_created_notification(contract):
    """
    Отправляет уведомление фрилансеру и клиенту о создании нового контракта
    """
    if not settings.EMAIL_ENABLED:
        return
    
    # Общий контекст для обоих писем
    base_context = {
        'contract_id': contract.contract_id,
        'project_title': contract.project.title,
        'contract_amount': contract.amount,
        'contract_deadline': contract.deadline,
        'contract_url': f"{settings.SITE_URL}/jobs/contracts/{contract.pk}/",
        'client_name': contract.client.get_full_name() or contract.client.username,
        'freelancer_name': contract.freelancer.get_full_name() or contract.freelancer.username,
    }
    
    # Уведомление для фрилансера
    freelancer_context = base_context.copy()
    freelancer_subject = _('New contract #{} has been created for project "{}"').format(
        contract.contract_id, contract.project.title
    )
    freelancer_html = render_to_string('emails/contract_created_freelancer.html', freelancer_context)
    freelancer_text = render_to_string('emails/contract_created_freelancer.txt', freelancer_context)
    
    send_mail(
        freelancer_subject,
        freelancer_text,
        settings.DEFAULT_FROM_EMAIL,
        [contract.freelancer.email],
        html_message=freelancer_html,
        fail_silently=True,
    )
    
    # Уведомление для клиента
    client_context = base_context.copy()
    client_subject = _('Contract #{} has been created for your project "{}"').format(
        contract.contract_id, contract.project.title
    )
    client_html = render_to_string('emails/contract_created_client.html', client_context)
    client_text = render_to_string('emails/contract_created_client.txt', client_context)
    
    send_mail(
        client_subject,
        client_text,
        settings.DEFAULT_FROM_EMAIL,
        [contract.client.email],
        html_message=client_html,
        fail_silently=True,
    ) 