from gql.tests import SnapshotGraphQLTestCase
from projects.models import Environment
from projects.tests.factories.deck import DeckFactory
from projects.tests.factories.environment import EnvironmentFactory


class EnvironmentTests(SnapshotGraphQLTestCase):
    def test_create_environment(self):
        environment_title = "Test"
        environment_type = Environment.TYPE_CHOICES[0][0]
        deck = DeckFactory.create()
        environment_input = {
            "title": environment_title,
            "description": "",
            "type": environment_type,
            "deck": str(deck.id),
            "sopsCredentials": "",
            "valuesType": "",
        }
        query = """
            mutation( $input: CreateUpdateEnvironmentInput! ) {
                createUpdateEnvironment( input: $input ) {
                    environment {
                        title
                    }
                }
            }
        """
        result = self.client.execute(query, variables={"input": environment_input})
        self.assertMatchSnapshot(result)

    def test_update_environment(self):
        new_title = "New Title"
        environment_type = Environment.TYPE_CHOICES[0][0]
        obj = EnvironmentFactory.create(title="Title")
        environment_input = {
            "id": str(obj.id),
            "title": new_title,
            "description": "",
            "type": environment_type,
            "deck": str(obj.deck.id),
            "sopsCredentials": "",
            "valuesType": "",
        }
        query = """
            mutation( $input: CreateUpdateEnvironmentInput! ) {
                createUpdateEnvironment( input: $input ) {
                    environment {
                        title
                    }
                }
            }
        """
        result = self.client.execute(query, variables={"input": environment_input})
        self.assertMatchSnapshot(result)

    def test_delete_environment(self):
        obj = EnvironmentFactory.create()
        query = """
            mutation( $id: UUID! ) {
                deleteEnvironment( id: $id ) {
                    ok
                }
            }
        """
        result = self.client.execute(query, variables={"id": str(obj.id)})
        self.assertMatchSnapshot(result)
