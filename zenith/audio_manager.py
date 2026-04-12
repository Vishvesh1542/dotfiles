import re
import subprocess
import threading

import pulsectl
from gi.repository import GLib


class AudioManager:
    _SINK_EVENTS = frozenset({"sink", "server", "card"})
    _DEBOUNCE_MS = 20

    def __init__(self, parent) -> None:
        self.parent = parent
        self.current_volume = 0
        self.current_device = "speakers"
        self.is_muted = False

        self._stop_event = threading.Event()
        self._debounce_id: int | None = None
        self._lock = threading.Lock()

        self.update_data()
        threading.Thread(target=self._monitor_events, daemon=True).start()

    def _run(self, *args: str) -> str | None:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()

    def _schedule_update(self) -> None:
        if self._debounce_id is not None:
            GLib.source_remove(self._debounce_id)
        self._debounce_id = GLib.timeout_add(self._DEBOUNCE_MS, self._debounced_update)

    def _debounced_update(self) -> bool:
        self._debounce_id = None
        self.update_data()
        return GLib.SOURCE_REMOVE

    def _detect_device(self, sink_name: str) -> str:
        info = self._run("pactl", "list", "sinks")

        item = "speakers"
        if not info or not sink_name:
            return "speakers"

        for block in info.split("\n\n"):
            if sink_name in block:
                low = block.lower()
                if any(
                    kw in low
                    for kw in (
                        "a2dp",
                        "bluez",
                        "bluetooth",
                        " bt ",
                    )
                ):
                    item = "headphones"
        return item

    def _monitor_events(self) -> None:
        while not self._stop_event.is_set():
            try:
                with pulsectl.Pulse("audio-listener") as pulse:
                    pulse.event_mask_set("sink", "card", "server", "source")

                    def callback(ev):
                        GLib.idle_add(self._schedule_update)

                    pulse.event_callback_set(callback)
                    GLib.idle_add(self._schedule_update)
                    pulse.event_listen()
            except Exception as exc:
                print(f"[AudioManager] monitor crashed: {exc}; restarting in 3 s")
                self._stop_event.wait(3)

    def update_source(self):
        with pulsectl.Pulse("audio-listener") as pulse:
            sources_list = pulse.source_list()
        return sources_list

    def update_data(self):
        raw = self._run("wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@")
        if raw is None:
            return

        m = re.fullmatch(r"Volume:\s+([\d.]+)(\s+\[MUTED\])?", raw)
        if not m:
            print(f"[AudioManager] unexpected wpctl output: {raw!r}")
            return

        with self._lock:
            self.current_volume = min(int(round(float(m.group(1)) * 100)), 150)
            self.is_muted = m.group(2) is not None

            sink_name = self._run("pactl", "get-default-sink") or ""
            self.current_device = self._detect_device(sink_name)

            GLib.idle_add(
                self.parent.update_audio_info,
                self.is_muted,
                self.current_device,
                self.current_volume,
            )

    def toggle_mute(self) -> None:
        if self._run("wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle") is not None:
            with self._lock:
                self.is_muted = not self.is_muted
            GLib.idle_add(
                self.parent.update_audio_info,
                self.is_muted,
                self.current_device,
                self.current_volume,
            )

    def set_volume(self, value: float | int) -> None:
        if isinstance(value, int) or value > 1.5:
            value = value / 100.0
        value = max(0.0, min(1.5, value))
        self._run("wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{value:.2f}")

    @classmethod
    def switch_to_source(cls, device):
        with pulsectl.Pulse("audio-listener") as pulse:
            for sink in pulse.sink_list():
                # For some reason, the device name doesnt match ever
                if sink.description == device.description:
                    pulse.default_set(sink)
                    return
