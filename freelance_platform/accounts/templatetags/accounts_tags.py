from django import template

register = template.Library()

@register.filter(name='accounts_add_class')
def accounts_add_class(field, css_class):
    """Добавляет CSS класс к виджету поля формы (Accounts app версия)"""
    return field.as_widget(attrs={
        "class": " ".join((field.field.widget.attrs.get('class', ''), css_class))
    }) 