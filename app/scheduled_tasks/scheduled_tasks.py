from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .remove_old_tokens import remove_old_tokens


def start_scheduled_tasks():
    schedule = BackgroundScheduler(daemon=True)

    remove_old_tokens_trigger = CronTrigger(
        year="*", month="*", day="*", hour="1", minute="0", second="0"
    )
    schedule.add_job(
        remove_old_tokens,
        trigger=remove_old_tokens_trigger,
        name='daily remove old jwt tokens'
    )

    schedule.start()
