from django.contrib import admin
from .models import Category, Tag, Project, Proposal, Contract, Milestone

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class ProposalInline(admin.TabularInline):
    model = Proposal
    extra = 0
    fields = ('freelancer', 'bid_amount', 'delivery_time', 'status')
    readonly_fields = ('freelancer',)

class ContractInline(admin.TabularInline):
    model = Contract
    extra = 0
    fields = ('contract_id', 'freelancer', 'amount', 'status')
    readonly_fields = ('contract_id', 'freelancer')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'category', 'budget_type', 'budget_min', 'budget_max', 'status', 'created_at')
    list_filter = ('status', 'category', 'budget_type', 'is_remote', 'created_at')
    search_fields = ('title', 'description', 'client__username')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('tags',)
    inlines = [ProposalInline, ContractInline]
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('client', 'category')

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('freelancer', 'project', 'bid_amount', 'delivery_time', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('freelancer__username', 'project__title')
    readonly_fields = ('created_at', 'updated_at')

class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 1
    fields = ('title', 'amount', 'due_date', 'status')

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_id', 'title', 'client', 'freelancer', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('contract_id', 'title', 'client__username', 'freelancer__username')
    readonly_fields = ('contract_id', 'created_at', 'updated_at')
    inlines = [MilestoneInline]
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('client', 'freelancer', 'project')

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'contract', 'amount', 'due_date', 'status')
    list_filter = ('status', 'due_date')
    search_fields = ('title', 'contract__title', 'contract__contract_id')
    readonly_fields = ('created_at', 'updated_at')
