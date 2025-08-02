
# InsiderWatch

**InsiderWatch** is a CLI-only, air-gapped insider threat detection and response system for Linux environments. It is designed to operate entirely offline and autonomously, targeting high-security setups like laboratories, clinics, academic institutions, and classified research units.

> ⚠️ **Work In Progress**: This project is actively being developed. Expect frequent changes and improvements.

---

## 🧠 Key Features

- USB activity monitoring (forensics, fingerprinting)
- Sensitive file access tracking
- Command history and tamper detection
- Mutual watchdog system with anti-kill logic
- Encrypted local logging
- Automated response actions (lock user, disable USB, etc.)
- Policy enforcement using YAML-based configuration
- Offline-first design — no cloud dependency
- Secure admin shutdown system

---

## 📁 File Structure

```
InsiderWatch/
├── core/                    # Core logic (USB monitor, file monitor, command monitor, etc.)
├── config/                  # YAML configuration files & shutdown flag
│   └── shutdown.flag
├── logs/                    # Encrypted log files
├── utils/                   # Watchdog scripts and helper tools
│   ├── watchdog_a.py
│   └── watchdog_b.py
├── installer/               # Python virtual environment (venv)
├── main.py                  # Central management agent
├── admin_shutdown.py        # Secure shutdown script with password prompt
├── insiderwatch.service     # Systemd unit for main agent
├── watchdog_a.service       # Systemd unit for Watchdog A
└── watchdog_b.service       # Systemd unit for Watchdog B
```

---

## ⚙️ Installation & Setup

1. Clone the project and set up the Python virtual environment.
2. Place the service files inside /etc/systemd/system 
3. Enable and start the services:

```bash
sudo systemctl daemon-reexec
sudo systemctl enable insiderwatch.service watchdog_a.service watchdog_b.service
sudo systemctl start insiderwatch.service
```

3. On system boot, the systemd services will ensure:
   - `main.py` starts the system
   - Watchdogs monitor each other and `main.py`
   - Any unauthorized termination is auto-restarted

---

<!-- ## 🔐 Admin Shutdown (Under development)

The only way to shut down InsiderWatch is using:

```bash
sudo python3 admin_shutdown.py
```

This script:
- Prompts for a password
- Marks the shutdown as authorized
- Gracefully stops `main.py`, `watchdog_a.py`, and `watchdog_b.py`

All other stop attempts (`systemctl stop`, `kill`, `pkill`, etc.) will be logged and countered.

--- -->

## 🛡️ Tamper Protection

- All services restart automatically on termination
- Any script attempting to kill InsiderWatch processes without authorization will fail
- Each script monitors the others and will relaunch any that stop unexpectedly

---

## 🔒 Requirements

- Python 3.12+
- Linux (Xubuntu/Debian-based recommended)
- `systemd` for process control
- Root access for full functionality

---

## 📌 Disclaimer

This software is intended for cybersecurity research, academic use, and internal defense tooling. It is not completely built or tested. **Do not deploy on production systems without understanding the risks.**

---

## 🚧 Development Status

- [x] Core architecture implemented
- [x] Encrypted logging system
- [x] Watchdog and anti-kill system
- [ ] Admin-only shutdown protocol
- [ ] File access tagging & sensitivity classifier (planned)
- [ ] LAN dashboard (optional)
- [ ] Full documentation

---

## 🧩 License

Work in progress. License to be finalized.

---
