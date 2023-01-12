from django.contrib import admin
from .models import Client, Visit, User
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            'Sms Remainder',
            {
                'fields': (
                    'sms_remainder',
                    'balance',
                    'sms_price',
                    'business_name',
                ),
            },
        ),
    )


class ClientAdmin(admin.ModelAdmin):
    pass


class VisitAdmin(admin.ModelAdmin):
    pass


admin.site.register(Client, ClientAdmin)
admin.site.register(Visit, VisitAdmin)
