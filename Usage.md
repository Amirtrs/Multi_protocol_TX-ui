# X-UI SubId Traffic Sync - Usage Guide

This document provides detailed instructions for managing the X-UI SubId Traffic Sync service after it has been installed using the `install.sh` script.

The primary command for interacting with the service is `xui-sync`. Since the service runs with `root` privileges, you must use `sudo` before `xui-sync` for all management commands.

---

## 1. Check Service Status

Use this command to verify if the X-UI SubId Traffic Sync service is running, active, or if it has encountered any issues.

```bash
sudo xui-sync status
Example Output (if running successfully):
yaml
Copy
Edit
● xui-subid-sync.service - X-UI SubId Traffic Sync Script
     Loaded: loaded (/etc/systemd/system/xui-subid-sync.service; enabled; vendor preset: enabled)
     Active: active (running) since <TIMESTAMP>; <TIME_AGO>
   Main PID: <PID> (python3)
      Tasks: <NUMBER> (limit: ...)
     Memory: <USAGE>
        CPU: <USAGE>
     CGroup: /system.slice/xui-subid-sync.service
             └─<PID> /usr/bin/python3 /opt/xui_sync_script/sync_xui_traffic.py
```
2. View Live Logs
To monitor the script's real-time activity, check for errors, or observe the synchronization process, use the following command:

bash
Copy
Edit
sudo xui-sync logs
Press Ctrl+C to exit the live log view.

Example Output:

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




3. Set Sync Interval
You can adjust the frequency at which the script runs its synchronization cycle. The interval is specified in seconds.

Default interval: 25 seconds

Example: To set the synchronization interval to 60 seconds:

sudo xui-sync set-interval 60
Example Output:
Setting sync interval to 60 seconds...
Restarting service to apply new interval...
x-ui service restarted successfully.
Interval set and service restarted.


4. Start the Service
If the service is currently stopped, you can manually start it using:


sudo xui-sync start


5. Stop the Service
To temporarily halt the synchronization process, run:


sudo xui-sync stop


6. Restart the Service
If you've made manual changes to the script files (not recommended unless you know what you're doing) or want to force a refresh, use:


sudo xui-sync restart

This will also happen automatically after changing the sync interval.
