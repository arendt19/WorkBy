from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
import random
import json

from .models import Conversation, Message, Notification
from .forms import MessageForm

User = get_user_model()

@login_required
def inbox_view(request):
    """
    Показывает список всех разговоров пользователя
    """
    # Получаем все разговоры, в которых участвует текущий пользователь
    conversations = Conversation.objects.filter(
        participants=request.user
    ).prefetch_related('participants').distinct()
    
    # Создаем список разговоров с дополнительной информацией
    conversations_list = []
    for conv in conversations:
        # Получаем и сохраняем собеседника
        other_participant = conv.get_other_participant(request.user)
        
        # Получаем количество непрочитанных сообщений
        unread_count = Message.objects.filter(
            conversation=conv,
            is_read=False
        ).exclude(sender=request.user).count()
        
        # Получаем последнее сообщение
        last_message = Message.objects.filter(
            conversation=conv
        ).order_by('-created_at').first()
        
        # Добавляем информацию в список
        conversations_list.append({
            'conversation': conv,
            'other_participant': other_participant,
            'unread_count': unread_count,
            'last_message': last_message,
            'updated_at': conv.updated_at,
        })
    
    # Сортируем разговоры: сначала с непрочитанными сообщениями, затем по времени последнего обновления
    conversations_list = sorted(
        conversations_list,
        key=lambda x: (not x['unread_count'], -x['updated_at'].timestamp())
    )
    
    context = {
        'conversations': conversations_list,
    }
    
    return render(request, 'chat/inbox.html', context)

@login_required
def conversation_detail_view(request, conversation_id):
    """
    Представление для детальной страницы чата
    """
    # Получаем разговор
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Проверяем, что пользователь является участником беседы
    if not conversation.participants.filter(id=request.user.id).exists():
        return HttpResponseForbidden(_("You don't have permission to view this conversation"))
    
    # Больше не загружаем сообщения здесь, так как они будут загружены через AJAX
    # messages = Message.objects.filter(conversation=conversation).order_by('created_at')
    
    # Получаем всех собеседников
    other_participant = conversation.get_other_participant(request.user)
    
    # Получаем все доступные беседы для бокового меню
    conversations = Conversation.objects.filter(
        participants=request.user
    ).prefetch_related('participants').distinct()
    
    conversations_list = []
    for conv in conversations:
        other_part = conv.get_other_participant(request.user)
        unread_count = Message.objects.filter(
            conversation=conv,
            is_read=False
        ).exclude(sender=request.user).count()
        
        last_message = Message.objects.filter(
            conversation=conv
        ).order_by('-created_at').first()
        
        conversations_list.append({
            'conversation': conv,
            'other_participant': other_part,
            'unread_count': unread_count,
            'last_message': last_message,
            'updated_at': conv.updated_at,
        })
    
    conversations_list = sorted(
        conversations_list,
        key=lambda x: (not x['unread_count'], -x['updated_at'].timestamp())
    )
    
    context = {
        'conversation': conversation,
        'conversations': conversations_list,
        'other_participant': other_participant,
        'related_project': conversation.related_project,
        'active_conversation_id': conversation.id,
    }
    
    return render(request, 'chat/conversation_detail.html', context)

@login_required
def start_conversation_view(request, user_id):
    """
    Начинает новый разговор с пользователем или открывает существующий
    """
    # Получаем пользователя, с которым хотим начать разговор
    other_user = get_object_or_404(User, pk=user_id)
    
    # Нельзя начать разговор с самим собой
    if other_user == request.user:
        return redirect('chat:inbox')
    
    # Получаем или создаем разговор между этими пользователями
    conversation = Conversation.get_or_create_conversation(request.user, other_user)
    
    return redirect('chat:conversation_detail', conversation_id=conversation.pk)

@login_required
def notifications_view(request):
    """
    Отображает все уведомления пользователя
    """
    notifications = Notification.objects.filter(user=request.user)
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'chat/notifications.html', context)

@login_required
def mark_notification_read_view(request, pk):
    """
    Отмечает уведомление как прочитанное и перенаправляет на связанный объект
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    
    # Перенаправляем на связанный объект в зависимости от типа уведомления
    if notification.notification_type == 'message' and notification.related_object_id:
        return redirect('chat:conversation_detail', conversation_id=notification.related_object_id)
    elif notification.notification_type == 'proposal' and notification.related_object_id:
        return redirect('jobs:proposal_detail', pk=notification.related_object_id)
    elif notification.notification_type == 'contract' and notification.related_object_id:
        return redirect('jobs:contract_detail', pk=notification.related_object_id)
    elif notification.notification_type == 'milestone' and notification.related_object_id:
        # Перенаправляем на контракт, содержащий вехи
        from jobs.models import Milestone
        milestone = get_object_or_404(Milestone, pk=notification.related_object_id)
        return redirect('jobs:contract_detail', pk=milestone.contract.pk)
    elif notification.notification_type == 'review' and notification.related_object_id:
        # Перенаправляем на профиль фрилансера
        from accounts.models import User
        freelancer = get_object_or_404(User, pk=notification.related_object_id)
        return redirect('freelancer_detail', username=freelancer.username)
    
    # Если не удалось определить, куда перенаправить
    return redirect('chat:notifications')

@login_required
def api_unread_count_view(request):
    """
    API для получения количества непрочитанных сообщений и уведомлений
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        unread_messages = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
        
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        data = {
            'unread_messages': unread_messages,
            'unread_notifications': unread_notifications,
            'total_unread': unread_messages + unread_notifications,
        }
        
        return JsonResponse(data)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def api_send_message_view(request, pk):
    """
    API для отправки сообщения через AJAX
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
    content = request.POST.get('content', '').strip()
    attachment = request.FILES.get('attachment', None)
    
    if not content and not attachment:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)
    
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content,
        attachment=attachment
    )
    
    # Обновляем время последнего обновления разговора
    conversation.save()  # Это автоматически обновит updated_at
    
    # Создаем уведомление для получателя
    Notification.create_message_notification(message)
    
    # Подготавливаем данные для ответа
    response_data = {
        'id': message.id,
        'content': message.content,
        'created_at': message.created_at.strftime('%H:%M'),
        'is_read': message.is_read
    }
    
    if message.attachment:
        response_data['attachment'] = True
        response_data['attachment_url'] = message.attachment.url
        response_data['attachment_name'] = message.attachment.name.split('/')[-1]
        response_data['is_image'] = message.is_image
    
    return JsonResponse(response_data)

@login_required
def api_check_messages_view(request, pk):
    """
    API для проверки новых сообщений через AJAX
    """
    # Добавляем CORS заголовки для локального окружения
    response = HttpResponse('', content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    
    # Если это preflight запрос, возвращаем пустой ответ с CORS заголовками
    if request.method == 'OPTIONS':
        return response
    
    try:
        conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
        
        # Получаем все сообщения разговора
        all_messages = Message.objects.filter(
            conversation=conversation
        ).order_by('created_at')
        
        # Форматируем сообщения для фронтенда
        formatted_messages = []
        for msg in all_messages:
            formatted_messages.append({
                'id': msg.id,
                'content': msg.content,
                'time': msg.created_at.strftime('%H:%M'),
                'is_mine': msg.sender == request.user,
                'sender_name': msg.sender.get_full_name() or msg.sender.username,
            })
        
        # Если нет реальных сообщений, добавим тестовое сообщение
        if not formatted_messages:
            formatted_messages = [
                {
                    'id': 999001,
                    'content': 'Это автоматическое тестовое сообщение, чтобы проверить отображение чата',
                    'time': timezone.now().strftime('%H:%M'),
                    'is_mine': False,
                    'sender_name': 'Система',
                },
                {
                    'id': 999002,
                    'content': 'Когда вы отправите сообщение, оно появится здесь',
                    'time': timezone.now().strftime('%H:%M'),
                    'is_mine': True,
                    'sender_name': request.user.get_full_name() or request.user.username,
                }
            ]
        
        # Отмечаем сообщения как прочитанные
        Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        
        # Возвращаем ответ
        data = {
            'messages': formatted_messages,
            'status': 'success',
            'message_count': len(formatted_messages),
            'debug': {
                'time': timezone.now().strftime('%H:%M:%S'),
                'user_id': request.user.id,
                'conversation_id': conversation.id
            }
        }
        
        # Устанавливаем содержимое ответа JSON
        response.content = json.dumps(data)
        return response
        
    except Exception as e:
        # В случае ошибки логгируем её и возвращаем запасной ответ
        print(f"Ошибка при загрузке сообщений: {str(e)}")
        
        # Возвращаем запасной ответ
        emergency_data = {
            'messages': [
                {
                    'id': 999999,
                    'content': f'Ошибка при загрузке сообщений: {str(e)}. Пожалуйста, обновите страницу.',
                    'time': timezone.now().strftime('%H:%M'),
                    'is_mine': False,
                    'sender_name': 'Система',
                }
            ],
            'status': 'error',
            'message_count': 1,
            'error': str(e)
        }
        
        response.content = json.dumps(emergency_data)
        return response

@login_required
def api_mark_messages_read_view(request, pk):
    """
    API для отметки сообщений как прочитанных через AJAX
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
    
    # Отмечаем все непрочитанные сообщения как прочитанные
    Message.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)
    
    return JsonResponse({'success': True})

@login_required
def api_add_test_message(request, pk):
    """
    Временная заглушка для устранения ошибки.
    Эта функция будет удалена после перезапуска сервера.
    """
    return JsonResponse({'status': 'disabled', 'message': 'This functionality has been disabled'}, status=404)
