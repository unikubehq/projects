import factory


class ProjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = "projects.Project"
