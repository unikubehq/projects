import factory

from projects.tests.factories.project import ProjectFactory


class AWSKMSFactory(factory.DjangoModelFactory):
    class Meta:
        model = "sops.AWSKMS"

    project = factory.SubFactory(ProjectFactory)
