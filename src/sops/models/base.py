import uuid

from django.db import models
from django_extensions.db.models import TitleDescriptionModel
from polymorphic.models import PolymorphicModel


class SOPSProvider(TitleDescriptionModel, PolymorphicModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(verbose_name="Project", to="projects.Project", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.get_sops_type()} {self.title} - {self.description}"

    def get_environment(self):
        return self.get_real_instance().get_environment()

    def get_sops_type(self):
        return self.get_real_instance().get_sops_type()
