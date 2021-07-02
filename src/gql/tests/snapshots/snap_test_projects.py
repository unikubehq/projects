# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["ProjectTests::test_create_project 1"] = {
    "data": {
        "createUpdateProject": {
            "project": {
                "description": "Some description",
                "specRepository": "https://github.com/Blueshoe/buzzword-charts",
                "title": "Test",
            }
        }
    }
}

snapshots["ProjectTests::test_delete_project 1"] = {"data": {"deleteProject": {"ok": True}}}

snapshots["ProjectTests::test_empty_projects_list 1"] = {"data": {"allProjects": {"results": []}}}

snapshots["ProjectTests::test_list_projects 1"] = {
    "data": {"allProjects": {"results": [{"title": "Blueshoe 0"}, {"title": "Blueshoe 1"}, {"title": "Blueshoe 2"}]}}
}

snapshots["ProjectTests::test_read_project 1"] = {
    "data": {"project": {"id": "7afd77bd-87f2-4097-88ef-002d9d6a8e2c", "title": "Blueshoe"}}
}

snapshots["ProjectTests::test_update_project 1"] = {"data": {"createUpdateProject": {"project": {"title": "Unikube"}}}}
