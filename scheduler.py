import schedule
import time

def run_scheduler():
    print(" * Scheduler working correctly")
    while True:
        schedule.run_pending()
        time.sleep(1)