import logging
import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TitleDescriptionModel

from projects.utils.model import NonUniqueSlugMixin

logger = logging.getLogger("projects.k8s")


class Deck(TitleDescriptionModel, NonUniqueSlugMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey("projects.Project", related_name="decks", on_delete=models.CASCADE)

    dir_path = models.TextField()

    type = models.TextField()

    namespace = models.TextField(
        _("Namespace"),
        help_text=_("The kubernetes namespace for the application to be deployed to."),
        default="unikube",
    )

    file_information = JSONField(
        help_text="Stores directory and file information like directory structure and SOPS meta information.",
        blank=True,
        null=True,
    )

    # SHA-256 hash from title + type
    hash = models.TextField()

    def __str__(self):
        return f"{self.project.title}:{self.title}"

    class Meta:
        verbose_name = "Deck"
        verbose_name_plural = "Decks"

    def update_environments(self, deck_data):
        # TODO how to update deployments for multiple environments?
        # If deck is only updated we probably need to update the values of the environments.
        for environment in self.environments.all():
            if "information" in deck_data.file_information and all(
                environment.values_path != file_info["path"] for file_info in deck_data.file_information["information"]
            ):
                environment.values_path = ""
            environment.save()


class K8SDeployment(TitleDescriptionModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ports = models.CharField(max_length=200)

    environment = models.ForeignKey("projects.Environment", related_name="deployments", on_delete=models.CASCADE)

    is_switchable = models.BooleanField(default=True, help_text="Can this deployment be switch with Telepresence")

    def __str__(self):
        return f"{self.environment.deck.project.title}:{self.environment.title}#{self.title}"
