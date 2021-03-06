# Generated by Django 2.2.23 on 2021-05-26 19:09

import uuid

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
import django_extensions.db.fields
from django.db import migrations, models

import projects.utils.model


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Deck",
            fields=[
                ("title", models.CharField(max_length=255, verbose_name="title")),
                ("description", models.TextField(blank=True, null=True, verbose_name="description")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("dir_path", models.TextField()),
                ("type", models.TextField()),
                (
                    "namespace",
                    models.TextField(
                        default="unikube",
                        help_text="The kubernetes namespace for the application to be deployed to.",
                        verbose_name="Namespace",
                    ),
                ),
                (
                    "file_information",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True,
                        help_text="Stores directory and file information like directory structure and SOPS meta information.",
                        null=True,
                    ),
                ),
                ("hash", models.TextField()),
            ],
            options={
                "verbose_name": "Deck",
                "verbose_name_plural": "Decks",
            },
            bases=(models.Model, projects.utils.model.NonUniqueSlugMixin),
        ),
        migrations.CreateModel(
            name="Environment",
            fields=[
                ("title", models.CharField(max_length=255, verbose_name="title")),
                ("description", models.TextField(blank=True, null=True, verbose_name="description")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "type",
                    models.CharField(
                        choices=[("local", "Local"), ("remote", "Remote")], max_length=6, verbose_name="Type"
                    ),
                ),
                ("values_path", models.TextField()),
                (
                    "values_type",
                    models.CharField(
                        blank=True,
                        choices=[("file", "File"), ("dir", "Directory")],
                        max_length=32,
                        null=True,
                        verbose_name="Values Type",
                    ),
                ),
                (
                    "deck",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="environments", to="projects.Deck"
                    ),
                ),
            ],
            options={
                "verbose_name": "Cluster Level",
                "verbose_name_plural": "Cluster Levels",
            },
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                ("title", models.CharField(max_length=255, verbose_name="title")),
                ("description", models.TextField(blank=True, null=True, verbose_name="description")),
                ("keycloak_data", django.contrib.postgres.fields.jsonb.JSONField(default={"groups": {}})),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "spec_repository",
                    models.URLField(help_text="Please provide the HTTPS URL to the Kubernetes Spec repository."),
                ),
                (
                    "spec_repository_branch",
                    models.TextField(
                        blank=True, help_text="Please provide the branch for the Kubernetes Spec repository.", null=True
                    ),
                ),
                ("created", django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                (
                    "spec_type",
                    models.CharField(choices=[("plain", "Plain"), ("helm", "Helm")], max_length=5, verbose_name="Type"),
                ),
                ("current_commit", models.TextField(blank=True)),
                ("current_commit_date_time", models.DateTimeField(blank=True, null=True)),
                (
                    "repository_status",
                    models.CharField(
                        choices=[
                            ("unknown", "Unknown"),
                            ("cloning-pending", "Cloning Pending"),
                            ("cloning", "Cloning"),
                            ("cloning-failed", "Failed"),
                            ("cloning-successful", "Successful"),
                            ("branch-unavailable", "Branch not found"),
                            ("auth-failed", "Authentication failed"),
                            ("parsing-failed", "Parsing failed"),
                            ("ok", "Okay"),
                        ],
                        default="unknown",
                        max_length=32,
                        verbose_name="Repository Status",
                    ),
                ),
                ("access_username", models.TextField(blank=True, verbose_name="Access Username")),
                ("access_token", models.TextField(blank=True, verbose_name="Access Token")),
                ("organization", models.UUIDField(default=uuid.uuid4)),
            ],
            options={
                "verbose_name": "Project",
                "verbose_name_plural": "Projects",
            },
            bases=(projects.utils.model.NonUniqueSlugMixin, models.Model),
        ),
        migrations.CreateModel(
            name="K8SDeployment",
            fields=[
                ("title", models.CharField(max_length=255, verbose_name="title")),
                ("description", models.TextField(blank=True, null=True, verbose_name="description")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("ports", models.CharField(max_length=200)),
                (
                    "is_switchable",
                    models.BooleanField(default=True, help_text="Can this deployment be switch with Telepresence"),
                ),
                (
                    "environment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deployments",
                        to="projects.Environment",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
