# storage.py

import json
import os
from datetime import datetime, timedelta

USERS_FILE = "data/users.json"
USED_IPS_FILE = "data/used_ips.json"

def load_json(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def load_users():
    return load_json(USERS_FILE)

def save_users(data):
    save_json(USERS_FILE, data)

def load_used_ips():
    return load_json(USED_IPS_FILE)

def save_used_ips(data):
    save_json(USED_IPS_FILE, data)

def generate_next_ip(ip_range, used_ips):
    base_ip = ip_range.split('/')[0]
    prefix = '.'.join(base_ip.split('.')[:-1])
    for i in range(2, 255):
        ip = f"{prefix}.{i}"
        if ip not in used_ips:
            used_ips.append(ip)
            save_used_ips(used_ips)
            return ip
    return None

def add_user(user_id, username, plan, ip, config_file, duration_hours):
    users = load_users()
    now = datetime.utcnow()
    expire = now + timedelta(hours=duration_hours)
    users[str(user_id)] = {
        "username": username,
        "plan": plan,
        "ip": ip,
        "config": config_file,
        "created": now.isoformat(),
        "expires": expire.isoformat()
    }
    save_users(users)

def get_user(user_id):
    users = load_users()
    return users.get(str(user_id))

def update_expiration(user_id, extra_hours):
    users = load_users()
    if str(user_id) in users:
        old_expire = datetime.fromisoformat(users[str(user_id)]["expires"])
        new_expire = old_expire + timedelta(hours=extra_hours)
        users[str(user_id)]["expires"] = new_expire.isoformat()
        save_users(users)
        return True
    return False

def get_expiring_users(reminder_hours):
    now = datetime.utcnow()
    users = load_users()
    result = []
    for uid, data in users.items():
        exp = datetime.fromisoformat(data["expires"])
        remaining = (exp - now).total_seconds() / 3600
        if any(int(remaining) == r for r in reminder_hours):
            result.append((uid, data))
    return result
