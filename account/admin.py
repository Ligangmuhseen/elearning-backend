from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined', 'custom_actions')
    list_filter = ('is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
    (None, {
        'fields': ('email', 'first_name', 'last_name', 'phone_no','is_superuser', 'role', 'gender', 'is_active')
    }),
    ('Important Dates', {
        'fields': ('date_joined', 'last_login'),
        'classes': ('collapse',),
    }),
    ('Security', {
        'fields': ('password',),
        'classes': ('collapse',),
    }),
)

    
    # Define the fields to be read-only
    readonly_fields = ('date_joined', 'last_login', 'password')

    def custom_actions(self, obj):
        view_url = reverse('admin:account_customuser_change', args=[obj.userid])
        delete_url = reverse('admin:account_customuser_delete', args=[obj.userid])
        return format_html(
            '<a class="button" href="{}">View/Edit</a> &nbsp;'
            '<a class="button" href="{}" style="color:red;" onclick="return confirm(\'Are you sure you want to delete?\')">Delete</a>',
            view_url, delete_url
        )

    custom_actions.short_description = 'Actions'
    

# Register the model
admin.site.register(CustomUser, CustomUserAdmin)

