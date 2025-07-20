import sqlite3
import json
import os
import time
import subprocess
from collections import defaultdict

# --- Configuration ---
DB_PATH = "/etc/x-ui/x-ui.db"
LOCAL_DB_FILE = "/opt/xui_sync_script/localDB.json"
DEFAULT_SLEEP_SECONDS = 25 
DB_TIMEOUT = 5

# --- Database Helper Functions ---

def connect_db():
    """Connects to the SQLite database in read-write mode."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to DB: {e}")
        return None

def fetch_all_inbounds(conn):
    """Reads all inbounds from the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, settings, protocol FROM inbounds")
    rows = cursor.fetchall()
    return [{"id": row[0], "settings": row[1], "protocol": row[2]} for row in rows]

def fetch_all_client_traffics(conn):
    """Reads all client traffic data from the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT email, up, down, total, expiry_time, enable, inbound_id, reset FROM client_traffics")
    rows = cursor.fetchall()
    return [{"Email": row[0], "Up": row[1], "Down": row[2], "Total": row[3],
             "Expiry_Time": row[4], "Enable": bool(row[5]), "Inbound_Id": row[6], "Reset": row[7]}
            for row in rows]

def update_client_traffics_in_db(conn, updated_traffics):
    """Updates client traffic records in the client_traffics table."""
    cursor = conn.cursor()
    updates = [(t["Up"], t["Down"], t["Total"], t["Expiry_Time"], int(t["Enable"]), t["Reset"], t["Inbound_Id"], t["Email"]) for t in updated_traffics]
    cursor.executemany("""
        UPDATE client_traffics
        SET up = ?, down = ?, total = ?, expiry_time = ?, enable = ?, reset = ?, inbound_id = ?
        WHERE email = ?
    """, updates)
    conn.commit()
    print(f"Updated {len(updates)} client traffic records in DB.")

def update_inbounds_in_db(conn, updated_inbounds):
    """Updates inbound records in the inbounds table."""
    cursor = conn.cursor()
    updates = [(ib['settings'], ib['id']) for ib in updated_inbounds]
    cursor.executemany("UPDATE inbounds SET settings = ? WHERE id = ?", updates)
    conn.commit()
    print(f"Updated {len(updates)} inbound records in DB.")

def restart_xui_service():
    """
    Restarts the x-ui service to apply database changes.
    This function requires root privileges.
    """
    print("Restarting x-ui service to apply changes...")
    try:
        result = subprocess.run(['sudo', 'systemctl', 'restart', 'x-ui.service'], 
                                capture_output=True, text=True, check=True)
        print("x-ui service restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error restarting x-ui service: {e.stderr}")
    except FileNotFoundError:
        print("Command 'systemctl' not found. Ensure systemd is installed.")
    except Exception as e:
        print(f"Unknown error restarting x-ui service: {e}")

# --- Core Logic Functions ---

def load_local_usage():
    """
    Loads previous traffic data from the local file.
    Creates an initial structure if the file does not exist or is corrupted.
    """
    if os.path.exists(LOCAL_DB_FILE):
        try:
            with open(LOCAL_DB_FILE, 'r') as f:
                data = json.load(f)
                if "clients" not in data or not isinstance(data["clients"], list):
                    data["clients"] = []
                if "sec" not in data or not isinstance(data["sec"], (int, float)):
                    data["sec"] = DEFAULT_SLEEP_SECONDS 
                return data
        except json.JSONDecodeError as e:
            print(f"Error reading JSON from {LOCAL_DB_FILE}: {e}. Creating new file.")
            return {"clients": [], "sec": DEFAULT_SLEEP_SECONDS}
    print(f"File {LOCAL_DB_FILE} not found. Creating a new file with initial values.")
    return {"clients": [], "sec": DEFAULT_SLEEP_SECONDS}

def save_local_usage(data):
    """Saves current traffic data to the local file."""
    try:
        os.makedirs(os.path.dirname(LOCAL_DB_FILE), exist_ok=True)
        with open(LOCAL_DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving to {LOCAL_DB_FILE}: {e}")

def get_sleep_interval():
    """Reads the SLEEP_SECONDS value from the settings file."""
    settings_file = "/opt/xui_sync_script/settings.json"
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                if "sleep_interval" in settings and isinstance(settings["sleep_interval"], (int, float)):
                    return settings["sleep_interval"]
        except json.JSONDecodeError:
            pass
    return DEFAULT_SLEEP_SECONDS

def process_and_sync_data():
    conn = connect_db()
    if not conn:
        return

    changes_made_to_inbounds = False

    try:
        db_client_traffics = fetch_all_client_traffics(conn)
        local_data = load_local_usage()
        inbounds_from_db = fetch_all_inbounds(conn)
        
        all_clients_from_inbounds = []
        inbounds_dict = {ib['id']: ib for ib in inbounds_from_db}

        for inbound_item in inbounds_from_db:
            if inbound_item["protocol"] in ["vmess", "vless"]:
                settings_str = inbound_item.get("settings")
                if settings_str:
                    try:
                        settings = json.loads(settings_str)
                        if "clients" in settings and isinstance(settings["clients"], list):
                            for client in settings["clients"]:
                                client_copy = client.copy()
                                client_copy["inbound_id"] = inbound_item["id"]
                                all_clients_from_inbounds.append(client_copy)
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error for Inbound {inbound_item['id']} settings: {e}")
                
        final_clients_to_update = []
        final_client_traffic_records_to_update = []
        
        local_clients_map = {c["Email"]: c for c in local_data["clients"]}

        grouped_by_subid = defaultdict(list)
        for client in all_clients_from_inbounds:
            if "subId" in client and client["subId"]:
                grouped_by_subid[client["subId"]].append(client)

        for subid, clients_in_group in grouped_by_subid.items():
            matching_traffics_db = [t for t in db_client_traffics if t["Email"] in [c["email"] for c in clients_in_group]]
            
            if not matching_traffics_db:
                continue

            max_up_db = max(t.get("Up", 0) for t in matching_traffics_db)
            max_down_db = max(t.get("Down", 0) for t in matching_traffics_db)
            max_total_db = max(t.get("Total", 0) for t in matching_traffics_db)

            expiry_times = [t.get("Expiry_Time", 0) for t in matching_traffics_db if t.get("Expiry_Time") is not None]
            expiry_time = 0
            if any(et > 0 for et in expiry_times):
                expiry_time = max(et for et in expiry_times if et > 0)
            elif any(et < 0 for et in expiry_times):
                expiry_time = min(et for et in expiry_times if et < 0)

            delta_up = 0
            delta_down = 0

            for client_db_traffic in matching_traffics_db:
                old_local_client = local_clients_map.get(client_db_traffic["Email"])
                if old_local_client:
                    old_up = old_local_client.get("Up", 0)
                    old_down = old_local_client.get("Down", 0)
                    
                    if client_db_traffic["Up"] > old_up:
                        delta_up += (client_db_traffic["Up"] - old_up)
                    if client_db_traffic["Down"] > old_down:
                        delta_down += (client_db_traffic["Down"] - old_down)

            new_up_for_group = max_up_db + delta_up
            new_down_for_group = max_down_db + delta_down

            if new_up_for_group != max_up_db or new_down_for_group != max_down_db:
                for client_db_traffic in matching_traffics_db:
                    client_db_traffic["Total"] = max_total_db
                    client_db_traffic["Up"] = new_up_for_group
                    client_db_traffic["Down"] = new_down_for_group
                    client_db_traffic["Expiry_Time"] = expiry_time
                    final_client_traffic_records_to_update.append(client_db_traffic)

                for client_inbound_setting in clients_in_group:
                    client_inbound_setting["totalGB"] = max_total_db # This assumes totalGB in inbound settings maps to total from client_traffics
                    client_inbound_setting["expiryTime"] = expiry_time
                    client_inbound_setting["up"] = new_up_for_group
                    client_inbound_setting["down"] = new_down_for_group
                    final_clients_to_update.append(client_inbound_setting)
                
                print(f"Syncing subId={subid} | UP={new_up_for_group} DOWN={new_down_for_group}")

        if final_client_traffic_records_to_update:
            update_client_traffics_in_db(conn, final_client_traffic_records_to_update)

        updated_inbounds_for_db = []
        final_clients_map = {c["email"]: c for c in final_clients_to_update}

        for inbound_id, inbound_obj in inbounds_dict.items():
            if inbound_obj["protocol"] in ["vmess", "vless"]:
                current_settings_str = inbound_obj.get("settings")
                if current_settings_str:
                    try:
                        current_settings = json.loads(current_settings_str)
                        current_clients_in_settings = current_settings.get("clients", [])
                        
                        new_clients_list_for_inbound = []
                        
                        for updated_client in final_clients_map.values():
                            if updated_client.get("inbound_id") == inbound_id:
                                new_clients_list_for_inbound.append(updated_client)
                        
                        existing_emails_in_updated_list = {c["email"] for c in new_clients_list_for_inbound}
                        for c_old in current_clients_in_settings:
                            if c_old.get("email") not in existing_emails_in_updated_list:
                                new_clients_list_for_inbound.append(c_old)
                        
                        if json.dumps(current_settings.get("clients", [])) != json.dumps(new_clients_list_for_inbound):
                            current_settings["clients"] = new_clients_list_for_inbound
                            inbound_obj["settings"] = json.dumps(current_settings)
                            updated_inbounds_for_db.append(inbound_obj)
                            changes_made_to_inbounds = True
                            print(f"Inbound {inbound_id} needs database update.")

                    except json.JSONDecodeError as e:
                        print(f"JSON decode error when rebuilding Inbound {inbound_id} settings: {e}")
                
        if updated_inbounds_for_db:
            update_inbounds_in_db(conn, updated_inbounds_for_db)

        save_local_usage({"sec": get_sleep_interval(), "clients": db_client_traffics})
        
        print("Done processing data.")

        if changes_made_to_inbounds:
            restart_xui_service()
        else:
            print("No inbound setting changes. No need to restart x-ui service.")

    except Exception as e:
        print(f"Error in process_and_sync_data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

def main():
    """Main function to run the sync cycle continuously."""
    print("Starting continuous X-UI SubId Traffic Sync (direct DB access)...")
    while True:
        try:
            print("\n--- Starting sync cycle ---")
            process_and_sync_data()
            sleep_duration = get_sleep_interval()
            print(f"Sync cycle finished. Waiting for {sleep_duration} seconds...")
            time.sleep(sleep_duration)
        except Exception as e:
            print(f"General error in main: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(10)

if __name__ == '__main__':
    main()
