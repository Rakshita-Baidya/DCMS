from django.contrib import admin
from .models import User

# Register your models here.


from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role',
                    'is_active', 'is_approved')
    list_filter = ('is_active', 'role', 'is_approved')
    actions = ['approve_users']

    @admin.action(description='Approve selected users')
    def approve_users(self, request, queryset):
        queryset.update(is_active=True)


admin.site.register(User, UserAdmin)
