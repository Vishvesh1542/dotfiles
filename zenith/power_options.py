import os
import subprocess


class PowerOptions:
    @classmethod
    def shutdown(cls):
        subprocess.run(["systemctl", "poweroff"])

    @classmethod
    def reboot(cls):
        subprocess.run(["systemctl", "reboot"])

    @classmethod
    def lock(cls):
        subprocess.run(["loginctl", "lock-session"])

    @classmethod
    def log_out(cls):
        uid = str(os.getuid())
        subprocess.run(["loginctl", "terminate-user", uid])
