from typing import Iterable, List

import factory
from commons.keycloak.abstract_models import KeycloakResource
from commons.keycloak.permissions import KeycloakPermissions
from commons.keycloak.testing.driver import KeycloakDriver
from commons.keycloak.users import UserHandler
from django.test import RequestFactory
from environs import Env

from gql.tests import SnapshotGraphQLTestCase
from projects.tests.factories.project import ProjectFactory


class ProjectTests(SnapshotGraphQLTestCase):
    @classmethod
    def setUpClass(cls):
        env = Env()
        cls.driver = KeycloakDriver(
            env.int("KEYCLOAK_PORT"),
            env.str("KEYCLOAK_REALM_NAME"),
            env.str("KEYCLOAK_CLIENT_ID"),
            env.str("KEYCLOAK_CLIENT_SECRET"),
        )
        cls.driver.start()
        cls.driver.create_realm()
        cls.driver.create_realm_client()

        uh = UserHandler()
        cls.user_id = uh.create({"username": "testface", "email": "test@unikube.io"})

        super(ProjectTests, cls).setUpClass()

    def test_empty_projects_list(self):
        query = """
            query {
                allProjects {
                    results {
                        title
                    }
                }
            }
        """
        self.assertMatchSnapshot(self.client.execute(query, context=self.get_kc_permission_context([])))

    def generate_kc_permissions_for_resources(self, resources: Iterable[KeycloakResource]):
        token = {"authorization": {"permissions": []}}
        for resource in resources:
            scopes = resource.resource_handler().get_available_scopes(resource._meta.model_name)
            rsid = resource.id
            rsname = resource.get_keycloak_name()
            token["authorization"]["permissions"].append({"scopes": scopes, "rsid": str(rsid), "rsname": rsname})
        return token

    def generate_kc_permissions_for_dicts(self, resources: List[dict]):
        return KeycloakPermissions(resources)

    def get_kc_permission_context(self, resources):
        token = self.generate_kc_permissions_for_resources(resources)
        request = RequestFactory().get("/graphql")
        request.permissions = KeycloakPermissions(token["authorization"]["permissions"])
        return request

    def test_list_projects(self):
        ProjectFactory.reset_sequence()  # make sure to always start with 0
        n = 3
        projects = ProjectFactory.create_batch(n, title=factory.Sequence(lambda x: f"Blueshoe {x}"))

        query = """
            query {
                allProjects {
                    results {
                        title
                    }
                }
            }
        """
        result = self.client.execute(query, context=self.get_kc_permission_context(projects))
        self.assertMatchSnapshot(result)
        self.assertEqual(len(result["data"]["allProjects"]["results"]), n)

    def test_create_project(self):
        scopes = ["organization:projects:add"]
        organization_id = "3c11eb31-38c6-470d-b72d-52851fe90aa9"
        rsname = "organization(3c11eb31-38c6-470d-b72d-52851fe90aa9)"

        project_data = {
            "title": "Test",
            "description": "Some description",
            "specRepository": "https://github.com/Blueshoe/buzzword-charts",
            "specType": "helm",
            "accessToken": "",
            "accessUsername": "",
            "specRepositoryBranch": "master",
            "organization": organization_id,
        }
        query = """
            mutation($title: String!, $description: String!, $specRepository: String!, $specType: SpecicifactionTypeEnum!, $accessUsername: String, $accessToken: String, $specRepositoryBranch: String!, $organization: UUID!) {
                createUpdateProject( input: {title: $title, description: $description, specRepository: $specRepository, specType: $specType, specRepositoryBranch: $specRepositoryBranch, accessUsername: $accessUsername, accessToken: $accessToken, organization: $organization} ) {
                    project {
                        title,
                        description,
                        specRepository
                    }
                }
            }
        """
        request = RequestFactory().get("/graphql")
        request.permissions = self.generate_kc_permissions_for_dicts(
            [{"rsname": rsname, "scopes": scopes, "rsid": organization_id}]
        )
        request.kcuser = {"uuid": self.user_id}
        self.assertMatchSnapshot(
            self.client.execute(
                query,
                variables=project_data,
                context=request,
            )
        )

    def test_read_project(self):
        _uuid = "7afd77bd-87f2-4097-88ef-002d9d6a8e2c"
        project = ProjectFactory.create(id=_uuid, title="Blueshoe")
        query = """
            query($id: UUID) {
                project(id: $id) {
                    id
                    title
                }
            }
        """
        result = self.client.execute(
            query, variables={"id": str(project.id)}, context=self.get_kc_permission_context([project])
        )
        self.assertMatchSnapshot(result)

    def test_update_project(self):
        organization_id = "3c11eb31-38c6-470d-b72d-52851fe90aa9"

        project = ProjectFactory.create(title="Blueshoe", organization=organization_id)
        new_project_data = {
            "id": str(project.id),
            "title": "Unikube",
            "description": "Some description",
            "specRepository": "https://github.com/Blueshoe/buzzword-charts",
            "specType": "helm",
            "accessToken": "",
            "accessUsername": "",
            "specRepositoryBranch": "master",
            "organization": organization_id,
        }
        query = """
            mutation UpdateProject($title: String!, $description: String!, $specRepository: String!, $specType: SpecicifactionTypeEnum!, $accessUsername: String, $accessToken: String, $specRepositoryBranch: String!, $id: UUID!, $organization: UUID!) {
                createUpdateProject(input: {title: $title, description: $description, specRepository: $specRepository, specType: $specType, specRepositoryBranch: $specRepositoryBranch, accessUsername: $accessUsername, accessToken: $accessToken, organization: $organization, id: $id}) {
                    project {
                        title
                    }
                }
            }
        """
        request = self.get_kc_permission_context([project])
        request.kcuser = {"uuid": self.user_id}
        result = self.client.execute(query, variables=new_project_data, context=request)
        self.assertMatchSnapshot(result)

    def test_delete_project(self):
        project = ProjectFactory.create()
        query = """
            mutation( $id: UUID ) {
                deleteProject( id: $id ) {
                    ok
                }
            }
        """
        result = self.client.execute(
            query, variables={"id": str(project.id)}, context=self.get_kc_permission_context([project])
        )
        self.assertMatchSnapshot(result)

    @classmethod
    def tearDownClass(cls):
        cls.driver.stop()
