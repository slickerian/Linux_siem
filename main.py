# main.py
import os
import time
import threading
import subprocess
from core import usb_monitor, file_watcher, command_monitor, policy_engine, tamper_protection, response_actions
from core.logger import EncryptedLogger
from utils.fingerprint import generate_device_fingerprint
from utils.system_info import collect_all_system_info as collect_system_info
from utils.colors import color_text, RED, GREEN, YELLOW, CYAN, MAGENTA, BLUE
from utils.auth import verify_admin_password

SERVICE_NAME = "insiderwatch"
PYTHON_PATH = "/usr/bin/python3"
SCRIPT_PATH = os.path.abspath("/root/InsiderWatch/main.py")
SHUTDOWN_FLAG = "/tmp/insider_shutdown.flag"

def ensure_systemd_service():
    """Automatically creates and enables the systemd service if not already set up."""
    service_file = f"/etc/systemd/system/{SERVICE_NAME}.service"

    if not os.path.exists(service_file):
        print(color_text(f"[*] Setting up {SERVICE_NAME} as a systemd service...", YELLOW))
        service_content = f"""[Unit]
Description=InsiderWatch Agent
After=network.target

[Service]
ExecStart={PYTHON_PATH} {SCRIPT_PATH}
Restart=always
RestartSec=3
User=root
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"""
        try:
            with open("/tmp/insiderwatch.service", "w") as f:
                f.write(service_content)
            subprocess.run(["mv", "/tmp/insiderwatch.service", service_file], check=True)
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            subprocess.run(["systemctl", "enable", SERVICE_NAME], check=True)
            print(color_text(f"[✓] {SERVICE_NAME} service installed and enabled.", GREEN))
        except Exception as e:
            print(color_text(f"[!] Failed to create service: {e}", RED))

def start_watchdogs():
    """Start watchdogs if not running."""
    for script in ["utils/watchdog_a.py", "utils/watchdog_b.py"]:
        script_path = f"/root/InsiderWatch/{script}"
        result = subprocess.run(["pgrep", "-f", script_path], stdout=subprocess.PIPE)
        if not result.stdout.strip():
            subprocess.Popen([PYTHON_PATH, script_path])
            print(color_text(f"[*] Started {script}", GREEN))

def monitor_watchdogs():
    """Periodically ensure watchdogs are running."""
    while True:
        start_watchdogs()
        time.sleep(10)

def start_monitor(module, name, logger, color=CYAN):
    def run():
        module.start(logger)
    threading.Thread(target=run, daemon=True).start()

def main():
    ensure_systemd_service()
    start_watchdogs()

    os.makedirs("logs", exist_ok=True)
    logger = EncryptedLogger()

    # Log system fingerprint and info
    fingerprint = generate_device_fingerprint()
    system_info = collect_system_info()
    logger.log("SYSTEM_STARTUP", {"fingerprint": fingerprint, "system_info": system_info})
    with open("/tmp/insider_main.pid", "w") as f:
        f.write(str(os.getpid()))

    print(color_text("[*] InsiderWatch CLI Agent Starting...", CYAN))

    start_monitor(usb_monitor, "USB", logger)
    start_monitor(file_watcher, "File", logger)
    start_monitor(command_monitor, "Command", logger)
    start_monitor(tamper_protection, "Tamper", logger)
    threading.Thread(target=monitor_watchdogs, daemon=True).start()

    try:
        logger.log("MONITORING_STARTED", {})

        while True:
            if os.path.exists(SHUTDOWN_FLAG):
                os.remove(SHUTDOWN_FLAG)
                logger.log("SYSTEM_SHUTDOWN", {"reason": "Authorized via shutdown flag"})
                print(color_text("[✓] Shutdown flag detected. Stopping service...", GREEN))
                subprocess.run(["systemctl", "stop", SERVICE_NAME])
                break

            events = logger.get_recent_events()
            decisions = policy_engine.evaluate(events, logger)

            for event in events:
                if "POLICY_TRIGGER" in event or "ALERT" in event:
                    print(color_text(f"[ALERT] {event.strip()}", YELLOW))
                elif "ERROR" in event or "FATAL" in event:
                    print(color_text(f"[ERROR] {event.strip()}", RED))
                else:
                    print(color_text(f"[EVENT] {event.strip()}", MAGENTA))

            for action, data in decisions:
                print(color_text(f"[ACTION] Executing {action} for {data}", BLUE))
                response_actions.execute(action, data, logger)

            time.sleep(5)

    except Exception as e:
        logger.log("FATAL_ERROR", {"exception": str(e)})
        print(color_text(f"[FATAL] {str(e)}", RED))
        raise

if __name__ == "__main__":
    main()
