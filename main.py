from school_manager.modules.web_server import WebServer
from school_manager.db import initialize_db
from flask_apscheduler import APScheduler


def schedule_periodic_reception():
    from school_manager.models.periodic_reception import PeriodicReception
    try:
        PeriodicReception.create_income_from_periodic_reception()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    print("Social School Manager")
    initialize_db.init_db()

    # TODO: To check before uncomment these lines ( משימת יציבות )-->
    # schedule tasks - for periodic reception
    #scheduler = APScheduler()
    #scheduler.add_job(id='Scheduled Task', func=schedule_periodic_reception, trigger="cron",
    #                  day='*', hour=0, minute=0)
    #scheduler.start()

    WebServer.start_web_server()
