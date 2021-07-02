import factory

from gql.tests import SnapshotGraphQLTestCase
from projects.tests.factories.project import ProjectFactory


class ProjectTests(SnapshotGraphQLTestCase):
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
        self.assertMatchSnapshot(self.client.execute(query))

    def test_list_projects(self):
        ProjectFactory.reset_sequence()  # make sure to always start with 0
        n = 3
        ProjectFactory.create_batch(n, title=factory.Sequence(lambda x: f"Blueshoe {x}"))
        query = """
            query {
                allProjects {
                    results {
                        title
                    }
                }
            }
        """
        result = self.client.execute(query)
        self.assertMatchSnapshot(result)
        self.assertEqual(len(result["data"]["allProjects"]["results"]), n)

    def test_create_project(self):
        project_data = {
            "title": "Test",
            "description": "Some description",
            "specRepository": "https://github.com/Blueshoe/buzzword-charts",
            "specType": "helm",
            "accessToken": "",
            "accessUsername": "",
            "specRepositoryBranch": "master",
        }
        query = """
            mutation($input: CreateUpdateProjectInput!) {
                createUpdateProject(input: $input) {
                    project {
                        title,
                        description,
                        specRepository
                    }
                }
            }
        """
        self.assertMatchSnapshot(
            self.client.execute(
                query,
                variables={"input": project_data},
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
        result = self.client.execute(query, variables={"id": str(project.id)})
        self.assertMatchSnapshot(result)

    def test_update_project(self):
        project = ProjectFactory.create(title="Blueshoe")
        new_project_data = {
            "id": str(project.id),
            "title": "Unikube",
            "description": "Some description",
            "specRepository": "https://github.com/Blueshoe/buzzword-charts",
            "specType": "helm",
            "accessToken": "",
            "accessUsername": "",
            "specRepositoryBranch": "master",
        }
        query = """
            mutation($input: CreateUpdateProjectInput!) {
                createUpdateProject( input: $input ) {
                    project {
                        title
                    }
                }
            }
        """
        result = self.client.execute(query, variables={"input": new_project_data})
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
        result = self.client.execute(query, variables={"id": str(project.id)})
        self.assertMatchSnapshot(result)
