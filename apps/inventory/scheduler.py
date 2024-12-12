from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Schedule the `update_expired_inventory` command to run every 10 minutes
    scheduler.add_job(call_command, 'interval', minutes=10, args=['update_expired_inventory'])
    scheduler.start()
