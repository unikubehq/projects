from typing import Iterable

from commons.keycloak.abstract_models import KeycloakResource
from commons.keycloak.permissions import KeycloakPermissions
from commons.keycloak.testing.driver import KeycloakDriver
from commons.keycloak.users import UserHandler
from django.test import RequestFactory
from environs import Env

from gql.tests import SnapshotGraphQLTestCase
from projects.tests.factories.environment import EnvironmentFactory
from projects.tests.factories.helm_overrides import HelmOverridesFactory


class HelmOverridesTests(SnapshotGraphQLTestCase):
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

        super(HelmOverridesTests, cls).setUpClass()

    def generate_kc_permissions_for_resources(self, resources: Iterable[KeycloakResource]):
        token = {"authorization": {"permissions": []}}
        for resource in resources:
            scopes = resource.resource_handler().get_available_scopes(resource._meta.model_name)
            rsid = resource.id
            rsname = resource.get_keycloak_name()
            token["authorization"]["permissions"].append({"scopes": scopes, "rsid": str(rsid), "rsname": rsname})
        return token

    def get_kc_permission_context(self, resources):
        token = self.generate_kc_permissions_for_resources(resources)
        request = RequestFactory().get("/graphql")
        request.permissions = KeycloakPermissions(token["authorization"]["permissions"])
        return request

    def test_create_helm_overrides(self):
        obj = EnvironmentFactory.create(title="Title")
        query = """
            mutation( $environmentId: UUID!, $overrides: String! ) {
                createUpdateHelmOverrides(environmentId: $environmentId, overrides: $overrides) {
                    ok
                }
            }
        """
        request = self.get_kc_permission_context([obj.deck.project])
        request.kcuser = {"uuid": self.user_id}
        result = self.client.execute(
            query,
            variables={"environmentId": str(obj.id), "overrides": "test: 1"},
            context=request,
        )
        self.assertMatchSnapshot(result)

    def test_query_helm_overrides(self):
        obj = HelmOverridesFactory.create()
        project_id = obj.environment.deck.project_id
        query = """
            query ProjectDetailQuery($id: UUID) {
              project(id: $id) {
                id
                decks {
                  id
                  environment {
                    id
                    helmOverrides {
                      overrides
                    }
                  }
                }
              }
            }
        """
        result = self.client.execute(query, variables={"id": project_id})
        self.assertMatchSnapshot(result)

    @classmethod
    def tearDownClass(cls):
        cls.driver.stop()
