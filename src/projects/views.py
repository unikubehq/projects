import logging

from django import views
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from projects.models import Environment

logger = logging.getLogger("unikube.views")


class K8sSpecsView(views.View):
    def get(self, request, environment_uuid):
        environment = get_object_or_404(Environment, pk=environment_uuid)
        if environment.application not in request.user.get_applications():
            return HttpResponse(status=403)
        # this user has access to the environment
        # todo handle other project types
        if environment.application.project.spec_type == "helm":
            # specfiles = HelmHandler().get_all_spec_files(environment)
            specfiles = []

            return JsonResponse({"specs": [{"sourceName": k.sourceName, "content": k.content} for k in specfiles]})
        else:
            raise Http404
