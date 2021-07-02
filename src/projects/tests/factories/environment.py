import factory

from projects.tests.factories.deck import DeckFactory


class EnvironmentFactory(factory.DjangoModelFactory):
    class Meta:
        model = "projects.Environment"

    deck = factory.SubFactory(DeckFactory)
