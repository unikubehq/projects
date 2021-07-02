import graphene
from commons.keycloak.abstract_models import KeycloakResource
from commons.keycloak.groups import GroupHandler
from commons.keycloak.users import UserHandler
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import GraphQLError, ResolveInfo

from projects.forms import ClusterSettingsForm, EnvironmentForm, ProjectForm
from projects.models import Environment, Project
from sops.models.aws import AWSKMS
from sops.models.base import SOPSProvider
from sops.models.pgp import PGPKey

from .query import ClusterSettingsNode, EnvironmentNode, ProjectNode


class CreateUpdateProject(DjangoModelFormMutation):
    project = graphene.Field(ProjectNode)

    @classmethod
    def perform_mutate(cls, form, info):
        result = super(CreateUpdateProject, cls).perform_mutate(form, info)
        # add this user as an administrator of this project
        uh = UserHandler()
        admin_group = form.instance.keycloak_data["groups"].get(KeycloakResource.ADMINS)
        uh.join_group(info.context.kcuser["uuid"], admin_group)
        return result

    class Meta:
        form_class = ProjectForm
        convert_choices_to_enum = True


class ProjectMemberRoleEnum(graphene.Enum):
    admin = "admin"
    member = "member"


class CreateProjectMember(graphene.Mutation):
    class Arguments:
        id = graphene.UUID()
        user = graphene.UUID()
        role = graphene.Argument(ProjectMemberRoleEnum)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if info.context.permissions.has_permission(str(kwargs.get("id")), "project:edit"):
            project = Project.objects.get(id=kwargs.get("id"))
            try:
                # we currently accept every user to be added to the project (also user not part of the orga)
                if kwargs.get("role") == ProjectMemberRoleEnum.admin:
                    UserHandler().join_group(
                        str(kwargs.get("user")), project.keycloak_data["groups"].get(KeycloakResource.ADMINS)
                    )
                    return cls(ok=True)
                elif kwargs.get("role") == ProjectMemberRoleEnum.member:
                    UserHandler().join_group(
                        str(kwargs.get("user")), project.keycloak_data["groups"].get(KeycloakResource.MEMBERS)
                    )
                    return cls(ok=True)
                else:
                    return cls(ok=False)
            except Exception:
                raise GraphQLError("Could not add this user to project.")
        else:
            raise GraphQLError("This user does not have permission to add a user to this project.")


class DeleteProjectMember(graphene.Mutation):
    class Arguments:
        id = graphene.UUID()
        user = graphene.UUID()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if info.context.permissions.has_permission(str(kwargs.get("id")), "project:edit"):
            project = Project.objects.get(id=kwargs.get("id"))
            try:
                UserHandler().leave_group(
                    str(kwargs.get("user")), project.keycloak_data["groups"].get(KeycloakResource.ADMINS)
                )
                UserHandler().leave_group(
                    str(kwargs.get("user")), project.keycloak_data["groups"].get(KeycloakResource.MEMBERS)
                )
                return cls(ok=True)
            except Exception:
                raise GraphQLError("Could not remove this user from project.")
        else:
            raise GraphQLError("This user does not have permission to remove a user from this project.")


class DeleteProject(graphene.Mutation):
    class Arguments:
        id = graphene.UUID()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        obj = Project.objects.get(id=kwargs.get("id"))
        obj.delete()
        return cls(ok=True)


class UpdateProjectRepository(graphene.Mutation):
    class Arguments:
        id = graphene.UUID()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        project = Project.objects.get(id=kwargs["id"])
        project.update_repository()
        return cls(ok=True)


class SOPSTypeEnum(graphene.Enum):
    aws = "aws"
    pgp = "pgp"


class SOPSInputType(graphene.InputObjectType):
    title = graphene.String(required=True)
    description = graphene.String(required=False)
    sops_type = SOPSTypeEnum(required=True)
    project = graphene.UUID(required=True)
    secret_1 = graphene.String(required=False)  # On edit this field is only provided when changed.
    secret_2 = graphene.String(required=False)  # AWS KMS required 2 fields.
    secret_3 = graphene.String(required=False)  # Backup in case we need 3 fields for secret information.


class CreateUpdateSOPS(graphene.Mutation):
    class Arguments:
        sops_data = SOPSInputType(required=True)
        id = graphene.UUID(required=False)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info: ResolveInfo, **kwargs):
        sops_data = kwargs.get("sops_data")
        sops_id = kwargs.get("id")
        try:
            project = Project.objects.get(id=sops_data.project)
        except Project.DoesNotExist:
            raise GraphQLError("Project does not exist.")
        if sops_id:
            try:
                sops_provider = SOPSProvider.objects.get(id=sops_id)
            except SOPSProvider.DoesNotExist:
                raise GraphQLError("SOPS Provider does not exist.")
            else:
                if sops_data.sops_type == "aws":
                    awskms = sops_provider.get_real_instance()
                    awskms.title = sops_data.title
                    awskms.description = sops_data.description
                    if hasattr(sops_data, "secret_1") and getattr(sops_data, "secret_1"):
                        awskms.access_key = sops_data.secret_1
                    if hasattr(sops_data, "secret_2") and getattr(sops_data, "secret_2"):
                        awskms.secret_access_key = sops_data.secret_2
                    awskms.save()
                elif sops_data.sops_type == "pgp":
                    pgp_key = sops_provider.get_real_instance()
                    pgp_key.title = sops_data.title
                    pgp_key.description = sops_data.description
                    if hasattr(sops_data, "secret_1") and getattr(sops_data, "secret_1"):
                        pgp_key.private_key = sops_data.secret_1
                    pgp_key.save()
                else:
                    raise GraphQLError(f"Unsupported SOPS type {sops_data.sops_type}.")
        else:
            if sops_data.sops_type == "aws":
                if not hasattr(sops_data, "secret_1") or not hasattr(sops_data, "secret_2"):
                    raise GraphQLError("Missing secret(s).")
                AWSKMS.objects.create(
                    title=sops_data.title,
                    description=sops_data.description,
                    access_key=sops_data.secret_1,
                    secret_access_key=sops_data.secret_2,
                    project=project,
                )
            elif sops_data.sops_type == "pgp":
                if not hasattr(sops_data, "secret_1"):
                    raise GraphQLError("Missing secret.")
                PGPKey.objects.create(
                    title=sops_data.title,
                    description=sops_data.description,
                    private_key=sops_data.secret_1,
                    project=project,
                )
            else:
                raise GraphQLError(f"Unsupported SOPS type {sops_data.sops_type}.")
        return cls(ok=True)


class DeleteSOPS(graphene.Mutation):
    class Arguments:
        id = graphene.UUID()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info: ResolveInfo, **kwargs):
        pk = kwargs.get("id")
        SOPSProvider.objects.get(id=pk).delete()
        return cls(ok=True)


class CreateUpdateEnvironment(DjangoModelFormMutation):
    environment = graphene.Field(EnvironmentNode)

    class Meta:
        form_class = EnvironmentForm
        convert_choices_to_enum = True
        return_field_name = "environment"


class DeleteEnvironment(graphene.Mutation):
    class Arguments:
        id = graphene.UUID()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        obj = Environment.objects.get(id=kwargs.get("id"))
        obj.delete()
        return cls(ok=True)


class UpdateClusterSettings(DjangoModelFormMutation):
    cluster_settings = graphene.Field(ClusterSettingsNode)

    class Meta:
        form_class = ClusterSettingsForm
        convert_choices_to_enum = True
        return_field_name = "cluster_settings"


class Mutation(graphene.ObjectType):
    create_update_project = CreateUpdateProject.Field()
    create_project_member = CreateProjectMember.Field()
    delete_project_member = DeleteProjectMember.Field()
    delete_project = DeleteProject.Field()
    create_update_environment = CreateUpdateEnvironment.Field()
    delete_environment = DeleteEnvironment.Field()
    create_update_sops = CreateUpdateSOPS.Field()
    delete_sops = DeleteSOPS.Field()
    update_cluster_settings = UpdateClusterSettings.Field()
