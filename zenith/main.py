import os
import subprocess
from ctypes import CDLL
from datetime import datetime
from optparse import Option

import gi

try:
    CDLL("libgtk4-layer-shell.so")
except OSError:
    print("Error: libgtk4-layer-shell.so not found. Ensure it is installed.")

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
gi.require_version("UPowerGlib", "1.0")

# Custom imports
from audio_manager import AudioManager
from battery_manager import BatteryManager, KeepAwake
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Pango
from gi.repository import Gtk4LayerShell as LayerShell
from power_options import PowerOptions
from workspaces import NiriManager, WorkspaceArea


class BottomSlider(Gtk.Revealer):
    def __init__(self, icon, title, items, calls) -> None:
        super().__init__()
        self.main_layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.main_layout.set_hexpand(True)
        self.main_layout.set_vexpand(True)
        self.main_layout.set_margin_top(10)
        self.main_layout.set_margin_bottom(10)

        self.main_layout.add_css_class("dropdown_bg")

        self.title_icon = Gtk.Image.new_from_icon_name(icon)
        self.title_icon.set_size_request(40, 40)
        self.title_icon.set_margin_start(10)
        self.title_icon.set_margin_top(10)

        self.title_icon.set_halign(Gtk.Align.CENTER)
        self.title_icon.add_css_class("dropdown_icon")
        self.title_label = Gtk.Label(label=title)
        self.title_label.add_css_class("dropdown_label")
        self.title_label.set_halign(Gtk.Align.FILL)
        self.title_label.set_margin_top(10)
        self.title_label.set_margin_start(20)

        self.top_layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.top_layout.append(self.title_icon)
        self.top_layout.append(self.title_label)

        self.main_layout.append(self.top_layout)

        self.buttons = []
        for i, item in enumerate(items):
            button = Gtk.Button()
            button_label = Gtk.Label(label=item)
            button_label.set_halign(Gtk.Align.START)
            button.set_child(button_label)
            button.connect("clicked", lambda x, _i=i: calls[_i]())
            button.set_margin_start(10)
            button.set_margin_end(10)
            self.buttons.append(button)
            button.add_css_class("slider_item")

            self.main_layout.append(button)

        self.buttons[0].set_margin_top(10)
        self.buttons[0].add_css_class("slider_item_top")
        self.buttons[-1].set_margin_bottom(15)
        self.buttons[-1].add_css_class("slider_item_bottom")

        self.set_child(self.main_layout)


class AudioDeviceSelection(BottomSlider):
    def __init__(self, audio_manager) -> None:
        self.items = ["Something", "Went", "Wrong"]
        calls = [
            self.nothing,
            self.nothing,
            self.nothing,
            self.nothing,
        ]
        self.audio_manager = audio_manager
        super().__init__(
            "audio-volume-high-symbolic", "Sound Output", self.items, calls
        )

    def nothing(self):
        print("GOT INFO!!")

    def change_source(self, device):
        # Edge case when user opens -> disconnects and tries to switch source
        try:
            AudioManager.switch_to_source(device)
        except:
            pass

    def update_devices(self):
        new_devices = self.audio_manager.update_source()
        for button in self.buttons:
            self.main_layout.remove(button)
        self.buttons = []
        for device in new_devices:
            if "Monitor of" not in device.description:
                b = Gtk.Button()
                b_label = Gtk.Label(label=device.description)
                b_label.set_halign(Gtk.Align.START)
                b.set_child(b_label)
                b.connect(
                    "clicked",
                    lambda x, d=device: self.change_source(d),
                )
                b.set_margin_start(10)
                b.set_margin_end(10)
                b.add_css_class("slider_item")
                self.buttons.append(b)
                self.main_layout.append(b)

        self.buttons[0].set_margin_top(10)
        self.buttons[0].add_css_class("slider_item_top")
        self.buttons[-1].set_margin_bottom(15)
        self.buttons[-1].add_css_class("slider_item_bottom")

        # Atleast for me, there is also a "Monitor for ..."
        if len(new_devices) > 2:
            return True
        return False


class OptionPill(Gtk.Box):
    def __init__(
        self, title, description, icon, bottom_slider, parent, manager
    ) -> None:
        super().__init__()
        self.set_hexpand(True)

        self.parent = parent
        self.manager = manager

        self.set_margin_top(5)
        self.set_margin_bottom(5)

        self.left_button = Gtk.Button()
        self.left_button.add_css_class("option_pill_left")
        self.left_button.add_css_class("button")
        self.left_button.set_size_request(-1, 50)
        self.left_button.set_hexpand(True)
        self.left_button.connect("clicked", lambda x: self.pressed())

        self.left_layout = Gtk.Box()

        self.text_layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.text_layout.set_hexpand(True)
        self.text_layout.set_margin_start(10)
        self.text_layout.set_margin_top(4)

        self.icon = Gtk.Image.new_from_icon_name(icon)
        self.icon.set_margin_start(4)
        self.icon.add_css_class("icon_size_l")

        self.title_label = Gtk.Label(label=title)
        self.title_label.set_max_width_chars(1)
        self.title_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.title_label.set_xalign(0.0)

        self.description = Gtk.Label(label=description)
        self.description.set_max_width_chars(1)
        self.description.set_ellipsize(Pango.EllipsizeMode.END)
        self.description.set_xalign(0.0)
        self.description.add_css_class("option_pill_description")

        self.text_layout.append(self.title_label)
        self.text_layout.append(self.description)

        self.left_layout.append(self.icon)
        self.left_layout.append(self.text_layout)

        self.left_button.set_child(self.left_layout)

        self.append(self.left_button)
        self.bottom_slider = None

        if bottom_slider:
            self.bottom_slider = bottom_slider

            self.right_button = Gtk.Button.new_from_icon_name("pan-end-symbolic")
            self.right_button.connect("clicked", lambda x: self.callback())
            self.right_button.add_css_class("option_pill_right")
            self.right_button.add_css_class("icon_size")

            self.append(self.right_button)

        else:
            self.left_button.add_css_class("option_pill_both")

        if manager and manager.is_active:
            self.left_button.add_css_class("option_pill_active")

    def callback(self):
        is_visible = self.bottom_slider.get_reveal_child()
        self.parent.reset_dropdowns()
        self.bottom_slider.set_reveal_child(not is_visible)

    def pressed(self):
        if self.manager:
            self.left_button.add_css_class("option_pill_waiting")
            result = self.manager.toggle()
            GLib.timeout_add_seconds(
                2, self.left_button.remove_css_class, "option_pill_waiting"
            )
            if result == "active":
                self.left_button.add_css_class("option_pill_active")
                self.left_button.remove_css_class("option_pill_waiting")

            elif result == "inactive":
                self.left_button.remove_css_class("option_pill_active")
                self.left_button.remove_css_class("option_pill_waiting")


class QuickSettings(Gtk.Window):
    def __init__(self, audio_manager) -> None:
        super().__init__()
        self.set_can_focus(True)
        self.add_css_class("right_popover_layout")

        self.audio_manager = audio_manager

        self._is_visible = False
        self._hide_timeout_id = None

        self.set_decorated(False)
        self.set_titlebar(None)

        LayerShell.init_for_window(self)
        LayerShell.set_layer(self, LayerShell.Layer.TOP)
        LayerShell.set_anchor(self, LayerShell.Edge.TOP, True)
        LayerShell.set_anchor(self, LayerShell.Edge.RIGHT, True)

        LayerShell.set_margin(self, LayerShell.Edge.TOP, 5)
        LayerShell.set_margin(self, LayerShell.Edge.RIGHT, 5)
        LayerShell.set_keyboard_mode(self, LayerShell.KeyboardMode.ON_DEMAND)
        LayerShell.set_namespace(self, "gtk-bar-popup")

        hover_checker = Gtk.EventControllerMotion()
        key_checker = Gtk.EventControllerKey()
        hover_checker.connect("leave", self._on_leave)
        hover_checker.connect("enter", self._on_enter)
        key_checker.connect("key-pressed", self._on_key_pressed)
        self.add_controller(hover_checker)
        self.add_controller(key_checker)

        self.set_margin_top(0)
        self.set_margin_bottom(0)

        # The main layout
        self.layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.layout.add_css_class("right_popover_box")
        self.layout.set_size_request(400, 1)
        self.layout.set_margin_top(10)
        self.layout.set_margin_start(10)
        self.layout.set_margin_end(10)
        self.layout.set_margin_bottom(5)

        # The bar of circled icons
        self.top_part = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.top_part.set_hexpand(True)

        self.init_battery_pill()

        self.screenshot_button = Gtk.Button.new_from_icon_name(
            "applets-screenshooter-symbolic"
        )
        self.screenshot_button.connect("clicked", lambda x: self.take_screenshot())
        self.button_3 = Gtk.Button.new_from_icon_name("system-lock-screen-symbolic")
        self.power_options = Gtk.Button.new_from_icon_name("system-shutdown-symbolic")
        self.power_options.connect("clicked", lambda x: self.toggle_power_expander())

        for btn in [
            self.screenshot_button,
            self.button_3,
            self.power_options,
        ]:
            btn.set_size_request(40, 40)
            btn.add_css_class("rounded_button")
            btn.add_css_class("popup_top_button")

        # Adding all the buttons to the layout
        self.top_part.append(self.screenshot_button)
        self.top_part.append(self.button_3)
        self.top_part.append(self.power_options)

        self.layout.append(self.top_part)

        self.init_power_expander()

        # Volume thingy
        self.init_volume_slider()
        self.init_brightness_slider()
        self.init_options_layout()

        self.wrapper = Gtk.Revealer()
        self.wrapper.set_child(self.layout)
        self.set_child(self.wrapper)

    def init_power_expander(self):
        icon = "system-shutdown-symbolic"
        title = "Power Options"
        items = ["Power Off", "Restart", "Lock Screen", "Log Out"]
        callbacks = [
            PowerOptions.shutdown,
            PowerOptions.reboot,
            PowerOptions.lock,
            PowerOptions.log_out,
        ]
        self.power_container = BottomSlider(icon, title, items, callbacks)
        self.layout.append(self.power_container)

    def init_battery_pill(self):
        # The battery icon
        self.battery_pill = Gtk.Button()
        self.battery_pill.set_size_request(90, 40)
        self.battery_pill.add_css_class("battery_pill")
        self.battery_pill.set_halign(Gtk.Align.START)
        self.battery_box = Gtk.Box()

        self.battery_box.set_margin_start(6)
        self.battery_box.set_margin_end(6)
        self.battery_box.add_css_class("battery_box")
        self.battery_box.set_hexpand(True)

        self.battery_pill.set_child(self.battery_box)
        self.battery_icon = Gtk.Image.new_from_icon_name("battery-level-100-symbolic")
        self.battery_icon.add_css_class("battery_icon")

        self.battery_text = Gtk.Label(label="-1%")
        self.battery_text.add_css_class("battery_text")
        self.battery_text.set_hexpand(True)
        self.battery_text.set_halign(Gtk.Align.END)

        self.battery_box.append(self.battery_icon)
        self.battery_box.append(self.battery_text)

        self.top_part.append(self.battery_pill)

    def init_volume_slider(self):
        self._prev_device = None
        self.volume_slider_layout = Gtk.Box()
        self.volume_slider_layout.set_hexpand(True)
        self.volume_slider_layout.set_margin_top(20)

        self.mute_button = Gtk.Button()
        self.mute_icon = Gtk.Image.new_from_icon_name("audio-speakers-symbolic")
        self.mute_button.set_child(self.mute_icon)
        self.mute_button.add_css_class("rounded_button")
        self.mute_button.add_css_class("transparent_button")

        self.audio_dropdown_button = Gtk.Button.new_from_icon_name("pan-end-symbolic")
        self.audio_dropdown_button.connect(
            "clicked", lambda x: self.toggle_audio_dropdown()
        )
        self.audio_dropdown_button.add_css_class("rounded_button")
        self.audio_dropdown_button.add_css_class("transparent_button")

        self.audio_device_dropdown = AudioDeviceSelection(self.audio_manager)

        self.volume_vertical_layiout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        adjustment = Gtk.Adjustment(
            value=0,
            lower=0,
            upper=100,
            step_increment=1,
            page_increment=10,
            page_size=0,
        )
        self.audio_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment
        )

        self.audio_scale.set_hexpand(True)
        self.volume_slider_layout.append(self.mute_button)
        self.volume_slider_layout.append(self.audio_scale)
        self.volume_slider_layout.append(self.audio_dropdown_button)

        self.volume_vertical_layiout.append(self.volume_slider_layout)
        self.volume_vertical_layiout.append(self.audio_device_dropdown)
        self.audio_scale.connect("value-changed", lambda x: self.update_audio_scale(x))

        self.mute_button.connect("clicked", lambda x: self.toggle_mute())
        self.layout.append(self.volume_vertical_layiout)

    def init_brightness_slider(self):
        self.brightness_slider_layout = Gtk.Box()
        self.brightness_slider_layout.set_hexpand(True)
        self.brightness_slider_layout.set_margin_top(1)

        self.brightness_icon = Gtk.Image.new_from_icon_name(
            "display-brightness-symbolic"
        )
        self.brightness_icon.set_margin_start(8)
        self.brightness_icon.set_margin_end(10)
        self.brightness_icon.add_css_class("icon_size")

        adjustment = Gtk.Adjustment(
            value=0,
            lower=0,
            upper=100,
            step_increment=1,
            page_increment=10,
            page_size=0,
        )
        self.brightness_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment
        )
        self.brightness_scale.set_hexpand(True)
        self.brightness_scale.connect(
            "value-changed", lambda x: self.update_brightness_scale(x)
        )

        self.brightness_slider_layout.append(self.brightness_icon)
        self.brightness_slider_layout.append(self.brightness_scale)
        self.layout.append(self.brightness_slider_layout)

    def init_options_layout(self):
        self.options_layout = Gtk.Grid()
        self.options_layout.set_margin_top(10)
        self.options_layout.set_column_spacing(12)
        self.options_layout.set_row_spacing(0)

        self.options_layout.set_hexpand(True)
        self.options_layout.set_column_homogeneous(True)

        self.dropdown_for_wifi = BottomSlider(
            "network-wireless-symbolic",
            "Wifi Network",
            ["Wifi network 1", "Wifi network 2"],
            [lambda: print("Hello world"), lambda: print("Button 2")],
        )

        self.dropdown_for_bluetooth = BottomSlider(
            "bluetooth-symbolic",
            "Bluetooth Devices",
            ["Device 1", "Device 2"],
            [lambda: print("Hello world"), lambda: print("Button 2")],
        )

        button_1 = OptionPill(
            "Wifi",
            "My wifi network",
            "network-wireless-symbolic",
            self.dropdown_for_wifi,
            self,
            None,
        )
        button_1.left_button.add_css_class("option_pill_active")
        button_1.right_button.add_css_class("option_pill_active_right")
        button_2 = OptionPill(
            "Bluetooth",
            "My bluetooth Device",
            "bluetooth-symbolic",
            self.dropdown_for_bluetooth,
            self,
            None,
        )

        keep_awake_manager = KeepAwake()
        keep_awake_button = OptionPill(
            "Keep Awake",
            "Don't suspend",
            "org.gnome.Settings-accessibility-seeing-symbolic",
            None,
            self,
            keep_awake_manager,
        )

        c = 0
        r = 0
        buttons = [button_1, button_2, keep_awake_button]
        for button in buttons:
            self.options_layout.attach(button, c, r, 1, 1)
            if button.bottom_slider:
                self.options_layout.attach(
                    button.bottom_slider, 0, r + 1 if c == 0 else r + 2, 2, 1
                )

            c += 1
            if c > 1:
                c = 0
                r += 3
        # self.options_layout.attach(self.dropdown_for_wifi, c, r + 1, 2, 1)
        # self.options_layout.attach(self.dropdown_for_bluetooth, c, r + 2, 2, 1)

        self.layout.append(self.options_layout)

    def update_battery_info(self):
        if self.is_visible():
            battery_percentage = BatteryManager.current_level
            battery_status = BatteryManager.current_status

            bat_string = int(battery_percentage / 10) * 10

            if battery_status == "Charging":
                bat_total_string = f"battery-level-{bat_string}-plugged-in-symbolic"

            elif battery_status == "Full":
                bat_total_string = "battery-level-100-plugged-in-symbolic"

            else:
                bat_total_string = f"battery-level-{bat_string}-symbolic"

            self.battery_icon.set_from_icon_name(bat_total_string)
            self.battery_text.set_label(f"{battery_percentage}%")

    def toggle_power_expander(self):
        is_visible = self.power_container.get_reveal_child()
        self.reset_dropdowns()
        self.power_container.set_reveal_child(not is_visible)

    def toggle_audio_dropdown(self):
        is_visible = self.audio_device_dropdown.get_reveal_child()
        self.reset_dropdowns()
        self.audio_device_dropdown.set_reveal_child(not is_visible)

    def reset_dropdowns(self):

        i = [
            self.audio_device_dropdown,
            self.power_container,
            self.dropdown_for_wifi,
            self.dropdown_for_bluetooth,
        ]

        for x in i:
            x.set_reveal_child(False)

        self.set_default_size(-1, -1)
        self.layout.set_size_request(400, -1)
        self.queue_resize()

    def toggle_mute(self):
        self.audio_manager.toggle_mute()

    def take_screenshot(self):
        command = ["niri", "msg", "action", "screenshot"]
        self.set_visible(False)
        _ = Gio.Subprocess.new(command, Gio.SubprocessFlags.NONE)

    def update_audio_info(self, is_muted, current_device, current_volume):
        if self.get_visible():
            if is_muted:
                self.mute_icon.set_from_icon_name("audio-volume-muted-symbolic")
                self.audio_scale.set_sensitive(False)
            else:
                self.mute_icon.set_from_icon_name(f"audio-{current_device}-symbolic")
                self.audio_scale.set_sensitive(True)

            self.audio_scale.set_value(current_volume)

            if self._prev_device != current_device:
                self.update_audio_devices()
                self._prev_device = current_device

    def update_audio_scale(self, scale):
        value = scale.get_value()
        try:
            self.audio_manager.set_volume(round(value / 100, 2))
        except Exception:
            pass

    def update_audio_devices(self):
        show_selection = self.audio_device_dropdown.update_devices()
        _parent = self.audio_dropdown_button.get_parent()
        if show_selection and not _parent:
            self.volume_slider_layout.append(self.audio_dropdown_button)
        elif not show_selection and _parent:
            self.volume_slider_layout.remove(self.audio_dropdown_button)

    def update_brightness_scale(self, scale):
        value = int(scale.get_value())
        if not value:
            value = 1
        try:
            subprocess.run(["brightnessctl", "set", f"{value}%"])
        except:
            pass

    def update_brightness(self):
        brightness = subprocess.run(
            ["brightnessctl", "g"], capture_output=True, text=True
        )

        max_value = subprocess.run(
            ["brightnessctl", "m"], capture_output=True, text=True
        )

        current = int(brightness.stdout.strip())
        maximum = int(max_value.stdout.strip())

        p = current / maximum * 100

        self.brightness_scale.set_value(p)

    def reveal(self):
        self.popup()

        if self._is_visible:
            self.update_audio_info(
                self.audio_manager.is_muted,
                self.audio_manager.current_device,
                self.audio_manager.current_volume,
            )
            self.update_audio_devices()
            self.update_battery_info()
            self.update_brightness()

    def _on_leave(self, *_):
        if self._hide_timeout_id is None:
            self._hide_timeout_id = GLib.timeout_add(10000, self.hide)

    def _on_enter(self, *_):
        if self._hide_timeout_id is not None:
            GLib.source_remove(self._hide_timeout_id)
            self._hide_timeout_id = None

    def _on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.hide()
            return True
        return False

    def popup(self):
        self.reset_dropdowns()

        if not self._is_visible:
            self.present()

            self.wrapper.set_reveal_child(True)
            self._is_visible = True

        elif self._is_visible:
            self._is_visible = False
            self.hide()

    def hide(self):
        self.wrapper.set_reveal_child(False)
        self._is_visible = False
        self._hide_timeout_id = None
        self.wrapper.set_reveal_child(False)

        GLib.timeout_add(200, self._set_visible_false)
        return GLib.SOURCE_REMOVE

    def _set_visible_false(self):
        self.set_visible(False)


class BarWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.HEIGHT = 27
        self.NAMESPACE = "gtk-bar"

        LayerShell.init_for_window(self)
        LayerShell.set_layer(self, LayerShell.Layer.TOP)
        LayerShell.set_namespace(self, self.NAMESPACE)

        LayerShell.set_anchor(self, LayerShell.Edge.TOP, True)
        LayerShell.set_anchor(self, LayerShell.Edge.LEFT, True)
        LayerShell.set_anchor(self, LayerShell.Edge.RIGHT, True)
        LayerShell.set_keyboard_mode(self, LayerShell.KeyboardMode.ON_DEMAND)
        LayerShell.auto_exclusive_zone_enable(self)

        # Managers
        self.audio_manager = AudioManager(parent=self)
        self.battery_manager = BatteryManager(parent=self)

        self.quicksettings = QuickSettings(audio_manager=self.audio_manager)

        self.setup_css()

        self.PADDING = 6
        self.main_layout = Gtk.CenterBox()

        self.main_layout.set_margin_start(self.PADDING)
        self.main_layout.set_margin_end(self.PADDING)

        self.right_side = Gtk.Button.new_from_icon_name("view-more-symbolic")

        self.right_side_layout = Gtk.Box()
        self.battery_icon = Gtk.Image.new_from_icon_name(
            "battery-full-charged-symbolic"
        )
        self.battery_icon.set_margin_start(5)
        self.battery_icon.add_css_class("right_icon")
        self.audio_icon = Gtk.Image.new_from_icon_name("audio-volume-high-symbolic")
        self.audio_icon.add_css_class("right_icon")

        self.right_side_layout.append(self.audio_icon)
        self.right_side_layout.append(self.battery_icon)
        self.right_side.set_child(self.right_side_layout)
        # self.quicksettings.set_parent(self.right_side)
        self.quicksettings.audio_manager = self.audio_manager

        self.niri_manager = NiriManager(parent=self)
        self.workspace_area = Gtk.Box()
        self.workspace_area.add_css_class("workspace_area")
        self.workspace_area.set_size_request(-1, 5)

        self.workspace_pills = WorkspaceArea()
        self.workspace_area.append(self.workspace_pills)

        self.center_layout = Gtk.Box()
        self.center = Gtk.Label()
        self.center.add_css_class("date_time_label")

        self.custom_timer = Gtk.Label()
        self.custom_timer.add_css_class("date_time_label")
        self.custom_timer.set_margin_start(20)

        self.center_layout.append(self.center)
        self.center_layout.append(self.custom_timer)

        self.right_side.set_cursor(Gdk.Cursor.new_from_name("pointer", None))
        self.right_side.connect("clicked", lambda x: self.quicksettings.reveal())
        self.right_side.add_css_class("power_button")
        self.right_side.add_css_class("button")

        self.main_layout.set_start_widget(self.workspace_area)
        self.main_layout.set_center_widget(self.center_layout)
        self.main_layout.set_end_widget(self.right_side)

        self.update_time()
        self.update_battery_info()
        # In milliseconds
        GLib.timeout_add(1000, self.update_time)

        self.set_default_size(-1, self.HEIGHT)
        self.set_child(self.main_layout)

    def setup_css(self):
        css_path = os.path.join(os.path.dirname(__file__), "style.css")
        if os.path.exists(css_path):
            provider = Gtk.CssProvider()
            provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

    def update_time(self):
        n_ = datetime.now()
        now = n_.astimezone()
        month = now.strftime("%b")
        day = str(now.day)
        hour = str(int(now.strftime("%I")))
        minute = now.strftime("%M")
        ampm = now.strftime("%p").upper()
        self.center.set_label(f"{month} {day}    {hour}:{minute} {ampm}")

        current_time = n_.timestamp()
        t_ = self.read_time()

        if t_:
            prefix = ""
            remaining = min(int(t_ - current_time + 182), 180)

            if remaining < 0:
                prefix = "-"
                remaining = -remaining

            m_ = remaining // 60
            s_ = int(remaining % 60)
            self.custom_timer.set_label(prefix + f"{m_} : {s_:02}")
        else:
            self.custom_timer.set_label("")

        return True

    def read_time(self):
        try:
            with open("/tmp/timer_time", "r") as f:
                return int(float(f.read()))
        except FileNotFoundError:
            return False

    def update_audio_info(self, is_muted, current_device, current_volume):
        self.quicksettings.update_audio_info(is_muted, current_device, current_volume)

        if current_volume <= 33:
            self.audio_icon.set_from_icon_name("audio-volume-low-symbolic")
        elif current_volume <= 66:
            self.audio_icon.set_from_icon_name("audio-volume-medium-symbolic")
        elif current_volume <= 100:
            self.audio_icon.set_from_icon_name("audio-volume-high-symbolic")
        else:
            self.audio_icon.set_from_icon_name("audio-volume-overamplified-symbolic")

        if is_muted:
            self.audio_icon.set_from_icon_name("audio-volume-muted-symbolic")

    def update_battery_info(self):
        self.quicksettings.update_battery_info()

        battery_percentage = BatteryManager.current_level
        battery_status = BatteryManager.current_status

        bat_string = int(battery_percentage / 10) * 10

        if battery_status == "Charging":
            bat_total_string = f"battery-level-{bat_string}-plugged-in-symbolic"

        elif battery_status == "Full":
            bat_total_string = "battery-level-100-plugged-in-symbolic"

        else:
            bat_total_string = f"battery-level-{bat_string}-symbolic"

        self.battery_icon.set_from_icon_name(bat_total_string)

    def update_workspace(self, idx, ws_list):
        self.workspace_pills.update(idx, ws_list)

    def change_overview(self, overview_state, active_workspace):
        if overview_state:
            self.workspace_area.add_css_class("is-open")
            if active_workspace == 1:
                self.add_css_class("is-transparent")
                self.remove_css_class("is-opaque")
            else:
                self.add_css_class("is-opaque")
                self.remove_css_class("is-transparent")

        else:
            self.workspace_area.remove_css_class("is-open")

            self.remove_css_class("is-transparent")
            self.remove_css_class("is-opaque")


class MyApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.python.gtk-bar")

    def do_activate(self):
        win = BarWindow(application=self)
        win.present()


if __name__ == "__main__":
    app = MyApp()
    app.run(None)
