import logging
from typing import List

import yaml
from commons.helm.data_classes import DeckData, RenderEnvironment
from commons.helm.exceptions import RepositoryAuthenticationFailed, RepositoryBranchUnavailable, RepositoryCloningFailed
from commons.helm.parser import HelmRepositoryParser
from django.db.models import QuerySet

from projects.models import Environment, K8SDeployment, RepositoryStatus

logger = logging.getLogger("projects.updater")


class ProjectUpdater:
    def __init__(self, project, decks: QuerySet = None, render_charts=False):
        self.project = project
        self.updating_decks = decks
        self.render_charts = render_charts

    def update(self):
        from projects.models import RepositoryStatus

        try:
            self._update()
        except Exception:
            logger.error(f"Could not update repo information for project {self.project.pk}.", exc_info=True)
            self.project.repository_status = RepositoryStatus.UNKNOWN
            self.project.save()

    def _update(self):
        project = self.project
        if project.spec_type == "helm":
            parser = HelmRepositoryParser(
                repository_url=project.spec_repository,
                access_username=project.access_username,
                access_token=project.access_token,
                branch=project.spec_repository_branch,
            )
        else:
            logger.warning("Repository Spec Type is currently not supported.")
            return

        try:
            parser.parse()
        except RepositoryBranchUnavailable:
            logger.error(f"Could not update repo information for project {project.pk}.", exc_info=True)
            project.repository_status = RepositoryStatus.BRANCH_UNAVAILABLE
            project.save()
            return
        except RepositoryAuthenticationFailed:
            project.repository_status = RepositoryStatus.AUTH_FAILED
            project.save()
            return
        except RepositoryCloningFailed:
            project.repository_status = RepositoryStatus.CLONING_FAILED
            project.save()
            return
        except Exception:
            logger.error(f"Could not parse repository for project {project.pk}.", exc_info=True)
            project.repository_status = RepositoryStatus.PARSING_FAILED
            project.save()
            return

        project.current_commit = parser.repository_data.current_commit
        project.current_commit_date_time = parser.repository_data.current_commit_date_time
        project.repository_status = RepositoryStatus.CLONING_SUCCESSFUL
        project.save()
        if self.updating_decks:
            # there is a limited deck update requested
            req_decks = []
            for available_deck in parser.deck_data:
                if self.updating_decks.filter(hash=available_deck.hash).exists():
                    req_decks.append(available_deck)
            decks_data = self.enrich_decks_data(req_decks)
        else:
            decks_data = self.enrich_decks_data(parser.deck_data)
            self.delete_stale_decks(exclude_these=decks_data)

        if self.render_charts:
            render_list = [(deck, env) for deck in decks_data for env in deck.environments]
            updated_decks = parser.render(*render_list)
            for deck, environment in updated_decks:
                level = Environment.objects.get(id=environment.id)
                self._update_deployments(level, environment)

    def enrich_decks_data(self, decks_data: List[DeckData]):
        from projects.models import Deck

        for deck_data in decks_data:
            deck, created = Deck.objects.update_or_create(  # maybe update or create
                project=self.project,
                hash=deck_data.hash,
                defaults={
                    "title": deck_data.title,
                    "description": deck_data.description,
                    "dir_path": deck_data.dir_path,
                    "type": deck_data.type,
                    "file_information": deck_data.file_information,
                },
            )

            if created:
                environment = Environment.create_initial_environment(deck)
                environments = [environment]
            else:
                deck.update_environments(deck_data)
                environments = deck.environments.all()

            for level in environments:
                environment = RenderEnvironment(values_path=level.values_path, specs_data=[])
                environment.id = level.id
                deck_data.environments.append(environment)

        return decks_data

    def delete_stale_decks(self, exclude_these):
        deck_hashes = [deck.hash for deck in exclude_these]
        stale_decks = self.project.decks.exclude(hash__in=deck_hashes)
        if stale_decks:
            logger.info(f"Deleting stale decks for project {self.project.pk}.")
            stale_decks.delete()

    def _update_deployments(self, environment: Environment, render_env: RenderEnvironment):
        environment.deployments.all().delete()
        for spec_data in render_env.specs_data:
            if spec_data.kind == "Deployment":
                content = yaml.load(spec_data.content, Loader=yaml.FullLoader)
                try:
                    title = content["metadata"]["name"]
                except (KeyError, TypeError):
                    title = spec_data.name
                ports = self._get_ports(content)
                K8SDeployment.objects.update_or_create(
                    environment=environment, title=title, is_switchable=False, ports=",".join(ports)
                )

    def _get_ports(self, content):
        ports = set()
        try:
            for container in content["spec"]["template"]["spec"]["containers"]:
                if "containerPort" in container:
                    ports.add(str(container["containerPort"]))
                elif "ports" in container:
                    for port in container["ports"]:
                        ports.add(str(port["containerPort"]))
        except KeyError:
            pass
        return list(ports)
