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


