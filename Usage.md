# X-UI SubId Traffic Sync - Usage Guide

This document provides detailed instructions for managing the X-UI SubId Traffic Sync service after it has been installed using the `install.sh` script.

The primary command for interacting with the service is `xui-sync`. Since the service runs with `root` privileges, you must use `sudo` before `xui-sync` for all management commands.

---

## 1. Check Service Status

Use this command to verify if the X-UI SubId Traffic Sync service is running, active, or if it has encountered any issues.

```bash
sudo xui-sync status

Expected Output (if running successfully):
● xui-subid-sync.service - X-UI SubId Traffic Sync Script
     Loaded: loaded (/etc/systemd/system/xui-subid-sync.service; enabled; vendor preset: enabled)
     Active: active (running) since <TIMESTAMP>; <TIME_AGO>
   Main PID: <PID> (python3)
      Tasks: <NUMBER> (limit: ...)
     Memory: <USAGE>
        CPU: <USAGE>
     CGroup: /system.slice/xui-subid-sync.service
             └─<PID> /usr/bin/python3 /opt/xui_sync_script/sync_xui_traffic.py
# ... (Recent log lines from the service)


2. View Live Logs
To monitor the script's real-time activity, check for errors, or observe the synchronization process, use the logs command. This will display the latest log entries and stream new ones as they occur.

To exit the live log view, press Ctrl+C.

Bash

sudo xui-sync logs
Expected Output (example lines):

--- Starting sync cycle ---
Syncing subId=your_sub_id_1 | UP=1234567890 DOWN=9876543210
Inbound 1 needs database update.
Updated 2 client traffic records in DB.
Updated 1 inbound records in DB.
Done processing data.
Restarting x-ui service to apply changes...
x-ui service restarted successfully.
Sync cycle finished. Waiting for 25 seconds...
--- Starting sync cycle ---
# ... (new log entries will appear here)
3. Set Sync Interval
You can easily adjust the frequency at which the script runs its synchronization cycle. The interval is specified in seconds.

The default interval is 25 seconds.

Example: To set the synchronization interval to 60 seconds:

Bash

sudo xui-sync set-interval 60
After changing the interval, the service will automatically restart to apply the new setting.

Expected Output:

Setting sync interval to 60 seconds...
Restarting service to apply new interval...
x-ui service restarted successfully.
Interval set and service restarted.
4. Start the Service
If the service is currently stopped, you can manually start it using this command.

Bash

sudo xui-sync start
Expected Output (if successful):

# No direct output, check status for confirmation: sudo xui-sync status
5. Stop the Service
To temporarily halt the synchronization process, you can stop the service.

Bash

sudo xui-sync stop
Expected Output (if successful):

# No direct output, check status for confirmation: sudo xui-sync status
6. Restart the Service
If you've made manual changes to the script files (though not recommended unless you know what you're doing) or just want to force a refresh, you can restart the service. This will also be automatically done after changing the sync interval.

Bash

sudo xui-sync restart
Expected Output (if successful):

# No direct output, check status for confirmation: sudo xui-sync status
7. Uninstall the Service
If you no longer need the X-UI SubId Traffic Sync service, you can completely remove it from your system using the uninstall command.

Bash

sudo xui-sync uninstall
Expected Output (example):

Starting X-UI SubId Traffic Sync uninstallation...
Stopping service...
Disabled service.
Removing Systemd service file...
Reloading Systemd daemon...
Removing installation directory...
Removing xui-sync command symlink...
Uninstallation complete!
