from gql.tests import SnapshotGraphQLTestCase


class ClusterSettingsTests(SnapshotGraphQLTestCase):
    def test_create_cluster_settings(self):
        # ClusterSettings should automatically created when project is created.
        pass

    def test_cluster_settings_port_same_organization(self):
        # Ports should not collide for ClusterSetting of different projects within the same organization
        pass

    def test_cluster_settings_port_different_organization(self):
        # Ports are allowed to collide for ClusterSetting of different projects between different organization
        pass

    def test_cluster_settings_update(self):
        # ClusterSettings can be updated via mutation
        pass

    def test_cluster_settings_invalid_port(self):
        # Only allow valid port ranges
        pass
