from django.contrib import admin

from projects.models import Deck, Environment, HelmOverrides, K8SDeployment, Project

admin.site.register(Project)
admin.site.register(Environment)
admin.site.register(Deck)
admin.site.register(K8SDeployment)
admin.site.register(HelmOverrides)
