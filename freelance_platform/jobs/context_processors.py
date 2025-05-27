from django.db import models
from .models import Contract

def contracts_processor(request):
    """
    Контекстный процессор для проверки наличия контрактов у пользователя
    и добавления соответствующей переменной в контекст шаблона
    """
    context = {
        'has_contracts': False,
    }
    
    # Проверяем, авторизован ли пользователь
    if request.user.is_authenticated:
        # Проверяем наличие контрактов, в которых пользователь является клиентом или фрилансером
        contracts_exist = Contract.objects.filter(
            models.Q(client=request.user) | models.Q(freelancer=request.user)
        ).exists()
        
        context['has_contracts'] = contracts_exist
    
    return context
