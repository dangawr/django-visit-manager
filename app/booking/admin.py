from django.contrib import admin
from .models import Client, Visit


class ClientAdmin(admin.ModelAdmin):
    pass


class VisitAdmin(admin.ModelAdmin):
    pass


admin.site.register(Client, ClientAdmin)
admin.site.register(Visit, VisitAdmin)
