
import os
import json
import time
import requests
from datetime import datetime

# === Telegram Config ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("MONIQUE_CHAT_ID", "")

UPLOAD_DIR = "uploads"
AUDIT_LOG = "vaultkeeper_audit_log.jsonl"
os.makedirs(UPLOAD_DIR, exist_ok=True)

AGENT_KEYS = {
    "vaultkeeper": ["NAMECHEAP_API_KEY", "NAMECHEAP_USERNAME", "NAMECHEAP_CLIENT_IP"],
    "coordinator": ["RENDER_API_KEY"],
    "monique": ["TELEGRAM_BOT_TOKEN", "MONIQUE_CHAT_ID"],
    "finance_bot": ["PLAID_API_KEY"],
    "smart_contract_bot": ["ALCHEMY_API_KEY"],
    "content_bot": ["OPENAI_API_KEY"],
    "cmo_bot": ["MAILGUN_API_KEY"],
    "sentinel": ["IPINFO_API_KEY", "SENTRY_API_KEY"]
}

def notify_monique(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing Telegram config.")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    except Exception as e:
        print("Telegram alert failed:", e)

def audit_env_keys():
    report = []
    for agent, keys in AGENT_KEYS.items():
        missing = [k for k in keys if not os.getenv(k)]
        if missing:
            report.append(f"❌ {agent} missing: {', '.join(missing)}")
        else:
            report.append(f"✅ {agent} has all required keys.")
    return report

def audit_uploaded_files():
    file_report = []
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            path = os.path.join(UPLOAD_DIR, f)
            if os.path.isfile(path):
                file_report.append({
                    "file": f,
                    "size_kb": round(os.path.getsize(path) / 1024, 2),
                    "last_modified": datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
                })
    return file_report

def run_full_audit():
    env_status = audit_env_keys()
    files_status = audit_uploaded_files()
    recommendations = []

    if not files_status:
        recommendations.append("⚠️ No agent files found in uploads/.")
    if any("❌" in line for line in env_status):
        recommendations.append("⚠️ Some agents are missing environment keys.")

    full_report = {
        "timestamp": datetime.utcnow().isoformat(),
        "env_check": env_status,
        "files_check": files_status,
        "recommendations": recommendations
    }

    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(full_report) + "\n")

    message = "📦 System Audit Summary:\n"
    message += "\n".join(env_status)
    if recommendations:
        message += "\n\n⚠️ Recommendations:\n" + "\n".join(recommendations)
    else:
        message += "\n\n✅ All systems appear operational."

    notify_monique(message)
    print(json.dumps(full_report, indent=2))

if __name__ == "__main__":
    run_full_audit()
