from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .remove_old_tokens import remove_old_tokens
from .sync_members import sync_members


def start_scheduled_tasks():
    schedule = BackgroundScheduler(daemon=True)

    # Daily task to remove old tokens
    remove_old_tokens_trigger = CronTrigger(
        year="*", month="*", day="*", hour="1", minute="0", second="0"
    )
    schedule.add_job(
        remove_old_tokens,
        trigger=remove_old_tokens_trigger,
        name='daily remove old jwt tokens'
    )

    # Run member sync every 15 minutes
    sync_members_trigger = CronTrigger(
        year="*", month="*", day="*", hour="*", minute="*/15", second="0"
    )
    schedule.add_job(
        sync_members,
        trigger=sync_members_trigger,
        name='sync members every 15 minutes'
    )

    schedule.start()