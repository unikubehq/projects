import uuid

import graphene
from commons.graphql.nodes import page_field_factory, resolve_page
from commons.keycloak.abstract_models import KeycloakResource
from commons.keycloak.groups import GroupHandler
from graphene import UUID, ObjectType
from graphene_django import DjangoObjectType
from graphene_federation import extend, external, key
from graphql import GraphQLError, ResolveInfo

from projects.models import ClusterSettings, Deck, Environment, HelmOverrides, K8SDeployment, Project
from sops.models.aws import AWSKMS
from sops.models.base import SOPSProvider
from sops.models.pgp import PGPKey


@extend(fields="id")
class UserNode(ObjectType):
    id = external(UUID(required=True))


class ProjectMember(ObjectType):
    user = graphene.Field(UserNode)
    role = graphene.String()


@extend(fields="id")
class OrganizationNode(graphene.ObjectType):
    id = external(graphene.UUID(required=True))


class FileInformationNode(ObjectType):
    path = graphene.String()
    encrypted = graphene.Boolean()


@key("id")
class DeckNode(DjangoObjectType):
    deployments = graphene.List(lambda: DeploymentNode, level=graphene.String(), switchable=graphene.Boolean())
    environment = graphene.List(lambda: EnvironmentNode, level=graphene.String())
    file_information = graphene.List(lambda: FileInformationNode)

    class Meta:
        model = Deck
        exclude = ("environments",)

    def resolve_file_information(self, info):
        result = []
        if self.file_information and "information" in self.file_information:
            for file_info in self.file_information["information"]:
                result.append(FileInformationNode(path=file_info["path"], encrypted=file_info["encrypted"]))
        return result

    def resolve_deployments(self, info, level=None, switchable=None):
        deployments = K8SDeployment.objects.filter(environment__deck=self)
        if level is not None:
            deployments = deployments.filter(environment__type=level)
        if switchable is not None:
            deployments = deployments.filter(is_switchable=switchable)
        return deployments

    def resolve_environment(self, info, level=None):
        environment = Environment.objects.filter(deck=self)
        if level is not None:
            return environment.filter(type=level)
        return environment


class DeploymentNode(DjangoObjectType):
    class Meta:
        model = K8SDeployment


class AWSKMSNode(DjangoObjectType):
    class Meta:
        model = AWSKMS
        fields = ("title", "description", "id", "access_key", "secret_access_key")

    def resolve_access_key(self, info):
        if info.context.headers.get("x-internal"):
            return self.access_key
        return str(bool(self.access_key))

    def resolve_secret_access_key(self, info):
        if info.context.headers.get("x-internal"):
            return self.secret_access_key
        return str(bool(self.secret_access_key))


class PGPKeyNode(DjangoObjectType):
    class Meta:
        model = PGPKey
        fields = ("title", "description", "id", "private_key")

    def resolve_private_key(self, info):
        if info.context.headers.get("x-internal"):
            return self.private_key
        return str(bool(self.private_key))


class SOPSProviderNode(graphene.Union):
    class Meta:
        types = (AWSKMSNode, PGPKeyNode)

    @classmethod
    def resolve_type(cls, instance, info):
        if instance.get_sops_type() == "aws":
            return AWSKMSNode
        if instance.get_sops_type() == "pgp":
            return PGPKeyNode


class ClusterSettingsNode(DjangoObjectType):
    class Meta:
        model = ClusterSettings
        fields = ("port", "id")  # only work with port for now


@key("id")
class ProjectNode(DjangoObjectType):
    organization = graphene.Field(OrganizationNode)
    access_token = graphene.String()
    sops = graphene.List(SOPSProviderNode)
    members = graphene.List(ProjectMember)
    cluster_settings = graphene.Field(ClusterSettingsNode)

    def resolve_decks(self, info: ResolveInfo, **kwargs):
        return Deck.objects.filter(project=self)

    def resolve_organization(self, info: ResolveInfo, **kwargs):
        return OrganizationNode(id=self.organization)

    def resolve_access_token(self, info, **kwargs):
        if info.context.headers.get("x-internal"):
            return self.access_token
        return str(bool(self.access_token))

    def resolve_cluster_settings(self, info, **kwargs):
        return ClusterSettings.objects.get(project=self)

    def resolve_sops(self, info: ResolveInfo, **kwargs):
        return SOPSProvider.objects.filter(project=self).get_real_instances()

    def resolve_members(self, info, **kwargs):
        member_list = []
        gh = GroupHandler()
        admin_group = self.keycloak_data["groups"].get(KeycloakResource.ADMINS)
        member_group = self.keycloak_data["groups"].get(KeycloakResource.MEMBERS)
        admins = gh.members(admin_group)
        for a in admins:
            member_list.append(ProjectMember(user=UserNode(id=a["id"]), role="admin"))
        members = gh.members(member_group)
        for m in members:
            member_list.append(ProjectMember(user=UserNode(id=m["id"]), role="member"))
        return member_list

    class Meta:
        model = Project


class HelmOverridesNode(DjangoObjectType):
    class Meta:
        model = HelmOverrides
        fields = (
            "id",
            "overrides",
        )


class EnvironmentNode(DjangoObjectType):
    specs_url = graphene.String()
    sops_credentials = graphene.Field(SOPSProviderNode)
    value_schema = graphene.String()
    helm_overrides = graphene.Field(HelmOverridesNode)

    def resolve_specs_url(self, info: ResolveInfo):
        return f"/manifests/{self.id}"

    def resolve_sops_credentials(self, info, **kwargs):
        if self.sops_credentials:
            return self.sops_credentials.get_real_instance()
        return None

    class Meta:
        model = Environment


class Query(graphene.ObjectType):
    all_projects = page_field_factory(ProjectNode, organization_id=graphene.UUID())
    project = graphene.Field(ProjectNode, id=graphene.UUID(), slug=graphene.String())

    all_decks = page_field_factory(DeckNode, organization_id=graphene.UUID(), project_id=graphene.UUID())
    deck = graphene.Field(DeckNode, id=graphene.UUID(), slug=graphene.String())

    environment = graphene.Field(EnvironmentNode, id=graphene.UUID())

    @resolve_page
    def resolve_all_projects(self, info, organization_id: uuid = None, **kwargs):
        allowed_projects = info.context.permissions.get_resource_id_by_scope("project:*")
        projects = Project.objects.filter(id__in=allowed_projects)

        # filter
        if organization_id:
            projects = projects.filter(organization__exact=organization_id)

        return projects

    def resolve_project(self, info, id: uuid = None):
        # check if this project is allowed to be resolved
        allowed_projects = info.context.permissions.get_resource_id_by_scope("project:*")
        if str(id) not in allowed_projects:
            raise GraphQLError("This project cannot be retrieved.")
        return Project.objects.get(id=id)

    @resolve_page
    def resolve_all_decks(self, info, organization_id: uuid = None, project_id: uuid = None, **kwargs):
        allowed_projects = info.context.permissions.get_resource_id_by_scope("project:*")
        decks = Deck.objects.filter(project__id__in=allowed_projects)

        # filter
        if organization_id:
            decks = decks.filter(project__organization__exact=organization_id)

        if project_id:
            decks = decks.filter(project__id__exact=project_id)

        return decks

    def resolve_deck(self, info, id: uuid = None):
        # TODO: check if this deck is allowed to be resolved
        return Deck.objects.get(id=id)

    def resolve_environment(self, info, id: str):
        allowed_projects = info.context.permissions.get_resource_id_by_scope("project:*")
        try:
            environment = Environment.objects.get(id=id)
        except Environment.DoesNotExist:
            raise GraphQLError("This environment cannot be retrieved.")
        if str(environment.deck.project.id) in allowed_projects:
            return environment
        else:
            raise GraphQLError("This environment cannot be retrieved.")
