from django.contrib import admin
from .models import User

# Register your models here.


from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role',
                    'is_active')  # Correct field name
    list_filter = ('is_active', 'role')  # Correct field name
    actions = ['approve_users']

    @admin.action(description='Approve selected users')
    def approve_users(self, request, queryset):
        queryset.update(is_active=True)  # Correct field name


admin.site.register(User, UserAdmin)
