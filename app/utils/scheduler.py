from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerNotRunningError
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def check_meal_reminders(db):
    """
    This function checks pending meal reminders and triggers notifications if the reminder time has arrived.
    """
    logging.info("Checking meal reminders...")
    current_time = datetime.now()

    try:
        # Fetch all 'pending' reminders
        reminders = db.meal_reminders.find({"status": "pending"})

        # Process each reminder
        for reminder in reminders:
            # Ensure reminder_time is in datetime format
            reminder_time = datetime.strptime(reminder['reminder_time'], "%Y-%m-%dT%H:%M:%S")
            
            # Trigger the reminder if the time has arrived
            if reminder_time <= current_time:
                logging.info(f"Sending reminder for {reminder['meal']}: {reminder['reminder_message']}")
                
                # You would trigger your notification here (e.g., push notification, email, etc.)
                
                # Mark reminder as 'notified'
                db.meal_reminders.update_one(
                    {"_id": reminder['_id']},
                    {"$set": {"status": "notified"}}
                )
    except Exception as e:
        logging.error(f"Error while checking meal reminders: {str(e)}")


def start_scheduler(app, db):
    """
    Starts the background scheduler to check meal reminders every minute.
    """
    scheduler = BackgroundScheduler(executors={"default": ThreadPoolExecutor(10)})

    # Add the job to check meal reminders every minute
    scheduler.add_job(func=lambda: check_meal_reminders(db), trigger="interval", minutes=1)
    
    # Ensure the scheduler starts only once
    if not scheduler.running:
        scheduler.start()
        logging.info("Scheduler started.")
    
    # Shut down the scheduler when the app exits
    @app.teardown_appcontext
    def shutdown_scheduler(exc):
        """
        Shutdown the scheduler when the Flask app context is torn down.
        """
        if scheduler.running:
            try:
                scheduler.shutdown(wait=False)
                logging.info("Scheduler shut down.")
            except SchedulerNotRunningError:
                logging.warning("Scheduler was not running.")
