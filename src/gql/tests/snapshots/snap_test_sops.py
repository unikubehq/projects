# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["AWSSoapTests::test_create_sops 1"] = {"data": {"createUpdateSops": {"ok": True}}}

snapshots["AWSSoapTests::test_delete_sops 1"] = {"data": {"deleteSops": {"ok": True}}}

snapshots["AWSSoapTests::test_update_sops 1"] = {"data": {"createUpdateSops": {"ok": True}}}

snapshots["PGPSoapTests::test_create_sops 1"] = {"data": {"createUpdateSops": {"ok": True}}}

snapshots["PGPSoapTests::test_delete_sops 1"] = {"data": {"deleteSops": {"ok": True}}}

snapshots["PGPSoapTests::test_update_sops 1"] = {"data": {"createUpdateSops": {"ok": True}}}
