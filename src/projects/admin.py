from django.contrib import admin

from projects.models import Deck, Environment, K8SDeployment, Project

admin.site.register(Project)
admin.site.register(Environment)
admin.site.register(Deck)
admin.site.register(K8SDeployment)
