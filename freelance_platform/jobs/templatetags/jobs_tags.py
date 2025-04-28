from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """
    Разделяет строку по указанному разделителю и возвращает список
    """
    if not value:
        return []
    return value.split(delimiter)

@register.filter
def strip(value):
    """
    Удаляет пробелы в начале и конце строки
    """
    if not value:
        return ''
    return value.strip()

@register.filter
def get_item(dictionary, key):
    """
    Получает значение из словаря по ключу
    """
    return dictionary.get(key)

@register.filter
def get_range(value):
    """
    Возвращает диапазон от 1 до value
    """
    return range(1, int(value) + 1) 