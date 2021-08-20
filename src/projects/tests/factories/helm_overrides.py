import factory

from projects.tests.factories.environment import EnvironmentFactory


class HelmOverridesFactory(factory.DjangoModelFactory):
    class Meta:
        model = "projects.HelmOverrides"

    environment = factory.SubFactory(EnvironmentFactory)
