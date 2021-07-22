import logging

from configuration.celery import app
from projects.models import Project, RepositoryStatus
from projects.utils.project import ProjectUpdater

logger = logging.getLogger("projects.celery")


@app.task(bind=True, default_retry_delay=5, max_retries=3)
def update_repository_information(self, project_id, deck_ids=None, render=False):
    project = Project.objects.get(id=project_id)
    project.current_commit = ""
    project.current_commit_date_time = None
    project.repository_status = RepositoryStatus.CLONING
    project.save()
    if deck_ids:
        decks = project.decks.filter(pk__in=deck_ids)
    else:
        decks_with_env = project.decks.filter(environments__isnull=False)
        if decks_with_env.exists():
            updater = ProjectUpdater(project, decks_with_env, render_charts=True)
            updater.update()
        decks = None
    updater = ProjectUpdater(project, decks, render_charts=render)
    updater.update()
