import factory

from projects.tests.factories.project import ProjectFactory


class PGPKeyFactory(factory.DjangoModelFactory):
    class Meta:
        model = "sops.PGPKey"

    project = factory.SubFactory(ProjectFactory)
