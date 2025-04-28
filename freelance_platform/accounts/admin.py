from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FreelancerProfile, ClientProfile, Review

class FreelancerProfileInline(admin.StackedInline):
    model = FreelancerProfile
    can_delete = False
    verbose_name_plural = 'Freelancer Profile'
    fk_name = 'user'

class ClientProfileInline(admin.StackedInline):
    model = ClientProfile
    can_delete = False
    verbose_name_plural = 'Client Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('user_type', 'bio', 'avatar', 'phone_number', 'preferred_language', 
                                              'dark_mode', 'skills', 'hourly_rate', 'company_name')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = UserAdmin.list_filter + ('user_type',)
    
    def get_inlines(self, request, obj=None):
        if obj:
            if obj.user_type == 'freelancer':
                return [FreelancerProfileInline]
            elif obj.user_type == 'client':
                return [ClientProfileInline]
        return []

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('freelancer', 'client', 'project', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('freelancer__username', 'client__username', 'comment')
    date_hierarchy = 'created_at'
    raw_id_fields = ('freelancer', 'client', 'project')

admin.site.register(User, CustomUserAdmin)
