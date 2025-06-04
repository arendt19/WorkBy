from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse, Http404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_POST, require_GET
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
    
    # Проверяем, что собеседник существует
    # Если пользователь был удален, перенаправляем на список бесед
    if other_participant is None:
        messages.error(request, _("Участник беседы был удален"))
        return redirect('chat:inbox')
    
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
    
    # Удалена логика отображения отладочной информации

    context = {
        'conversation': conversation,
        'conversations_list': conversations_list,
        'other_participant': other_participant,
        'related_project': conversation.related_project,
        'active_conversation_id': conversation.id
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
        return redirect('accounts:freelancer_detail', username=freelancer.username)
    
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

# Удалена дублирующаяся функция api_send_message_view

@login_required
def api_check_messages_view(request, pk):
    """
    API для проверки новых сообщений через AJAX
    
    Поддерживает параметры:
    - since: ID сообщения, начиная с которого нужно загрузить новые
    - limit: максимальное количество сообщений (по умолчанию 50)
    """
    # Настраиваем CORS заголовки для локального окружения
    response = HttpResponse('', content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    
    # Если это preflight запрос, возвращаем пустой ответ с CORS заголовками
    if request.method == 'OPTIONS':
        return response
    
    try:
        # Получаем параметры из запроса
        since_id = request.GET.get('since', None)
        limit = min(int(request.GET.get('limit', 50)), 100)  # Ограничиваем максимум 100 сообщений
        
        conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
        
        # Получаем сообщения разговора с учётом фильтров
        messages_query = Message.objects.filter(conversation=conversation)
        
        # Если указан since_id, получаем только более новые сообщения
        if since_id and since_id.isdigit() and int(since_id) > 0:
            messages_query = messages_query.filter(id__gt=int(since_id))
        
        # Сортируем и ограничиваем количество
        all_messages = messages_query.order_by('created_at')[:limit]
        
        # Форматируем сообщения для фронтенда
        formatted_messages = []
        for msg in all_messages:
            message_data = {
                'id': msg.id,
                'content': msg.content,
                'time': msg.created_at.strftime('%H:%M'),
                'is_mine': msg.sender == request.user,
                'sender_name': msg.sender.get_full_name() or msg.sender.username,
            }
            
            # Добавляем данные о вложениях, если они есть
            if msg.attachment:
                message_data.update({
                    'attachment': True,
                    'attachment_url': msg.attachment.url,
                    'attachment_name': msg.attachment.name.split('/')[-1],
                    'is_image': msg.is_image
                })
            
            formatted_messages.append(message_data)
        
        # Тестовые сообщения удалены
        
        # Отмечаем сообщения как прочитанные (только если не запрошены инкрементальные обновления)
        if not since_id:
            Message.objects.filter(
                conversation=conversation,
                is_read=False
            ).exclude(sender=request.user).update(is_read=True)
        
        # Получаем общее количество сообщений в беседе для пагинации
        total_messages = Message.objects.filter(conversation=conversation).count()
        
        # Подготавливаем данные для ответа
        data = {
            'messages': formatted_messages,
            'status': 'success',
            'message_count': len(formatted_messages),
            'total_count': total_messages,
            'has_more': total_messages > (len(formatted_messages) + (int(since_id) if since_id and since_id.isdigit() else 0)),
            'debug': {
                'time': timezone.now().strftime('%H:%M:%S'),
                'user_id': request.user.id,
                'conversation_id': conversation.id,
                'since_id': since_id,
                'limit': limit
            }
        }
        
        # Устанавливаем содержимое ответа JSON
        response.content = json.dumps(data)
        return response
        
    except Exception as e:
        # В случае ошибки логгируем её и возвращаем запасной ответ
        import logging
        logger = logging.getLogger('chat')
        logger.error(f"Ошибка при загрузке сообщений: {str(e)}", exc_info=True)
        
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
    # Добавляем логирование
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Получен запрос на отметку сообщений как прочитанных. Пользователь: {request.user.username}, ID разговора: {pk}")
    logger.info(f"Method: {request.method}, POST: {request.POST}")
    
    # Разрешаем как GET, так и POST запросы для удобства
    if request.method not in ['POST', 'GET']:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
        logger.info(f"Разговор найден. ID: {conversation.id}")
        
        # Отмечаем все непрочитанные сообщения как прочитанные
        updated = Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        logger.info(f"Обновлено сообщений: {updated}")
        
        return JsonResponse({'success': True, 'updated': updated})
    except Exception as e:
        logger.error(f"Ошибка при отметке сообщений как прочитанных: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# Тестовая функция с декоратором @login_required была удалена

@login_required
def api_send_message_view(request, pk):
    """
    API для отправки сообщения в разговор
    
    Принимает POST-запрос с параметрами:
    - content: текст сообщения
    - attachment: файл вложения (опционально)
    
    Возвращает JSON с результатом операции
    """
    import json
    import traceback
    from django.views.decorators.csrf import ensure_csrf_cookie
    
    # Проверяем, что это POST-запрос
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Только POST-запросы разрешены'}, status=405)
    
    # Добавляем логирование
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Получен запрос на отправку сообщения. Пользователь: {request.user.username}, ID: {pk}")
    logger.info(f"POST данные: {request.POST}")
    logger.info(f"FILES: {request.FILES}")
    
    try:
        # Проверяем, является ли pk ID разговора или ID пользователя
        try:
            # Сначала пробуем найти разговор по ID
            conversation = Conversation.objects.get(pk=pk, participants=request.user)
            logger.info(f"Разговор найден по ID {pk}. Участники: {[p.username for p in conversation.participants.all()]}")
        except Conversation.DoesNotExist:
            # Если разговор не найден, пробуем найти пользователя по ID
            try:
                other_user = User.objects.get(pk=pk)
                logger.info(f"Пользователь найден по ID {pk}. Создаем или получаем разговор.")
                # Создаем или получаем существующий разговор
                conversation = Conversation.get_or_create_conversation(request.user, other_user)
                logger.info(f"Разговор создан или получен. ID: {conversation.id}")
            except User.DoesNotExist:
                logger.error(f"Не найден ни разговор, ни пользователь с ID {pk}")
                return JsonResponse({'success': False, 'error': 'Пользователь или разговор не найден'}, status=404)
        
        logger.info(f"Разговор готов для отправки сообщения. ID: {conversation.id}")
         
        # Получаем данные из запроса
        content = request.POST.get('content', '').strip()
        attachment = request.FILES.get('attachment', None)
        logger.info(f"Полученные данные: content='{content}', attachment={attachment is not None}")
        
        # Проверяем, что есть хотя бы текст или вложение
        if not content and not attachment:
            logger.warning("Попытка отправить пустое сообщение")
            return JsonResponse({'success': False, 'error': 'Сообщение не может быть пустым'}, status=400)
        
        # Создаем новое сообщение
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content,
            attachment=attachment
        )
        logger.info(f"Сообщение создано. ID: {message.id}")
        
        # Формируем данные ответа
        message_data = {
            'id': message.id,
            'content': message.content,
            'time': message.created_at.strftime('%H:%M'),
            'is_mine': True,
            'sender_name': request.user.get_full_name() or request.user.username,
        }
        
        # Добавляем данные о вложении, если оно есть
        if message.attachment:
            message_data.update({
                'attachment': True,
                'attachment_url': message.attachment.url,
                'attachment_name': message.attachment.name.split('/')[-1],
                'is_image': message.is_image
            })
        
        # Создаем уведомления для других участников разговора
        for participant in conversation.participants.all():
            if participant != request.user:
                notification = Notification.objects.create(
                    user=participant,
                    notification_type='message',
                    related_object_id=conversation.id,
                    content=f'{request.user.get_full_name() or request.user.username} отправил вам сообщение'
                )
                logger.info(f"Создано уведомление для {participant.username}. ID: {notification.id}")
        
        response_data = {
            'success': True, 
            'message_data': message_data,
            'message': 'Сообщение успешно отправлено'
        }
        logger.info(f"Отправляем ответ: {json.dumps(response_data)}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def support_chat_view(request):
    """
    Представление для страницы чата с ботом поддержки
    """
    return render(request, 'chat/support_chat.html')

@require_POST
def support_bot_view(request):
    """
    API для обработки сообщений от бота поддержки
    """
    message = request.POST.get('message', '').strip()
    if not message:
        return JsonResponse({'error': 'Message is required'}, status=400)

    # Получаем язык из запроса или используем 'ru' по умолчанию
    lang = request.GET.get('lang', 'ru')
    
    message_lower = message.lower()

    categories = {
        'payment': {
            'keywords': [
                'payment', 'pay', 'card', 'transaction', 'deposit', 'withdraw',
                'оплата', 'платеж', 'карта', 'транзакция', 'депозит', 'вывод',
                'төлем', 'төлеу'
            ],
            'responses': {
                'en': (
                    "It looks like you're experiencing payment issues. Please try the following:\n"
                    "1. Ensure your card is supported and activated.\n"
                    "2. Verify you have sufficient funds or credit.\n"
                    "3. Try a different card or payment provider.\n"
                    "Still stuck? Reach out to our support team and we'll be happy to assist."
                ),
                'ru': (
                    "Похоже, у вас возникли трудности с оплатой. Попробуйте сделать следующее:\n"
                    "1. Убедитесь, что карта поддерживается и активна.\n"
                    "2. Проверьте, достаточно ли средств или доступного лимита.\n"
                    "3. Попробуйте другую карту или способ оплаты.\n"
                    "Если проблема не решена, свяжитесь со службой поддержки — мы поможем."
                ),
                'kk': (
                    "Төлем кезінде қателіктер туындады сияқты. Келесі қадамдарды орындап көріңіз:\n"
                    "1. Картаңыздың қолдау табатынына және белсенді екеніне көз жеткізіңіз.\n"
                    "2. Шотыңызда жеткілікті қаражат бар екенін тексеріңіз.\n"
                    "3. Басқа картаны немесе төлем әдісін қолданып көріңіз.\n"
                    "Мәселе шешілмесе, қолдау қызметіне хабарласыңыз — көмектесуге дайынбыз."
                )
            }
        },
        'registration': {
            'keywords': [
                'register', 'sign up', 'registration', 'create account', 'username', 'password', 'email',
                'регистрация', 'зарегистрироваться', 'аккаунт', 'логин', 'пароль',
                'тіркелу', 'аккаунт жасау'
            ],
            'responses': {
                'en': (
                    "Need help signing up? Make sure to:\n"
                    "• Choose a unique username (3–150 characters).\n"
                    "• Provide a valid email so we can send confirmations.\n"
                    "• Create a strong password (min 8 chars with letters & numbers).\n"
                    "If you already have an account, simply log in from the top-right corner."
                ),
                'ru': (
                    "Помощь с регистрацией:\n"
                    "• Придумайте уникальное имя пользователя (3–150 символов).\n"
                    "• Укажите действующий e-mail для подтверждения.\n"
                    "• Создайте надёжный пароль (не менее 8 символов, буквы и цифры).\n"
                    "Уже есть аккаунт? Используйте кнопку входа в правом верхнем углу."
                ),
                'kk': (
                    "Тіркелуге көмек:\n"
                    "• Бірегей пайдаланушы атын таңдаңыз (3–150 таңба).\n"
                    "• Растау хатын алу үшін жарамды email енгізіңіз.\n"
                    "• Күшті құпия сөз жасаңыз (кемінде 8 таңба, әріптер мен сандар).\n"
                    "Бұрын тіркелген болсаңыз, жоғарғы оң жақтағы кіру батырмасын пайдаланыңыз."
                )
            }
        },
        'withdrawal': {
            'keywords': [
                'withdraw', 'payout', 'cash out', 'escrow release',
                'вывод', 'снятие', 'вывести', 'эскроу',
                'шығару', 'ақша шығару'
            ],
            'responses': {
                'en': "To withdraw funds: Go to Wallet → Withdraw, choose a method (bank card, QIWI, etc.), enter the amount, and confirm. Processing usually takes 1-3 business days.",
                'ru': "Чтобы вывести средства: откройте Кошелёк → Вывод, выберите способ (карта, QIWI и др.), введите сумму и подтвердите. Обработка занимает 1-3 рабочих дня.",
                'kk': "Қаражатты шығару үшін: Әмиян → Шығару бөлімін ашыңыз, әдісті таңдаңыз (карта, QIWI т.б.), соманы енгізіп, растаңыз. Өңдеу 1-3 жұмыс күнін алады."
            }
        },
        'project_post': {
            'keywords': [
                'post project', 'create project', 'new project', 'job posting',
                'разместить проект', 'создать проект', 'проект', 'заказ',
                'жоба жариялау', 'жоба қосу'
            ],
            'responses': {
                'en': "Posting a project is easy: Click ‘Post a Project’, fill in title, description, budget & deadline, then publish. Freelancers will start sending proposals shortly!",
                'ru': "Чтобы разместить проект: нажмите «Опубликовать проект», заполните название, описание, бюджет и дедлайн, затем опубликуйте. Фрилансеры вскоре начнут отправлять предложения!",
                'kk': "Жобаны жариялау үшін: «Жоба жариялау» түймесін басып, атау, сипаттама, бюджет және мерзімді енгізіңіз, содан кейін жариялаңыз. Фрилансерлер ұсыныстарын жіберетін болады!"
            }
        },
        'proposal': {
            'keywords': [
                'proposal', 'bid', 'apply', 'offer',
                'предложение', 'ставка', 'отклик',
                'ұсыныс', 'өтінім'
            ],
            'responses': {
                'en': "To submit a proposal: Open the project page, click ‘Send Proposal’, specify your price, timeline & cover letter, and attach samples if relevant.",
                'ru': "Чтобы отправить предложение: откройте страницу проекта, нажмите «Отправить предложение», укажите цену, сроки и сопроводительное письмо, при необходимости приложите примеры работ.",
                'kk': "Ұсыныс жіберу үшін: Жоба бетіне кіріп, «Ұсыныс жіберу» түймесін басыңыз, бағасын, мерзімін және хабарламаңызды көрсетіңіз, қажет болса мысалдар тіркеңіз."
            }
        },
        'dispute': {
            'keywords': [
                'dispute', 'conflict', 'issue', 'problem with freelancer', 'problem with client',
                'спор', 'конфликт', 'проблема', 'жалоба',
                'дау', 'мәселе'
            ],
            'responses': {
                'en': "We’re sorry to hear about the dispute. Please open the contract page and click ‘Open Dispute’. Provide evidence and our support team will review within 48 h.",
                'ru': "Сожалеем о споре. Перейдите на страницу контракта и нажмите «Открыть спор». Приложите доказательства, и наша команда рассмотрит запрос в течение 48 ч.",
                'kk': "Даудың пайда болғанына өкініш білдіреміз. Контракт бетіне өтіп, «Дау ашу» түймесін басыңыз. Дәлелдер қосыңыз, қолдау тобы 48 сағ ішінде қарайды."
            }
        }
    }

    selected_response = None
    for cat in categories.values():
        if any(k in message_lower for k in cat['keywords']):
            selected_response = cat['responses'].get(lang) or cat['responses']['ru']
            break

    if not selected_response:
        # Ответ по умолчанию
        default_responses = {
            'en': "I'm here to help! How can I assist you today?",
            'ru': "Здравствуйте! Я виртуальный помощник WorkBy. Чем могу вам помочь сегодня?",
            'kk': "Сәлеметсіз бе! Мен WorkBy виртуалды көмекшісімін. Қалай көмектесе аламын?"
        }
        selected_response = default_responses.get(lang, default_responses['ru'])

    response = selected_response
    return JsonResponse({
        'message': response,
        'timestamp': timezone.now().strftime('%H:%M')
    })
