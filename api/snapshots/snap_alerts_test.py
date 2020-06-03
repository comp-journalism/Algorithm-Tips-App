# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_alert_render 1'] = '''<!DOCTYPE html>
<html>

<body>
    <p>New leads matching your alert have been added to the <a href="http://db.algorithmtips.org/">AlgorithmTips
            Database</a>.</p>
    <p>
    <table>
        <thead>
            <tr>
                <th colspan="2" style="font-variant: small-caps">Alert Details</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Filter:</td>
                <td><em>None</em></td>
            </tr>
            <tr>
                <td>Sources:</td>
                <td>Federal Agency - Executive, No Regional, Any Local</td>
            </tr>
        </tbody>
    </table>
    <table>
        <thead>
            <tr>
                <th style="font-variant: small-caps">Selected Leads</th>
            </tr>
        </thead>
        <tbody>
            
            <tr>
                <td><a href="http://db.algorithmtips.org/lead/6933">FEMA&#39;s Climate Impact Model</a></td>
            </tr>
            
        </tbody>
    </table>
    </p>
    <p>
        Click <a href="http://db.algorithmtips.org/alert?token=MQ.w-J-fKwgPT3AIxF7etDyRq_kcGY">here</a> to see all 1 new leads.
    </p>
    <p style="font-size:small;">
        <em><a href="http://db.algorithmtips.org/delete-alert?token=eyJ1c2VyIjoxLCJzZW5kIjoxfQ.c1W0brRrBzXYLL2Euk8RHAHIPzo">Delete This Alert</a> &middot; <a href="http://db.algorithmtips.org/unsubscribe?token=eyJ1c2VyIjoxLCJzZW5kIjoxfQ.c1W0brRrBzXYLL2Euk8RHAHIPzo">Unsubscribe
                From All Alerts</a> &middot; <a href="http://algorithmtips.org/about/">Contact</a></em>
    </p>
    <p style="font-size:small;">
        <em>You are receiving this email because you signed up for an alert from the AlgorithmTips Database. If this was
            done in error, click <a href="http://db.algorithmtips.org/unsubscribe?token=eyJ1c2VyIjoxLCJzZW5kIjoxfQ.c1W0brRrBzXYLL2Euk8RHAHIPzo">here</a> to remove yourself from the database and
            prevent future
            emails.</em>
    </p>
</body>

</html>'''

snapshots['test_alert_render 2'] = '''New leads matching your alert have been added to the AlgorithmTips Database at http://db.algorithmtips.org/.

Click here to see all 1 new leads: http://db.algorithmtips.org/alert?token=MQ.w-J-fKwgPT3AIxF7etDyRq_kcGY

Delete This Alert: http://db.algorithmtips.org/delete-alert?token=eyJ1c2VyIjoxLCJzZW5kIjoxfQ.c1W0brRrBzXYLL2Euk8RHAHIPzo
Unsubscribe From All Alerts: http://db.algorithmtips.org/unsubscribe?token=eyJ1c2VyIjoxLCJzZW5kIjoxfQ.c1W0brRrBzXYLL2Euk8RHAHIPzo
Contact: http://algorithmtips.org/about/'''
