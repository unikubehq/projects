from commons.keycloak.testing.driver import KeycloakDriver
from commons.keycloak.users import UserHandler
from environs import Env

from projects.tests.factories.project import ProjectFactory


class SopsTestsMixin:
    SOPS_TYPE = None
    MODEL = None

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

        super(SopsTestsMixin, cls).setUpClass()

    @classmethod
    def get_sops_type(cls):
        if cls.SOPS_TYPE:
            return cls.SOPS_TYPE
        raise NotImplementedError

    @classmethod
    def get_model(cls):
        if cls.MODEL:
            return cls.MODEL
        raise NotImplementedError

    @classmethod
    def get_factory(cls):
        raise NotImplementedError

    def test_create_sops(self):
        project = ProjectFactory.create()
        sops_input = {
            "title": "Test",
            "description": "",
            "sopsType": self.get_sops_type(),
            "project": str(project.id),
            "secret1": "",
            "secret2": "",
            "secret3": "",
        }
        query = """
            mutation( $sopsData: SOPSInputType! ) {
                createUpdateSops( sopsData: $sopsData ) {
                    ok
                }
            }
        """
        result = self.client.execute(query, variables={"sopsData": sops_input})
        self.assertMatchSnapshot(result)
        model = self.get_model()
        self.assertTrue(model.objects.exists())

    def test_update_sops(self):
        new_title = "New title"
        factory = self.get_factory()
        obj = factory.create(title="Test")
        sops_input = {
            "title": new_title,
            "project": str(obj.project.id),
            "sopsType": self.get_sops_type(),
            "secret1": "",
            "secret2": "",
            "secret3": "",
        }
        query = """
            mutation( $sopsData: SOPSInputType!, $id: UUID ) {
                createUpdateSops( sopsData: $sopsData, id: $id ) {
                    ok
                }
            }
        """

        result = self.client.execute(query, variables={"sopsData": sops_input, "id": str(obj.id)})
        self.assertMatchSnapshot(result)

    def test_delete_sops(self):
        factory = self.get_factory()
        obj = factory.create()
        query = """
            mutation( $id: UUID! ) {
                deleteSops( id: $id ) {
                    ok
                }
            }
        """
        result = self.client.execute(query, variables={"id": str(obj.id)})
        self.assertMatchSnapshot(result)
        model = self.get_model()
        self.assertFalse(model.objects.exists())

    @classmethod
    def tearDownClass(cls):
        cls.driver.stop()
