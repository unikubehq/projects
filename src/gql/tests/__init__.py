from graphene.test import Client
from snapshottest.django import TestCase

from gql import schema


class SnapshotGraphQLTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client(schema.schema)
