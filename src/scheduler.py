import os
import sys
import time
import subprocess

LOCK_FILE = "data/ingestion.lock"

def run_pipeline():
    if os.path.exists(LOCK_FILE):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ingestion task is already running (lock file found). Skipping duplicate run.")
        return
    
    # Create lock file
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
        
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting daily ingestion task...")
    try:
        # Run ingestion run module
        result = subprocess.run([sys.executable, "-m", "src.ingestion.run"], check=True)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Daily ingestion completed successfully.")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error running ingestion pipeline: {e}", file=sys.stderr)
    finally:
        # Remove lock file
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)

import datetime

def sleep_until_target_time(target_hour=10, target_minute=30):
    now = datetime.datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    # If the target time is in the past for today, schedule it for tomorrow
    if target_time <= now:
        target_time += datetime.timedelta(days=1)
        
    delta_seconds = (target_time - now).total_seconds()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Next scheduled run is at {target_time.strftime('%Y-%m-%d %H:%M:%S')} (local time). Sleeping for {delta_seconds:.0f} seconds...")
    time.sleep(delta_seconds)

def main():
    print("Mutual Fund FAQ Bot Scheduler initialized.")
    print("Scheduling ingestion pipeline to run at 10:30 AM local time every day...")
    
    while True:
        sleep_until_target_time(10, 30)
        run_pipeline()

if __name__ == "__main__":
    main()
