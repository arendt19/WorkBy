from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.contrib.auth.validators import UnicodeUsernameValidator

from .models import User, FreelancerProfile, ClientProfile, Review, PortfolioProject, PortfolioImage

class UserProfileForm(forms.ModelForm):
    """
    Форма для обновления базовой информации профиля
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'avatar', 
                  'phone_number', 'preferred_language', 'dark_mode')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5}),
        }

class FreelancerProfileForm(forms.ModelForm):
    """
    Форма для профиля фрилансера
    """
    class Meta:
        model = FreelancerProfile
        fields = ('portfolio_website', 'is_available', 'experience_years', 
                  'education', 'certifications', 'resume', 'specialization', 'languages')
        widgets = {
            'education': forms.Textarea(attrs={'rows': 3}),
            'certifications': forms.Textarea(attrs={'rows': 3}),
            'languages': forms.TextInput(attrs={'placeholder': _('English, Russian, Kazakh')}),
        }

class FreelancerUserForm(forms.ModelForm):
    """
    Форма для обновления информации связанной с фрилансером в модели User
    """
    class Meta:
        model = User
        fields = ('skills', 'hourly_rate')
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3}),
        }

class ClientProfileForm(forms.ModelForm):
    """
    Форма для профиля клиента
    """
    class Meta:
        model = ClientProfile
        fields = ('company_website', 'industry', 'company_size')

class ClientUserForm(forms.ModelForm):
    """
    Форма для обновления информации связанной с клиентом в модели User
    """
    class Meta:
        model = User
        fields = ('company_name',)

class ReviewForm(forms.ModelForm):
    """
    Форма для создания отзыва о фрилансере
    """
    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {
            'rating': forms.RadioSelect(),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': _('Describe your experience with this freelancer')})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].help_text = _('Rate from 1 to 5 stars')

class PortfolioProjectForm(forms.ModelForm):
    """
    Форма для создания и редактирования проектов в портфолио
    """
    class Meta:
        model = PortfolioProject
        fields = ('title', 'description', 'completed_date', 'client_name', 'url', 'categories')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'completed_date': forms.DateInput(attrs={'type': 'date'}),
            'categories': forms.CheckboxSelectMultiple(),
        }

class PortfolioImageForm(forms.ModelForm):
    """
    Форма для добавления изображений к проектам в портфолио
    """
    class Meta:
        model = PortfolioImage
        fields = ('image', 'caption', 'order')
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': _('Short description of the image')}),
        }

# Формсет для работы с несколькими изображениями одновременно
PortfolioImageFormSet = forms.inlineformset_factory(
    PortfolioProject, 
    PortfolioImage,
    form=PortfolioImageForm,
    extra=3,  # Количество пустых форм
    max_num=10,  # Максимальное количество форм
    can_delete=True  # Возможность удаления
)

class UserRegistrationForm(UserCreationForm):
    """
    Форма для регистрации новых пользователей с дружелюбными сообщениями
    """
    USER_TYPE_CHOICES = [
        ('freelancer', _('Freelancer')),
        ('client', _('Client')),
    ]
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        label=_('Register as'),
        widget=forms.RadioSelect
    )
    
    email = forms.EmailField(
        required=True,
        help_text=_('Enter a valid email address to receive notifications and password reset links')
    )
    first_name = forms.CharField(
        required=True,
        help_text=_('Enter your first name for a more personalized experience')
    )
    last_name = forms.CharField(
        required=True,
        help_text=_('Enter your last name to increase trust on the platform')
    )
    
    # Переопределяем поле username для добавления дружелюбных подсказок
    username = forms.CharField(
        help_text=_('Choose a unique username. We recommend a professional nickname to stand out on the platform.'),
        max_length=150,
        required=True,
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': _('This username is already taken. Try adding numbers or other characters.'),
        },
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'user_type', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем более дружелюбные сообщения для пароля
        self.fields['password1'].help_text = _('Create a strong password: at least 8 characters including letters and numbers')
        
        # Добавляем атрибуты для валидации логина
        self.fields['username'].widget.attrs.update({
            'class': 'form-control username-field',
            'data-validate-username-url': '/accounts/check-username/',
            'autocomplete': 'off'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.user_type = self.cleaned_data['user_type']
        
        if commit:
            user.save()
            # Создаем соответствующий профиль только если его еще нет
            if user.user_type == 'freelancer':
                if not FreelancerProfile.objects.filter(user=user).exists():
                    FreelancerProfile.objects.create(user=user)
            else:
                if not ClientProfile.objects.filter(user=user).exists():
                    ClientProfile.objects.create(user=user)
                
        return user

class UserUpdateForm(forms.ModelForm):
    """
    Форма для обновления основной информации пользователя
    """
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio', 'avatar', 'phone_number']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        } 