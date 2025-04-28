from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class Conversation(models.Model):
    """
    Модель для разговора между двумя пользователями
    """
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations',
        verbose_name=_('Participants')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Conversation')
        verbose_name_plural = _('Conversations')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.id}"
    
    def get_absolute_url(self):
        return reverse('chat:conversation_detail', args=[self.pk])
    
    @property
    def last_message(self):
        """Возвращает последнее сообщение в разговоре"""
        return self.messages.order_by('-created_at').first()
    
    def get_other_participant(self, user=None):
        """
        Возвращает другого участника разговора (не текущего пользователя)
        Если пользователь не указан, возвращает первого участника, который не является текущим пользователем
        """
        if user is None:
            # Если пользователь не указан, вернем первого участника
            return self.participants.first()
        
        # Иначе возвращаем первого участника, который не является указанным пользователем
        return self.participants.exclude(id=user.id).first()
    
    def get_unread_count(self, user=None):
        """
        Возвращает количество непрочитанных сообщений для указанного пользователя
        """
        if user is None:
            return 0
        
        return self.messages.filter(is_read=False).exclude(sender=user).count()
    
    def add_participant(self, user):
        """Добавляет участника в разговор"""
        if user not in self.participants.all():
            self.participants.add(user)
    
    def remove_participant(self, user):
        """Удаляет участника из разговора"""
        if user in self.participants.all():
            self.participants.remove(user)
    
    @classmethod
    def get_or_create_conversation(cls, user1, user2):
        """
        Получает или создает разговор между двумя пользователями
        """
        # Поиск существующего разговора между пользователями
        conversations = Conversation.objects.filter(participants=user1).filter(participants=user2)
        
        if conversations.exists():
            return conversations.first()
        
        # Создание нового разговора
        conversation = Conversation.objects.create()
        conversation.participants.add(user1, user2)
        return conversation

class Message(models.Model):
    """
    Модель для сообщения в разговоре
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Conversation')
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('Sender')
    )
    content = models.TextField(_('Content'))
    attachment = models.FileField(_('Attachment'), upload_to='chat_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    is_read = models.BooleanField(_('Read'), default=False)
    
    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message {self.id}"
    
    def mark_as_read(self):
        """Отмечает сообщение как прочитанное"""
        if not self.is_read:
            self.is_read = True
            self.save()
            
    @property
    def is_image(self):
        """Проверяет, является ли прикрепленный файл изображением"""
        if not self.attachment:
            return False
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        file_ext = self.attachment.name.lower().split('.')[-1]
        return f'.{file_ext}' in image_extensions

class Notification(models.Model):
    """
    Модель для уведомлений пользователя о новых сообщениях
    """
    TYPE_CHOICES = (
        ('message', _('New Message')),
        ('proposal', _('New Proposal')),
        ('contract', _('Contract Update')),
        ('milestone', _('Milestone Update')),
        ('review', _('New Review')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('User')
    )
    notification_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    content = models.TextField(_('Content'))
    related_object_id = models.PositiveIntegerField(_('Related Object ID'), null=True, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    is_read = models.BooleanField(_('Read'), default=False)
    email_sent = models.BooleanField(_('Email Notification Sent'), default=False)
    
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user.username}"
    
    def mark_as_read(self):
        """Отмечает уведомление как прочитанное"""
        if not self.is_read:
            self.is_read = True
            self.save()

    @classmethod
    def create_message_notification(cls, message):
        """
        Создает уведомление о новом сообщении
        """
        # Получаем получателя (не отправителя сообщения)
        for participant in message.conversation.participants.all():
            if participant != message.sender:
                Notification.objects.create(
                    user=participant,
                    notification_type='message',
                    content=f"Новое сообщение от {message.sender.username}",
                    related_object_id=message.conversation.id
                )
