# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_alert_db_link 1'] = 'http://db.algorithmtips.org/db?regional=exclude&local=exclude&from=2020-05-28&to=2020-06-04'
