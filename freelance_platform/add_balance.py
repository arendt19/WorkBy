import os
import sys
import django

# Настраиваем Django для работы с проектом
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "freelance_core.settings")
django.setup()

from django.contrib.auth import get_user_model
from payments.models import Wallet, Transaction
from decimal import Decimal

def add_balance_to_user(username, amount):
    """
    Начисляет указанную сумму на баланс пользователя
    """
    User = get_user_model()
    
    try:
        # Находим пользователя
        user = User.objects.get(username=username)
        print(f"Пользователь {username} найден")
        
        # Проверяем существование кошелька, если нет - создаем
        wallet, created = Wallet.objects.get_or_create(user=user)
        if created:
            print(f"Кошелек для пользователя {username} создан")
        
        # Преобразуем сумму в Decimal
        amount_decimal = Decimal(str(amount))
        
        # Пополняем кошелек
        transaction = wallet.deposit(
            amount=amount_decimal,
            description=f"Пополнение баланса на сумму {amount_decimal}"
        )
        
        print(f"Баланс пользователя {username} успешно пополнен на {amount_decimal}")
        print(f"Новый баланс: {wallet.balance}")
        print(f"ID транзакции: {transaction.transaction_id}")
        
        return transaction
        
    except User.DoesNotExist:
        print(f"Ошибка: Пользователь {username} не найден")
        return None
    except Exception as e:
        print(f"Ошибка при пополнении баланса: {str(e)}")
        return None

if __name__ == "__main__":
    # Проверяем аргументы командной строки или используем значения по умолчанию
    if len(sys.argv) > 2:
        username = sys.argv[1]
        amount = sys.argv[2]
    else:
        username = "testing123"  # Имя пользователя по умолчанию
        amount = 10000           # Сумма по умолчанию
    
    add_balance_to_user(username, amount)
