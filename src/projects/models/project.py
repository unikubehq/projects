import logging
import uuid
from typing import Optional

from commons.keycloak.abstract_models import KeycloakResource
from django.db import models
from django.db.models import QuerySet
from django.db.models.aggregates import Max
from django_extensions.db.fields import CreationDateTimeField
from django_extensions.db.models import TitleDescriptionModel

from projects.models import Deck
from projects.utils.model import NonUniqueSlugMixin

logger = logging.getLogger("unikube.projects")
# p = Project.objects.create(title="FF Hub", access_username="gitlab+deploy-token-32", access_token="KzANezy9YwiaXz8sYn_U", spec_repository="https://gitlab.blueshoe.de/fondsfinanz/fondsfinanz-charts.git", spec_type="helm")


class RepositoryStatus:
    UNKNOWN = "unknown"
    CLONING_PENDING = "cloning-pending"
    CLONING = "cloning"
    CLONING_FAILED = "cloning-failed"
    CLONING_SUCCESSFUL = "cloning-successful"
    BRANCH_UNAVAILABLE = "branch-unavailable"
    AUTH_FAILED = "auth-failed"
    PARSING_FAILED = "parsing-failed"
    OK = "ok"


class Project(TitleDescriptionModel, NonUniqueSlugMixin, KeycloakResource):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    SPEC_CHOICES = [("helm", "Helm")]
    REPOSITORY_STATUS_CHOICES = [
        (RepositoryStatus.UNKNOWN, "Unknown"),
        (RepositoryStatus.CLONING_PENDING, "Cloning Pending"),
        (RepositoryStatus.CLONING, "Cloning"),
        (RepositoryStatus.CLONING_FAILED, "Failed"),
        (RepositoryStatus.CLONING_SUCCESSFUL, "Successful"),
        (RepositoryStatus.BRANCH_UNAVAILABLE, "Branch not found"),
        (RepositoryStatus.AUTH_FAILED, "Authentication failed"),
        (RepositoryStatus.PARSING_FAILED, "Parsing failed"),
        (RepositoryStatus.OK, "Okay"),
    ]

    spec_repository = models.URLField(help_text="Please provide the HTTPS URL to the Kubernetes Spec repository.")

    spec_repository_branch = models.TextField(
        help_text="Please provide the branch for the Kubernetes Spec repository.", null=True, blank=True
    )

    created = CreationDateTimeField()

    spec_type = models.CharField("Type", max_length=5, choices=SPEC_CHOICES)

    current_commit = models.TextField(blank=True)
    current_commit_date_time = models.DateTimeField(blank=True, null=True)
    repository_status = models.CharField(
        "Repository Status", max_length=32, choices=REPOSITORY_STATUS_CHOICES, default=REPOSITORY_STATUS_CHOICES[0][0]
    )

    access_username = models.TextField("Access Username", blank=True)
    access_token = models.TextField("Access Token", blank=True)

    organization = models.UUIDField(default=uuid.uuid4, editable=True)

    def __str__(self):
        return f"Project: {self.title}"

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def save(self, *args, **kwargs):
        update_repo = kwargs.pop("update_repository", False)
        super(Project, self).save(*args, **kwargs)
        if update_repo:
            self.update_repository()

    def update_repository(self, updating_decks: QuerySet = None, render=False):
        from projects.tasks import update_repository_information

        self.repository_status = RepositoryStatus.CLONING_PENDING
        self.save()
        if updating_decks:
            update_repository_information.delay(
                self.pk, deck_ids=list(updating_decks.values_list("pk", flat=True)), render=render
            )
        else:
            update_repository_information.delay(self.pk, render=render)

    def add_cluster_settings(self):
        """
        Add cluster settings to a project.

        The port for the cluster settings is set to avoid collisions between projects.
        The default port is 61335. It was chosen by multiplying the char code of all letters of 'unikube' and
        applying
        modulo 65535 (highest possible port).
        """
        highest_cluster_port = Project.objects.filter(organization=self.organization).aggregate(
            Max("cluster_settings__port")
        )["cluster_settings__port__max"]
        if highest_cluster_port:
            # Create with port + 1 to avoid collisions between projects.
            cluster_settings = ClusterSettings.objects.create(port=highest_cluster_port + 1, project=self)
        else:
            # Create with default port
            cluster_settings = ClusterSettings.objects.create(project=self)
        self.cluster_settings = cluster_settings
        self.save()

    def get_keycloak_name(self) -> Optional[str]:
        return f"{self.slug}({str(self.pk)})"


class Environment(TitleDescriptionModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TYPE_CHOICES = [("local", "Local"), ("remote", "Remote")]

    deck = models.ForeignKey("projects.Deck", related_name="environments", on_delete=models.CASCADE)

    type = models.CharField("Type", max_length=6, blank=False, choices=TYPE_CHOICES)

    values_path = models.TextField()
    values_type = models.CharField(
        "Values Type",
        max_length=32,
        choices=(
            ("file", "File"),
            ("dir", "Directory"),
        ),
        blank=True,
        null=True,
    )

    namespace = models.TextField(default="default")

    value_schema = models.TextField(null=True)

    sops_credentials = models.ForeignKey(
        "sops.SOPSProvider",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.deck.title}:{self.title} ({self.type})"

    class Meta:
        verbose_name = "Environment"
        verbose_name_plural = "Environments"
        unique_together = ("deck", "type")

    def save(self, *args, **kwargs):
        update_project = kwargs.pop("update_project", False)
        super(Environment, self).save(*args, **kwargs)
        if update_project:
            updating_deck = Deck.objects.filter(pk=self.deck.pk)
            self.deck.project.update_repository(updating_decks=updating_deck, render=True)

    @classmethod
    def create_initial_environment(cls, deck):
        return Environment.objects.create(
            title="auto-created environment",
            deck=deck,
            type=cls.TYPE_CHOICES[0][0],
            values_path="",
        )


class ClusterSettings(models.Model):
    PROVIDER_CHOICES = (("k3d", "k3d"),)

    project = models.OneToOneField(
        verbose_name="Project", to="projects.Project", on_delete=models.CASCADE, related_name="cluster_settings"
    )

    port = models.PositiveIntegerField(verbose_name="Port", default=61335)

    provider = models.CharField(verbose_name="K8S Provider", max_length=255, choices=PROVIDER_CHOICES)


class HelmOverrides(models.Model):
    environment = models.OneToOneField(
        verbose_name="Environment", to="projects.Environment", on_delete=models.CASCADE, related_name="helm_overrides"
    )

    overrides = models.TextField(
        verbose_name="overrides",
    )
