from django.core.management.base import BaseCommand
from chat.tasks import send_pending_email_notifications, clean_old_notifications
from django.utils import timezone

class Command(BaseCommand):
    help = 'Send pending email notifications and clean up old notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up old read notifications',
        )

    def handle(self, *args, **options):
        # Отправка email-уведомлений
        start_time = timezone.now()
        sent_count = send_pending_email_notifications()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent {sent_count} email notifications')
        )
        
        # Если нужно, удаляем старые уведомления
        if options['cleanup']:
            deleted_count = clean_old_notifications()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully cleaned up {deleted_count} old notifications')
            )
        
        # Выводим время выполнения
        execution_time = timezone.now() - start_time
        self.stdout.write(
            self.style.SUCCESS(f'Command executed in {execution_time.total_seconds():.2f} seconds')
        ) 