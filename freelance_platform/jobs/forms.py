from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Project, Proposal, Contract, Milestone, Category, Tag

class ProjectForm(forms.ModelForm):
    """
    Форма для создания и редактирования проектов
    """
    tags = forms.CharField(
        required=False,
        label=_('Tags (comma separated)'),
        widget=forms.TextInput(attrs={'placeholder': _('e.g. web design, logo, programming')})
    )
    
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'category', 'budget_type', 'budget_min', 
            'budget_max', 'deadline', 'location_required', 'is_remote', 
            'experience_required', 'is_private', 'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'budget_min': forms.NumberInput(attrs={'step': '0.01'}),
            'budget_max': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Если редактируем существующий проект
        if self.instance.pk:
            # Преобразуем список тегов в строку через запятую
            tag_names = ', '.join([tag.name for tag in self.instance.tags.all()])
            self.initial['tags'] = tag_names
    
    def save(self, commit=True):
        project = super().save(commit=False)
        
        if commit:
            project.save()
            
            # Обработка тегов
            tag_input = self.cleaned_data.get('tags', '')
            if tag_input:
                # Удалить существующие теги
                project.tags.clear()
                
                # Добавить новые теги
                tag_names = [tag.strip() for tag in tag_input.split(',') if tag.strip()]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={'slug': tag_name.lower().replace(' ', '-')}
                    )
                    project.tags.add(tag)
        
        return project

class ProposalForm(forms.ModelForm):
    """
    Форма для подачи предложений на проект
    """
    class Meta:
        model = Proposal
        fields = ['cover_letter', 'bid_amount', 'delivery_time']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 5}),
            'bid_amount': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project
        
        if project:
            self.fields['bid_amount'].help_text = _(f'Budget range: {project.budget_min} - {project.budget_max}')

class ContractForm(forms.ModelForm):
    """
    Форма для создания контракта
    """
    class Meta:
        model = Contract
        fields = ['title', 'description', 'amount', 'deadline']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

class MilestoneForm(forms.ModelForm):
    """
    Форма для создания этапов контракта
    """
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'amount', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

class MilestoneFormSet(forms.BaseInlineFormSet):
    """
    Формсет для работы с несколькими этапами одновременно
    """
    def clean(self):
        super().clean()
        
        # Проверить, что общая сумма этапов не превышает сумму контракта
        total_amount = 0
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            if form.cleaned_data.get('amount'):
                total_amount += form.cleaned_data.get('amount')
        
        contract_amount = self.instance.amount if hasattr(self, 'instance') else 0
        if total_amount > contract_amount:
            raise forms.ValidationError(
                _('The total amount of all milestones cannot exceed the contract amount.')
            )

# Форма для поиска проектов
class ProjectSearchForm(forms.Form):
    query = forms.CharField(
        required=False, 
        label=_('Search'),
        widget=forms.TextInput(attrs={
            'placeholder': _('Search projects...'),
            'class': 'form-control'
        })
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.all(),
        label=_('Category'),
        empty_label=_('All Categories'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tags = forms.CharField(
        required=False,
        label=_('Skills/Tags'),
        widget=forms.TextInput(attrs={
            'placeholder': _('e.g. python, design'),
            'class': 'form-control'
        })
    )
    min_budget = forms.DecimalField(
        required=False,
        min_value=0,
        label=_('Minimum Budget'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'class': 'form-control'
        })
    )
    max_budget = forms.DecimalField(
        required=False,
        min_value=0,
        label=_('Maximum Budget'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'class': 'form-control'
        })
    )
    budget_type = forms.ChoiceField(
        required=False,
        choices=[('', _('Any')), ('fixed', _('Fixed Price')), ('hourly', _('Hourly Rate'))],
        label=_('Budget Type'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_remote = forms.BooleanField(
        required=False,
        label=_('Remote only'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    location = forms.CharField(
        required=False,
        label=_('Location'),
        widget=forms.TextInput(attrs={
            'placeholder': _('e.g. Almaty, Astana'),
            'class': 'form-control'
        })
    )
    experience_level = forms.ChoiceField(
        required=False,
        choices=[
            ('', _('Any')),
            ('entry', _('Entry Level')),
            ('intermediate', _('Intermediate')),
            ('expert', _('Expert'))
        ],
        label=_('Experience Level'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('recent', _('Most Recent')),
            ('budget_high', _('Highest Budget')),
            ('budget_low', _('Lowest Budget')),
            ('deadline', _('Deadline')),
        ],
        label=_('Sort By'),
        initial='recent',
        widget=forms.Select(attrs={'class': 'form-select'})
    ) 