# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["EnvironmentTests::test_create_environment 1"] = {
    "data": {"createUpdateEnvironment": {"environment": {"title": "Test"}}}
}

snapshots["EnvironmentTests::test_delete_environment 1"] = {"data": {"deleteEnvironment": {"ok": True}}}

snapshots["EnvironmentTests::test_update_environment 1"] = {
    "data": {"createUpdateEnvironment": {"environment": {"title": "New Title"}}}
}
