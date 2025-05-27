from .models import Wallet

def wallet_balance(request):
    """
    Добавляет баланс кошелька пользователя в контекст всех шаблонов
    """
    if request.user.is_authenticated:
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return {'user_balance': wallet.balance}
    return {'user_balance': None} 