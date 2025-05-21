from .models import Notification
from .utils import send_notification_email
from django.utils import timezone
from datetime import timedelta

def send_pending_email_notifications():
    """
    Отправляет email-уведомления для всех непрочитанных уведомлений,
    по которым еще не было отправлено email.
    """
    # Находим все непрочитанные уведомления без отправленных email
    notifications = Notification.objects.filter(
        is_read=False,
        email_sent=False,
        # Отправляем только те уведомления, которые созданы более 5 минут назад
        # (даем время пользователю прочитать их в реальном времени)
        created_at__lte=timezone.now() - timedelta(minutes=5)
    )
    
    sent_count = 0
    
    for notification in notifications:
        # Проверяем, что у пользователя есть email
        if notification.user.email:
            # Отправляем email
            if send_notification_email(notification):
                sent_count += 1
    
    return sent_count

def clean_old_notifications():
    """
    Удаляет старые прочитанные уведомления для экономии места в базе данных
    """
    # Удаляем прочитанные уведомления старше 3 месяцев
    old_date = timezone.now() - timedelta(days=90)
    result = Notification.objects.filter(
        is_read=True,
        created_at__lt=old_date
    ).delete()
    
    return result[0]  # Возвращаем количество удаленных записей 