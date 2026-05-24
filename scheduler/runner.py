# scheduler/runner.py
# Runs the pipeline job on a schedule.
# Default: every 30 minutes.
# During active alerts: every 5 minutes.

import schedule
import time
from datetime        import datetime, timezone
from config.settings import settings
from storage         import get_stats
from .job            import run_pipeline_job


def check_alert_mode() -> bool:
    """
    Returns True if there are active critical or high alerts
    in the database — triggers faster polling.
    """
    try:
        stats = get_stats()
        return (stats['critical'] + stats['high']) > 0
    except Exception:
        return False


def start_scheduler():
    """
    Starts the scheduler loop.
    - Runs pipeline every 30 minutes normally
    - Switches to every 5 minutes when high/critical alerts exist
    """
    print(f"\n[scheduler] Starting supply chain monitoring...")
    print(f"[scheduler] Default interval : every {settings.DEFAULT_POLL_INTERVAL_SECONDS // 60} minutes")
    print(f"[scheduler] Alert interval   : every {settings.ALERT_POLL_INTERVAL_SECONDS  // 60} minutes")

    # Run immediately on startup
    print(f"[scheduler] Running initial pipeline job...")
    run_pipeline_job()

    # Schedule regular runs
    schedule.every(settings.DEFAULT_POLL_INTERVAL_SECONDS).seconds.do(run_pipeline_job)

    alert_mode = False

    while True:
        try:
            # Check if we should switch to alert mode
            currently_alerting = check_alert_mode()

            if currently_alerting and not alert_mode:
                print(f"\n[scheduler] ⚠️  High/Critical alerts detected!")
                print(f"[scheduler] Switching to fast polling every "
                      f"{settings.ALERT_POLL_INTERVAL_SECONDS // 60} minutes")
                schedule.clear()
                schedule.every(settings.ALERT_POLL_INTERVAL_SECONDS).seconds.do(run_pipeline_job)
                alert_mode = True

            elif not currently_alerting and alert_mode:
                print(f"\n[scheduler] ✅ Alerts cleared.")
                print(f"[scheduler] Returning to normal polling every "
                      f"{settings.DEFAULT_POLL_INTERVAL_SECONDS // 60} minutes")
                schedule.clear()
                schedule.every(settings.DEFAULT_POLL_INTERVAL_SECONDS).seconds.do(run_pipeline_job)
                alert_mode = False

            schedule.run_pending()
            time.sleep(30)

        except KeyboardInterrupt:
            print(f"\n[scheduler] Stopped by user.")
            break
        except Exception as e:
            print(f"[scheduler] Error: {e}")
            time.sleep(30)
            continue