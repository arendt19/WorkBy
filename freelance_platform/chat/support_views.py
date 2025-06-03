"""
Представления для бота поддержки WorkBy
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import get_language
import json

from .support_bot import get_support_response

@csrf_exempt
def bot_response(request):
    """
    API для получения ответа от бота поддержки
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            
            # Получаем текущий язык пользователя
            current_language = get_language()
            
            # Получаем ответ от бота
            response_text = get_support_response(query, language=current_language)
            
            return JsonResponse({
                'success': True,
                'response': response_text
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Only POST method is allowed'
    }, status=405)
