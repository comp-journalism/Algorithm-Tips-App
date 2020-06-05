"""Initialize the cron settings to trigger jobs for each frequency.

The frequency level mappings are:

Weekly (every 7 days)
Semi-Weekly (every 10 days)
Monthly (every 30 days)

This script sets up cron triggers for each level.

Usage:
    setup-cron.py [options]

Options:
    -h --help           Show this screen.
    -u --undo           Remove cron commands
"""
from crontab import CronTab
from docopt import docopt
import re


def cmd(freq):
    return f'curl -X POST http://localhost/api/alert/trigger?frequency={freq} > /var/log/algotips/api_trigger_{freq}.log'


def setup_cron():
    with CronTab(True) as cron:
        weekly = cron.new(
            command=cmd('weekly'),
            comment='Weekly Alert Trigger'
        )
        weekly.dow.on('TUE')

        semi = cron.new(
            command=cmd('semi-weekly'),
            comment='Semi-Weekly Alert Trigger'
        )
        semi.day.every(10)

        monthly = cron.new(
            command=cmd('monthly'),
            comment='Monthly Alert Trigger'
        )
        monthly.dom.on(1)


def undo_cron():
    with CronTab(True) as cron:
        jobs = cron.find_comment(re.compile('.* Alert Trigger'))
        for job in jobs:
            cron.remove(job)


if __name__ == '__main__':
    args = docopt(__doc__)
    if args['--undo']:
        undo_cron()
    else:
        setup_cron()
