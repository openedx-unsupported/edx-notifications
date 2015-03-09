"""
Defines the abstract interface for a class that can handle
a callback when the timer expires
"""

import logging
import pytz
import copy
from datetime import datetime, timedelta

from importlib import import_module

from edx_notifications.stores.store import notification_store
from edx_notifications import const

log = logging.getLogger(__name__)


def poll_and_execute_timers():
    """
    Will look in our registry of timers and see which should be executed now. It is not
    advised to call this method on any webservers that are serving HTTP traffic as
    this can take an arbitrary amount of time
    """

    log.info('Starting poll_and_execute_timers()...')
    store = notification_store()

    timers_not_executed = store.get_all_active_timers()

    for timer in timers_not_executed:
        log.info('Executing timer: {timer}...'.format(timer=str(timer)))

        timer.executed_at = datetime.now(pytz.UTC)
        store.save_notification_timer(timer)

        try:
            module_path, _, name = timer.class_name.rpartition('.')
            log.info('Creating TimerCallback at class_name "{class_name}"'.format(class_name=timer.class_name))

            class_ = getattr(import_module(module_path), name)
            handler = class_()

            results = handler.notification_timer_callback(timer)

            # store a copy of the results in the database record
            # for the timer
            timer.results = copy.deepcopy(results)

            if not results.get('errors'):
                # successful, see if we should reschedule
                rerun_delta = results.get('reschedule_in_mins')
                rerun_delta = rerun_delta if rerun_delta else timer.periodicity_min

                if rerun_delta:
                    min_delta = const.NOTIFICATION_MINIMUM_PERIODICITY_MINS
                    rerun_delta = rerun_delta if rerun_delta >= min_delta else min_delta

                    timer.callback_at = timer.callback_at + timedelta(minutes=rerun_delta)
                    timer.executed_at = None  # need to reset this or it won't get picked up again
            else:
                timer.err_msg = str(results['errors'])

            store.save_notification_timer(timer)
        except Exception, ex:  # pylint: disable=broad-except
            # generic error (possibly couldn't create class_name instance?)
            timer.err_msg = str(ex)
            timer.is_active = False
            store.save_notification_timer(timer)

            log.exception(ex)

    log.info('Ending poll_and_execute_timers()...')
