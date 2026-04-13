import subprocess

from gi.repository import Gio


class BatteryManager:
    current_level = 69
    current_status = "Discharging"

    def __init__(self, parent) -> None:

        self.parent = parent
        self.proxy = Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SYSTEM,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.freedesktop.UPower",
            "/org/freedesktop/UPower/devices/DisplayDevice",
            "org.freedesktop.UPower.Device",
            None,
        )
        self.proxy.connect("g-properties-changed", self.on_battery_changed)

        self.update_data()

    def update_data(self):
        percent_variant = self.proxy.get_cached_property("Percentage")
        state_variant = self.proxy.get_cached_property("State")

        if percent_variant:
            BatteryManager.current_level = int(percent_variant.unpack())

        if state_variant:
            state = state_variant.unpack()
            # 1: Charging, 2: Discharging, 4: Full
            if state == 1:
                BatteryManager.current_status = "Charging"
            elif state == 4:
                BatteryManager.current_status = "Full"
            else:
                BatteryManager.current_status = "Discharging"

    def on_battery_changed(self, proxy, changed_properties, invalidated_properties):
        self.update_data()
        self.parent.update_battery_info()
        return True


class KeepAwake:
    def __init__(self) -> None:
        self.is_active = bool(subprocess.run(["pgrep", "swayidle"]).returncode)

    def toggle(self):
        try:
            if self.is_active:
                _ = subprocess.Popen(
                    ["swayidle"], stdout=subprocess.DEVNULL, start_new_session=True
                )
                self.is_active = False
                return "inactive"
            else:
                _ = subprocess.run(["pkill", "swayidle"])
                self.is_active = True
                return "active"

        except Exception as e:
            print(e)
            return False
