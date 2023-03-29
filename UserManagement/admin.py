from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from UserManagement.models import CustomUser


# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    readonly_fields = [
        'date_joined',
    ]

    list_display = ('email', 'name', 'country', 'phone_no', 'role', 'is_active',)
    list_filter = ('country', 'role', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'country', 'phone_no')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'country', 'phone_no', 'password1', 'password2', 'role', 'is_active'),
        }),
    )
    search_fields = ('email', 'name', 'country', 'phone_no')
    ordering = ('email',)
    filter_horizontal = ()

    def get_ordering(self, request):
        ordering = super().get_ordering(request)
        print(ordering)
        ordering = (CustomUser.USERNAME_FIELD,)
        return ordering

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        if not is_superuser:
            disabled_fields |= {
                'username',
                'is_superuser',
                'user_permissions',
            }

        if not is_superuser and obj is not None and obj == request.user:
            disabled_fields |= {
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form


admin.site.register(CustomUser, CustomUserAdmin)