from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from backoffice.models import AdminUser

admin.site.register(AdminUser, BaseUserAdmin)
