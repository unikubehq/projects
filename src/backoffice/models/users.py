from django.contrib.auth.models import AbstractUser

from projects.utils.model import UUIDMixin


class AdminUser(AbstractUser, UUIDMixin):
    pass
