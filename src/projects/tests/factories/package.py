import factory

from projects.tests.factories.project import ProjectFactory


class DeckFactory(factory.DjangoModelFactory):
    class Meta:
        model = "projects.Deck"

    project = factory.SubFactory(ProjectFactory)
