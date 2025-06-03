from django.shortcuts import render

def test_button_view(request):
    """
    Тестовая страница для проверки кнопки поддержки
    """
    return render(request, 'test_button.html')
