from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.etl.run_world_bank import run_world_bank_etl


def start_etl_scheduler() -> BackgroundScheduler | None:
    if not settings.etl_scheduler_enabled:
        return None

    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        func=run_world_bank_etl,
        trigger=CronTrigger.from_crontab(settings.etl_schedule_cron),
        id="global_debt_multisource",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler


def stop_etl_scheduler(scheduler: BackgroundScheduler | None) -> None:
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
