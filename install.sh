#!/bin/bash

# --- Installation Script Settings ---
# REPLACE THESE WITH YOUR GITHUB USERNAME AND REPO NAME
# Example: https://raw.githubusercontent.com/your-username/your-repo/main
REPO_URL="https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/main" 
INSTALL_DIR="/opt/xui_sync_script"
SERVICE_NAME="xui-subid-sync"
PYTHON_SCRIPT="sync_xui_traffic.py"
SETTINGS_FILE="settings.json"
SYSTEMD_SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# --- Functions ---

print_help() {
    echo "Usage: sudo bash $0 [install|uninstall|status|start|stop|restart|logs|set-interval]"
    echo ""
    echo "  install                  : Install the X-UI SubId Traffic Sync service."
    echo "  uninstall                : Uninstall the service."
    echo "  status                   : Check the service status."
    echo "  start                    : Start the service."
    echo "  stop                     : Stop the service."
    echo "  restart                  : Restart the service."
    echo "  logs                     : View service logs (live tail)."
    echo "  set-interval <seconds>   : Set the sync interval (e.g., set-interval 60 for 60 seconds)."
    echo ""
    exit 0
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo "This script must be run as root."
        exit 1
    fi
}

install_service() {
    check_root
    echo "Starting X-UI SubId Traffic Sync installation..."

    # 1. Create installation directory
    mkdir -p "$INSTALL_DIR"
    chmod 755 "$INSTALL_DIR"

    # 2. Download Python script
    echo "Downloading Python script..."
    curl -o "$INSTALL_DIR/$PYTHON_SCRIPT" "$REPO_URL/$PYTHON_SCRIPT"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to download Python script. Exiting."
        exit 1
    fi
    chmod 644 "$INSTALL_DIR/$PYTHON_SCRIPT" # Read-only for others

    # 3. Create initial settings file
    echo "Creating initial settings file..."
    DEFAULT_INTERVAL=25
    echo "{\"sleep_interval\": $DEFAULT_INTERVAL}" > "$INSTALL_DIR/$SETTINGS_FILE"
    chmod 644 "$INSTALL_DIR/$SETTINGS_FILE"

    # 4. Create Systemd service file
    echo "Creating Systemd service file..."
    cat <<EOF > "$SYSTEMD_SERVICE_FILE"
[Unit]
Description=X-UI SubId Traffic Sync Script
After=network.target multi-user.target x-ui.service

[Service]
ExecStart=/usr/bin/python3 ${INSTALL_DIR}/${PYTHON_SCRIPT}
WorkingDirectory=${INSTALL_DIR}/
Restart=always
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF
    chmod 644 "$SYSTEMD_SERVICE_FILE"

    # 5. Enable and start the service
    echo "Reloading Systemd daemon..."
    systemctl daemon-reload
    echo "Enabling service to start on boot..."
    systemctl enable "${SERVICE_NAME}.service"
    echo "Starting service now..."
    systemctl start "${SERVICE_NAME}.service"

    echo "Installation complete!"
    echo "You can check the service status with: sudo systemctl status ${SERVICE_NAME}.service"
    echo "You can view live logs with: sudo journalctl -u ${SERVICE_NAME}.service -f"
    echo "To set the sync interval: sudo xui-sync set-interval <seconds>"
    echo "Example: sudo xui-sync set-interval 60"

    # 6. Create a symlink for easy command access
    echo "Creating xui-sync command symlink..."
    ln -sf "$0" "/usr/local/bin/xui-sync"
    echo "You can now manage the service using 'sudo xui-sync' command."
}

uninstall_service() {
    check_root
    echo "Starting X-UI SubId Traffic Sync uninstallation..."

    echo "Stopping service..."
    systemctl stop "${SERVICE_NAME}.service"
    echo "Disabling service..."
    systemctl disable "${SERVICE_NAME}.service"
    echo "Removing Systemd service file..."
    rm -f "$SYSTEMD_SERVICE_FILE"
    echo "Reloading Systemd daemon..."
    systemctl daemon-reload

    echo "Removing installation directory..."
    rm -rf "$INSTALL_DIR"

    echo "Removing xui-sync command symlink..."
    rm -f "/usr/local/bin/xui-sync"

    echo "Uninstallation complete!"
}

set_interval() {
    check_root
    if [ -z "$1" ]; then
        echo "Error: Please provide the interval in seconds. Example: set-interval 60"
        exit 1
    fi
    INTERVAL=$1
    if ! [[ "$INTERVAL" =~ ^[0-9]+$ ]] || [ "$INTERVAL" -le 0 ]; then
        echo "Error: Interval must be a positive integer."
        exit 1
    fi

    echo "Setting sync interval to ${INTERVAL} seconds..."
    echo "{\"sleep_interval\": $INTERVAL}" > "$INSTALL_DIR/$SETTINGS_FILE"
    chmod 644 "$INSTALL_DIR/$SETTINGS_FILE"

    echo "Restarting service to apply new interval..."
    systemctl restart "${SERVICE_NAME}.service"
    echo "Interval set and service restarted."
}

# --- Script Execution Logic ---
case "$1" in
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    status)
        systemctl status "${SERVICE_NAME}.service"
        ;;
    start)
        check_root
        systemctl start "${SERVICE_NAME}.service"
        ;;
    stop)
        check_root
        systemctl stop "${SERVICE_NAME}.service"
        ;;
    restart)
        check_root
        systemctl restart "${SERVICE_NAME}.service"
        ;;
    logs)
        journalctl -u "${SERVICE_NAME}.service" -f --no-pager
        ;;
    set-interval)
        set_interval "$2"
        ;;
    *)
        print_help
        ;;
esac