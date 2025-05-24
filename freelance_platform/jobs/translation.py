from modeltranslation.translator import register, TranslationOptions
from .models import Project

# Примечание: модели Category и Tag уже имеют встроенные поля перевода
# Поэтому мы регистрируем только Project

@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
