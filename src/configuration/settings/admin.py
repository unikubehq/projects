"""
Django settings for unikube project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
from .base import *
from .base import INSTALLED_APPS

ROOT_URLCONF = "configuration.urls.admin"
