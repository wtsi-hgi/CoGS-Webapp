from datetime import timedelta, datetime

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db_helper import get_most_recent_group
from scheduling.deadlines import deadline_scheduler


def setup(app):
    jobstore = SQLAlchemyJobStore(engine=app["db"])
    jobstores = {"default": jobstore}
    scheduler = AsyncIOScheduler(jobstores=jobstores)

    scheduler.start()
    scheduler.print_jobs()
    app["scheduler"] = scheduler
    # TODO: Remove
    scheduler.remove_all_jobs()
    deadlines.schedule_deadline(app, get_most_recent_group(app["session"]), "supervisor_submit", datetime.now()+timedelta(seconds=15))
