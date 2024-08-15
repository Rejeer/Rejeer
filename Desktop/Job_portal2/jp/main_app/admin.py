from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'is_staff')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_approved', 'role')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser', 'role'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Company)
admin.site.register(JobAds)
admin.site.register(Education)
admin.site.register(Skill)
admin.site.register(JobType)
admin.site.register(Applicant)
admin.site.register(Application)
admin.site.register(Notification)