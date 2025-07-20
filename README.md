# X-UI SubId Traffic Sync

This project provides a Python script designed to synchronize traffic usage for X-UI panel users based on their `subId`. It addresses synchronization issues in certain X-UI panel forks by directly interacting with the SQLite database, ensuring accurate traffic reporting across multiple client connections sharing the same `subId`.

## Features

-   **SubId-based Traffic Sync:** Automatically aggregates and updates traffic (upload and download) for all clients sharing the same `subId` to reflect the highest usage among them.
-   **Direct Database Interaction:** Bypasses potential API issues in some X-UI panel versions by directly reading from and writing to the `x-ui.db` SQLite database.
-   **Systemd Service:** Runs as a background service, ensuring the script starts automatically after server reboots and restarts if it crashes.
-   **Configurable Sync Interval:** Easily adjust the synchronization frequency.
-   **Easy Installation & Management:** A simple one-liner installation script and a dedicated command-line tool for service management.
-   **Minimal Resource Usage:** Optimized to minimize server resource consumption by only restarting X-UI when necessary.

## Prerequisites

Before installing, ensure your server meets the following requirements:

-   **Linux Operating System:** (e.g., Ubuntu, Debian, CentOS)
-   **Python 3:** Installed and accessible via `/usr/bin/python3`.
-   **X-UI Panel:** Must be installed and running (any fork, though this script is designed to work around issues in older/specific forks).
-   **`curl`:** For downloading the installation script.
-   **`systemd`:** For managing the background service.

## Installation

To install the X-UI SubId Traffic Sync service, run the following command as `root` (or with `sudo`):

```bash
sudo bash -c "$(curl -Ls https://raw.githubusercontent.com/Amirtrs/Multi_protocol_TX-ui/main/install.sh)" -- install
```
```bash
sudo wget -O /opt/xui_sync_script/install.sh https://raw.githubusercontent.com/Amirtrs/Multi_protocol_TX-ui/main/install.sh
```
## Usage

After installation, you can manage the service using the `xui-sync` command. Since the service operates with root privileges, prefix all commands with `sudo`.

### Check Service Status

To check whether the sync service is active and running properly:

```bash
sudo bash /opt/xui_sync_script/install.sh status
```


View Live Logs
To monitor the script's real-time activity and verify synchronization cycles:

```bash
sudo bash /opt/xui_sync_script/install.sh logs
```
Press Ctrl + C to exit the log stream.


Set Sync Interval
By default, the sync cycle runs every 25 seconds. You can adjust this interval as needed (value in seconds):

```bash
sudo bash /opt/xui_sync_script/install.sh set-interval 60
```

Start, Stop, and Restart Service
To start the service manually:

```bash
sudo bash /opt/xui_sync_script/install.sh start
sudo bash /opt/xui_sync_script/install.sh stop
sudo bash /opt/xui_sync_script/install.sh restart
```



Uninstallation
To remove the script and service completely:

```bash
sudo bash /opt/xui_sync_script/install.sh uninstall
```







