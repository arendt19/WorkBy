from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Добавляет CSS класс к виджету поля формы"""
    return field.as_widget(attrs={
        "class": " ".join((field.field.widget.attrs.get('class', ''), css_class))
    }) 